import sys
import os
from types import coroutine
from unittest.util import _MAX_LENGTH
import pandas as pd
import pyarrow as pa
import argparse
import glob
#import requests_async as requests
import asyncio
from aiohttp import ClientSession
from typing import IO
import aiofiles
import re
from colorama import Fore, Style
from PIL import Image
import io

# can tweak these you feel like it, but shouldn't be needed
unsafe_threshhold = 0.1 # higher values is more likely to be nsfw and will be skipped
aesthetic_threshhold = 5 # higher is more aesthetic, note laion2B-aesthetic already >7?
http_timeout = 10 

# dont touch
downloaded_count = 0
current_parquet_file_downloaded_count = 0
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
    parser.add_argument(
        "--parquet_skip",
        type=int,
        nargs="?",
        const=True,
        default=0,
        help="skips the first n parquet files on disk, useful to resume",
    )

    return parser

def cleanup_text(file_name: str):
    # TODO: can be improved
    file_name = re.sub(r'[^\x00-\x7F]+', '', file_name) # remove non-ascii
    file_name = re.sub("<div.*<\/div>", "", file_name)
    file_name = re.sub("<span.*<\/span>", "", file_name)
    file_name = file_name.split("/")[-1]

    # remove forward slash from file_name
    file_name = file_name.replace("/", "").replace('&', 'and') 

    file_name = file_name.replace('\t', '').replace('\n', '').replace('\r', '')

    file_name = file_name.replace('"', '').replace('\'', '').replace('?', '').replace(':','').replace('|','') \
        .replace('<', '').replace('>', '').replace('/', '').replace('\\', '').replace('*', '') \
        .replace('!', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '') \
        .replace('^', '').replace('(', '').replace(')', '').replace('_', ' ') \
        .replace('\t', '').replace('\n', '').replace('\r', '')

    _MAX_LENGTH = 240
    if (len(file_name) > _MAX_LENGTH):
        file_name = file_name[:_MAX_LENGTH]
    
    return file_name
    
async def dummyToConsole_dict(dict):
    #print("{" + f"\"{dict[0]}\": \"{dict[1]}\"" +"},")
    print(dict[1])

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

async def call_http(image_url: str, out_file_name: str, session: ClientSession):
    #print(f"calling http and save to: {out_file_name}")
    global downloaded_count
    global http_timeout
    global current_parquet_file_downloaded_count
    try:
        if os.path.exists(out_file_name):
            print(f"{Fore.YELLOW}   already exists: {Fore.LIGHTWHITE_EX}{out_file_name}{Fore.YELLOW}, skipping{Style.RESET_ALL}")
            return

        #print(f"    attempting to download to: {out_file_name}")
        res = await session.request(method="GET", url=image_url, timeout=http_timeout)
        
        if (res.status == 200):            
            return await res.content.read()
        else:
            print(f"{Fore.YELLOW}Failed to download image, HTTP response code: {res.status} for {Fore.LIGHTWHITE_EX}{image_url}{Style.RESET_ALL}")
            downloaded_count -= 1
    except Exception as e:
        print(f"{Fore.YELLOW} *** Error downloading image: {Fore.LIGHTWHITE_EX}{image_url}{Fore.YELLOW}, ex: {str(e)}{Style.RESET_ALL}")
        downloaded_count -= 1
        pass
    return None


async def save_img(image: Image, text: str, out_dir: str):
    try:
        buffer = io.BytesIO(image)
        image = Image.open(buffer)
        format = image.format.lower()

        if (format == "jpeg"):
            format = "jpg"

        out_file_name = f"{out_dir}{text}.{format}"

        async with aiofiles.open(out_file_name, "wb") as f:
            await f.write(buffer.getbuffer())
    
    except Exception as e:
        print(f"{Fore.YELLOW} *** Possible corrupt image for text: {Fore.LIGHTWHITE_EX}{text}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} ***   ex: {Fore.LIGHTWHITE_EX}{str(e)}{Style.RESET_ALL}")
        pass
        #del image
        #del img_bytes

async def download_image(image_url: str, text: str, outpath: IO, session: ClientSession):
    if outpath[-1] != "/":
        outpath += "/"

    text = cleanup_text(text)
    file_extension = get_file_extension(image_url)
    out_file_name = f"{outpath}{text}.{file_extension}"

    #await dummyToConsole_dict(tuple([image_url, out_file_name]))
    img = await call_http(image_url, out_file_name, session)

    if img is not None: 
        global downloaded_count
        downloaded_count += 1
        await save_img(img, text, outpath)

async def download_set_dict(opt, matches_dict: dict):
    async with ClientSession() as session:
        current_parquet_file_downloaded_count = 0
        tasks = []
        for row in matches_dict:
            if downloaded_count < opt.limit:
                current_parquet_file_downloaded_count += 1
                tasks.append(
                    download_image(image_url=row["URL"], text=row["TEXT"], outpath=opt.out_dir, session=session)              
                )
            else:
                print(f"{Fore.YELLOW} Limit reached: {opt.limit}, exiting...{Style.RESET_ALL}")
                break
                
        await asyncio.gather(*tasks)
    print(f"{Fore.LIGHTBLUE_EX}       Downloaded chunk of {current_parquet_file_downloaded_count} images{Style.RESET_ALL}")

def query_parquet(df: pd.DataFrame, opt):
    # TODO: efficiency, expression tree?
    matches = df

    matches = matches[(matches.HEIGHT > opt.min_hw) & \
        (matches.WIDTH > opt.min_hw) & \
        (matches.punsafe < unsafe_threshhold) & \
        (matches.aesthetic > aesthetic_threshhold)]

    if opt.search_text:
        for word in opt.search_text.split(","):
            matches = matches[matches[opt.column].str.contains(word, case=False)]

    matches = matches[~matches["URL"].str.contains("dreamstime.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("alamy.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("123rf.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("colourbox.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("envato.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("stockfresh.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("depositphotos.com", case=False)] # watermarks
    matches = matches[~matches["URL"].str.contains("istockphoto.com", case=False)] # watermarks

    return matches

async def download_laion_matches(opt):
    print(f"{Fore.LIGHTBLUE_EX}  Searching for {opt.search_text} in column: {opt.column} in {opt.laion_dir}/*.parquet{Style.RESET_ALL}")
    
    for idx, file in enumerate(glob.iglob(f"{opt.laion_dir}/*.parquet")):
        if idx < opt.parquet_skip: 
            print(f"{Fore.YELLOW} Skipping file {idx+1}/{opt.parquet_skip}: {file}{Style.RESET_ALL}")
            continue

        global downloaded_count
        global aesthetic_threshhold
        if downloaded_count < opt.limit:
            print(f"{Fore.CYAN}  reading file: {file}{Style.RESET_ALL}")

            df = pd.read_parquet(file, engine="auto")
            matches = query_parquet(df, opt)
            # print(f"{Fore.CYAN}       matches in current parquet file:{ Style.RESET_ALL}")
            # print(matches)
            
            match_dict = matches.to_dict('records') # TODO: pandas problems later in script... needs revisiting

            await download_set_dict(opt, match_dict)
        else:
            print(f"{Fore.YELLOW}limit reached before reading next parquet file. idx: {idx}, filename: {file}{Style.RESET_ALL}")
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
    
    if (isWindows()): 
        print("{Fore.CYAN}Windows detected, using asyncio.WindowsSelectorEventLoopPolicy{Style.RESET_ALL}")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        print("{Fore.CYAN}Unix detected, using default asyncio event loop policy{Style.RESET_ALL}")

    import time
    s = time.perf_counter()

    result = asyncio.run(download_laion_matches(opt))
        
    elapsed = time.perf_counter() - s
    print(f"{Fore.CYAN} **** Job Complete ****")
    print(f" search_text: \"{opt.search_text}\", force: {opt.force}")
    print(f" Total downloaded {downloaded_count} images")
    print(f"{__file__} executed in {elapsed:0.2f} seconds.{Style.RESET_ALL}{Style.RESET_ALL}")