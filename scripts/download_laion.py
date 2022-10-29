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
import aiohttp
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
    do_not_download = True
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
    ),
    parser.add_argument(
        "--verbose",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="additional logging of URL and TEXT prefiltering",
    ),
    parser.add_argument(
        "--test",
        action='store_const',
        const=do_not_download,
        default=not(do_not_download),
        help="skips downloading, for checking filters, use with --verbose",
    )
    
    return parser

def cleanup_text(file_name: str):
    # TODO: can be improved    

    file_name = re.sub("<div.*<\/div>", "", file_name)
    file_name = re.sub("<span.*<\/span>", "", file_name)
    file_name = re.sub("<a.*<\/a>", "", file_name)
    file_name = file_name.replace('<p>', '').replace("</p>", "")
    file_name = file_name.replace('<strong>', '').replace("</strong>", "")
    file_name = file_name.replace('<em>', '').replace("</em>", "")

    file_name = re.sub(r'[^\x00-\x7F]+', '', file_name) # remove non-ascii

    file_name = file_name.replace(' & ', ' and ').replace(' &', ' and').replace('& ', 'and ') \
        .replace(" + ", " and ").replace(" +", " and").replace("+ ", "and ")

    file_name = file_name.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

    file_name = file_name.replace('\"t"', ' ')

    file_name = file_name.replace(" ♥ ","love").replace("♥ ","love ").replace(" ♥"," love") \
        .replace("♥"," love ")

    # remove bad chars
    file_name = file_name.replace('\"', '').replace('?', '') \
        .replace('<', '').replace('>', '').replace('/', '').replace('*', '') \
        .replace('!', '').replace('#', '').replace('$', '').replace('%', '') \
        .replace('^', '').replace('(', '').replace(')', '')
    
    # replace with space
    file_name = file_name.replace(':',' ').replace('|',' ').replace('@', '') \
        .replace("/", " ").replace("\\'", "\'").replace("\\", " ").replace('\\', ' ') \
        .replace('_', ' ').replace("=", " ")
    
    # replace foreign chars
    file_name = file_name.replace('é', 'e').replace('è', 'e').replace('ê', 'e') \
        .replace('ë', 'e').replace('à', 'a').replace('â', 'a').replace('ä', 'a') \
        .replace('ç', 'c').replace('ù', 'u').replace('û', 'u').replace('ü', 'u') \
        .replace('ô', 'o').replace('ö', 'o').replace('ï', 'i').replace('î', 'i') \
        .replace('í', 'i').replace('ì', 'i').replace('ñ', 'n').replace('ß', 'ss') \
        .replace('á', 'a').replace('ã', 'a').replace('å', 'a').replace('æ', 'ae') \
        .replace('œ', 'oe').replace('ø', 'o').replace('ð', 'd').replace('þ', 'th') \
        .replace('ý', 'y').replace('ÿ', 'y').replace('ž', 'z').replace('ž', 'z') \
        .replace('š', 's').replace('đ', 'd').replace('ď', 'd').replace('č', 'c') \
        .replace('ć', 'c').replace('ř', 'r').replace('ŕ', 'r').replace('ľ', 'l') \
        .replace('ĺ', 'l').replace('ť', 't').replace('ň', 'n').replace('ņ', 'n') \
        .replace('ď', 'd').replace('Ď', 'D').replace('Ť', 'T').replace('Ň', 'N')

    _MAX_LENGTH = 240
    if (len(file_name) > _MAX_LENGTH):
        file_name = file_name[:_MAX_LENGTH]
    
    return file_name
    
async def call_http(image_url: str, session: aiohttp.ClientSession):
    #print(f"calling http and save to: {out_file_name}")
    global downloaded_count
    global http_timeout
    global current_parquet_file_downloaded_count
    try:
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

async def save_img(buffer: io.BytesIO, full_outpath: str):
    try:
        async with aiofiles.open(full_outpath, "wb") as f:
            await f.write(buffer.getbuffer())
    except Exception as e:
        print(f"{Fore.RED} *** Unable to write to disk: {Fore.LIGHTWHITE_EX}{full_outpath}{Style.RESET_ALL}")
        print(f"{Fore.RED} ***   ex: {Fore.LIGHTWHITE_EX}{str(e)}{Style.RESET_ALL}")
        pass

def get_outpath_filename(data: any, full_outpath_noext: str, clean_text: str):
    ext = "jpg"
    full_outpath = None
    buffer = None
    try: 
        buffer = io.BytesIO(data)
        image = Image.open(buffer)
        ext = image.format.lower()

        if (ext == "jpeg"):
            ext = "jpg"

        full_outpath = f"{full_outpath_noext}.{ext}"
    except Exception as e:
        print(f"{Fore.YELLOW} *** Possible corrupt image for text: {Fore.LIGHTWHITE_EX}{clean_text}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} ***   ex: {Fore.LIGHTWHITE_EX}{str(e)}{Style.RESET_ALL}")
        pass
    return full_outpath, buffer

async def download_image(image_url: str, clean_text: str, full_outpath_noext: IO, session: aiohttp.ClientSession):
    http_content = await call_http(image_url=image_url, session=session)

    buffer = None

    if (http_content is not None):
        full_outpath, buffer = get_outpath_filename(data=http_content, full_outpath_noext=full_outpath_noext, clean_text=clean_text)

    if buffer is not None: 
        global downloaded_count
        downloaded_count += 1
        await save_img(buffer, full_outpath)

async def download_set_dict(opt, matches_dict: dict):
    async with aiohttp.ClientSession() as session:
        global downloaded_count
        current_parquet_file_downloaded_count = 0
        tasks = []
        for row in matches_dict:
            if downloaded_count < opt.limit:
                current_parquet_file_downloaded_count += 1
                pre_text=row["TEXT"]
                image_url=row["URL"]

                clean_text = cleanup_text(pre_text)

                full_outpath_noext = os.path.join(opt.out_dir, clean_text)

                if (opt.verbose):
                    print(f"{Fore.LIGHTGREEN_EX}***** Verbose log: ***** {Style.RESET_ALL}")
                    print(f"{Fore.LIGHTGREEN_EX}   url: {image_url}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTGREEN_EX}  text: {pre_text}{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTGREEN_EX} captn: {clean_text}{Style.RESET_ALL}")

                if any(glob.glob(full_outpath_noext + ".*")):                    
                    print(f"{Fore.YELLOW}   already exists: {Fore.LIGHTWHITE_EX}{full_outpath_noext}{Fore.YELLOW}, skipping{Style.RESET_ALL}")
                    return

                if not opt.test:
                    tasks.append(
                        download_image(image_url=image_url, clean_text=clean_text, full_outpath_noext=full_outpath_noext, session=session)              
                    )
                else:
                    current_parquet_file_downloaded_count += 1
                    downloaded_count += 1
                if len(tasks) > 63:
                    await asyncio.gather(*tasks)
                    tasks = []
            else:
                print(f"{Fore.YELLOW} Limit reached: {opt.limit}, exiting...{Style.RESET_ALL}")
                break
        if not opt.test & len(tasks) > 0:
            await asyncio.gather(*tasks)
    print(f"{Fore.LIGHTBLUE_EX}       Downloaded chunk of {current_parquet_file_downloaded_count} images{Style.RESET_ALL}")

def query_parquet(df: pd.DataFrame, opt):
    # TODO: efficiency, expression tree?
    matches = df

    matches = matches[(matches.HEIGHT > opt.min_hw) &  (matches.WIDTH > opt.min_hw)]

    if 'punsafe' in matches.columns:
        matches = matches[(matches.punsafe > unsafe_threshhold)]

    if ('aesthetic' in matches):
        matches = matches[(matches.aesthetic > aesthetic_threshhold)]

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
    
    for idx, file in enumerate(glob.iglob(os.path.join(opt.laion_dir, "*.parquet"))):
        if idx < opt.parquet_skip: 
            print(f"{Fore.YELLOW} Skipping file {idx+1}/{opt.parquet_skip}: {file}{Style.RESET_ALL}")
            continue

        global downloaded_count
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

    print(f"Test only mode: {opt.test}")

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