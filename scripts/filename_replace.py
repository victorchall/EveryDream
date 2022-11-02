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
        default=None,
        help="what strings to replace, in csv format, default: 'a man,a woman,a person'",
    ),
    parser.add_argument(
        "--replace",
        type=str,
        nargs="?",
        required=False,
        const=True,
        default=None,
        help="string to replace with, ex. 'john doe'",
    ),
    parser.add_argument(
        "--append_only",
        type=str,
        nargs="?",
        required=False,
        const=True,
        default=None,
        help="skips pronoun replace, adds a string at the end of the filename, use for 'by artist name' or 'in the style of somestyle'",
    )
    
    return parser

def isWindows():
    return sys.platform.startswith('win')

def get_replace_list(opt):
    if opt.find is None:
        return ("a man", "a woman", "a person", \
            "a girl", "a boy", \
            "a young woman", "a young man", \
            "a beautiful woman", "a handsome man", \
            "a beautiful young woman", "a handsome young man",        
        )
    else:
        return opt.find.split(",")


def rename_files(opt):
    find_list = get_replace_list(opt)

    for file in glob.glob(opt.img_dir + "/*"):
        print(file)

        if os.path.splitext(file)[1] in (".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp"):
            new_filename = file
            if opt.append_only is not None:
                new_filename = f"{os.path.splitext(file)[0]} {opt.append_only}{os.path.splitext(file)[1]}"
            else:
                for s in find_list:
                    if s in file.name:
                        new_filename = new_filename.replace(s, opt.replace)
            try:
                print(f"Renaming {file} to {new_filename}")
                os.rename(file, new_filename)
            except Exception as e:
                print(f"error opening file: {file}")
                print(f"{e}")
                raise e
            
if __name__ == "__main__":
    parser = get_parser()
    opt = parser.parse_args()
    
    import time

    s = time.perf_counter()

    rename_files(opt)

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")