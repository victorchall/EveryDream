import sys
import os
from types import coroutine
from unittest.util import _MAX_LENGTH
import pandas as pd
import pyarrow as pa
import argparse
import glob
import requests_async as requests
import asyncio
from aiohttp import ClientSession
from typing import IO
import aiofiles
import re
from colorama import Fore, Style

# can tweak these you feel like it, but shouldn't be needed
unsafe_threshhold = 0.1 # higher values is more likely to be nsfw and will be skipped
aesthetic_threshhold = 5 # higher is more aesthetic, note laion2B-aesthetic already >7?
http_timeout = 10 

# dont touch
downloaded_count = 0
current_parquest_file_downloaded_count = 0
logger_sp = None

def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix

def get_parser(**parser_kwargs):
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--laion_dir",
        type=str,
        nargs="?",
        const=True,
        default="./laion",
        help="directory with laion parquet files, default is ./laion",
    )
    parser.add_argument(
        "--search_text",
        type=str,
        const=True,
        nargs="?",
        default=None,
        help="csv of words with AND logic, ex \"photo,man,dog\"",
    ),
    parser.add_argument(
        "--out_dir",
        type=str,
        nargs="?",
        const=True,
        default="./output",
        help="directory to download files to, defaults is ./output",
    ),
    parser.add_argument(
        "--log_dir",
        type=str,
        nargs="?",
        const=True,
        default=None,
        help="directory for logs, if ommitted will not log, logs may be large!",
    ),
    parser.add_argument(
        "--column",
        type=str,
        nargs="?",
        const=True,
        default="TEXT",
        help="column to search for matches, defaults is 'TEXT', but you could use 'URL' if you wanted",
    ),
    parser.add_argument(
        "--limit",
        type=int,
        nargs="?",
        const=True,
        default=100,
        help="max number of matching images to download, warning: may be slightly imprecise due to concurrency and http errors, defaults is 100",
    ),
    parser.add_argument(
        "--min_hw",
        type=int,
        nargs="?",
        const=True,
        default=512,
        help="min height AND width of image to download, default is 512",
    ),
    parser.add_argument(
        "--force",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="forces a full download of all images, even if no search is provided, USE CAUTION!",
    ),

    return parser

def cleanup_filename(file_name: str):
    # TODO: can be improved
    file_name = re.sub(r'[^\x00-\x7F]+', '', file_name) # remove non-ascii
    file_name = re.sub("<div.*<\/div>", "", file_name)
    file_name = re.sub("<span.*<\/span>", "", file_name)
    file_name = file_name.split("/")[-1]
    file_name = file_name.replace('"', '').replace('\'', '').replace('?', '').replace(':','').replace('|','') \
        .replace('<', '').replace('>', '').replace('/', '').replace('\\', '').replace('*', '') \
        .replace('!', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '') \
        .replace('^', '').replace('&', '').replace('(', '').replace(')', '').replace('_', ' ')
    #    .replace('<div>', '').replace('</div>', '').replace('<span>', '').replace('</span>', '') \

    #file_name = re.sub(".*", ".", file_name)

    _MAX_LENGTH = 240
    if (len(file_name) > _MAX_LENGTH):
        file_name = file_name[:_MAX_LENGTH]
    
    return file_name
    
# async def dummyToConsole_dict(dict) -> None: 
#     print(f"iterating match: {dict['URL']}, {dict['TEXT']}")

def get_file_extension(image_url: str):
    result = "jpg"

    if '?' in image_url:
        try:
            image_url = image_url.split('?')[0]
            #print(result)
        except ValueError:
            pass

    result = image_url.split(".")[-1]

    if result in ["asp", "aspx", "ashx", "php", "jpeg"]:
       result = "jpg"

    return result

async def call_http_and_save(image_url: str, out_file_name: str, session: ClientSession):
    #print(f"calling http and save to: {out_file_name}")
    global downloaded_count
    global http_timeout
    global current_parquest_file_downloaded_count
    try:
        if os.path.exists(out_file_name):
            print(f"{Fore.YELLOW}   skipping {out_file_name} as it already exists{Style.RESET_ALL}")
            return

        #print(f"    attempting to download to: {out_file_name}")
        img_data = await session.request(method="GET", url=image_url, timeout=http_timeout)
        
        if (img_data.status == 200):            
            async with aiofiles.open(out_file_name, "wb") as f:
                data = await img_data.content.read()
                await f.write(data)
                current_parquest_file_downloaded_count += 1
        else:
            print(f"{Fore.YELLOW}Failed to download image, HTTP response code: {img_data.status} for {Fore.LIGHTWHITE_EX}{image_url}{Style.RESET_ALL}")
            downloaded_count -= 1
    except Exception as e:
        print(f"{Fore.YELLOW} *** Error downloading image: {Fore.LIGHTWHITE_EX}{image_url}{Fore.YELLOW}, skipping: {e}{Style.RESET_ALL}")
        downloaded_count -= 1
        pass

async def download_image(image_url: str, text: str, outpath: IO, session: ClientSession):
    if outpath[-1] != "/":
        outpath += "/"

    file_name = cleanup_filename(text)
    file_extension = get_file_extension(image_url)
    out_file_name = f"{outpath}{file_name}.{file_extension}"
    
    await call_http_and_save(image_url, out_file_name, session)

async def download_set_dict(opt, matches_dict: dict):
    async with ClientSession() as session:
        global downloaded_count
        current_parquest_file_downloaded_count = 0
        tasks = []
        for row in matches_dict:
            if downloaded_count < opt.limit:
                downloaded_count += 1
                current_parquest_file_downloaded_count += 1
                tasks.append(
                    download_image(image_url=row["URL"], text=row["TEXT"], outpath=opt.out_dir, session=session)              
                )
            else:
                print(f"{Fore.YELLOW} Limit reached: {opt.limit}, exiting...{Style.RESET_ALL}")
                break
                
        await asyncio.gather(*tasks)
        print(f"{Fore.LIGHTBLUE_EX}       Downloaded chunk of {current_parquest_file_downloaded_count} images{Style.RESET_ALL}")

def query_parquest(df: pd.DataFrame, opt):
    # TODO: efficiency, expression tree?
    matches = df

    matches = matches[(matches.HEIGHT > opt.min_hw) & \
        (matches.WIDTH > opt.min_hw) & \
        (matches.punsafe < unsafe_threshhold) & \
        (matches.aesthetic > aesthetic_threshhold)]

    if opt.search_text:
        for word in opt.search_text.split(","):
            matches = matches[matches[opt.column].str.contains(word, case=False)]

    return matches

async def download_laion_matches(opt):
    print(f"{Fore.LIGHTBLUE_EX}  Searching for {opt.search_text} in column: {opt.column} in {opt.laion_dir}/*.parquet{Style.RESET_ALL}")
    
    for idx, file in enumerate(glob.iglob(f"{opt.laion_dir}/*.parquet")):
        global downloaded_count
        global aesthetic_threshhold
        if downloaded_count < opt.limit:
            print(f"{Fore.CYAN}  reading file: {file}{Style.RESET_ALL}")

            df = pd.read_parquet(file, engine="auto")
            matches = query_parquest(df, opt)
            # print(f"{Fore.CYAN}       matches in current parquet file:{ Style.RESET_ALL}")
            # print(matches)
            
            match_dict = matches.to_dict('records') # TODO: pandas problems later in script... needs revisiting

            await download_set_dict(opt, match_dict)
        else:
            print(f"{Fore.YELLOW}limit reached before reading next parquest file. idx: {idx}, filename: {file}{Style.RESET_ALL}")
            break

def isWindows():
    return sys.platform.startswith('win')

def ensure_path_exists(path: str):
    if not os.path.exists(path):
        print(f"{Fore.LIGHTBLUE_EX}creating path: {path}{Style.RESET_ALL}")
        os.makedirs(path)

if __name__ == '__main__':
    print(f"{Fore.CYAN}Launching...{Style.RESET_ALL}")
    inVenv = in_virtualenv()
    print(f"is running in venv: {inVenv}")
    #assert inVenv, "Error loading venv. Please run 'source everydream-venv/bin/activate', or in windows 'everydream-venv/bin/activate.bat'"

    parser = get_parser()
    opt = parser.parse_args()

    if(opt.search_text is None and opt.force is False):
        print(f"{Fore.YELLOW}** No search terms provided, exiting...")
        print(f"** Use --force to bypass safety to dump entire DB{Style.RESET_ALL}")
        sys.exit(2)

    ensure_path_exists(opt.out_dir)

    if (opt.laion_dir[-1] != "/" or opt.laion_dir[-1] != "\\"):
        opt.laion_dir += "/"
    
    if (isWindows): 
        print("{Fore.CYAN}Windows detected, using asyncio.WindowsSelectorEventLoopPolicy{Style.RESET_ALL}")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        print("{Fore.CYAN}Unix detected, using default asyncio event loop policy{Style.RESET_ALL}")

    import time
    s = time.perf_counter()

    try:
        result = asyncio.run(download_laion_matches(opt))
    except RuntimeError as rte: # p https://bugs.python.org/issue37373
        print(f"{Fore.RED} ************** Fatal Error: **************{Style.RESET_ALL}")
        elapsed = time.perf_counter() - s
        print(f"{Fore.LIGHTBLUE_EX}{__file__} executed in {elapsed:0.2f} seconds.{Style.RESET_ALL}")
        raise rte
        
    elapsed = time.perf_counter() - s
    print(f"{Fore.CYAN} **** Job Complete ****")
    print(f" search_text: \"{opt.search_text}\", force: {opt.force}")
    print(f" Total downloaded {downloaded_count} images")
    print(f"{__file__} executed in {elapsed:0.2f} seconds.{Style.RESET_ALL}{Style.RESET_ALL}")