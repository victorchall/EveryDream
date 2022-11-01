import aiofiles
import aiofiles.os
import asyncio
import sys
import os
import glob
import argparse

def get_parser(**parser_kwargs):
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--img_dir",
        type=str,
        nargs="?",
        const=True,
        default="input",
        help="directory with images to be renamed",
    ),
    parser.add_argument(
        "--find",
        type=str,
        nargs="?",
        const=True,
        default="a man,a woman,a person",
        help="what strings to replace, in csv format, default: 'a man,a woman,a person'",
    ),
    parser.add_argument(
        "--replace",
        type=str,
        nargs="?",
        required=True,
        const=True,
        default="filename",
        help="string to replace with, ex. 'john doe'",
    ),
    
    return parser

def isWindows():
    return sys.platform.startswith('win')

async def rename_files(opt):
    print("go")
    find_list = opt.find.split(",")

    dir_iter = await aiofiles.os.scandir(opt.img_dir)
    for file in dir_iter:
        # get file extension
        if file.is_file() and os.path.splitext(file.name)[1] in (".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp"):
            try:
                for s in find_list:
                    if s in file.name:
                        new_filename = file.name.replace(s, opt.replace)
                        await aiofiles.os.rename(file, os.path.join(opt.img_dir, new_filename))
            except Exception as e:
                print(f"error opening file: {file}")
                print(f"{e}")
                raise e

if __name__ == "__main__":
    parser = get_parser()
    opt = parser.parse_args()

    if (isWindows()): 
        print("{Fore.CYAN}Windows detected, using asyncio.WindowsSelectorEventLoopPolicy{Style.RESET_ALL}")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        print("{Fore.CYAN}Unix detected, using default asyncio event loop policy{Style.RESET_ALL}")
    import time

    s = time.perf_counter()
    result = asyncio.run(rename_files(opt))
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")