#!/usr/bin/env python3

"""Compress images in a folder to a maximum megapixel size."""

import argparse
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import iglob
from multiprocessing import cpu_count
from queue import Queue

from PIL import Image, ImageFile, ImageOps

# Prevent errors from halting the script.
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.warnings.simplefilter("error", Image.DecompressionBombWarning)

VERSION = "2.0"
SHORT_DESCRIPTION = "Compress images in a directory."
SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


def get_args(**parser_kwargs):
    """Get command-line options."""
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--img_dir",
        type=str,
        default="input",
        help="path to image directory (default: 'input')",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="path to output directory (default: IMG_DIR)",
    )
    parser.add_argument(
        "--max_mp",
        type=float,
        default=1.5,
        help="maximum megapixels (default: 1.5)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="save quality (default: 95, range: 0-100, suggested: 90+)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="overwrite files in output directory",
    )
    parser.add_argument(
        "--noresize",
        action="store_true",
        default=False,
        help="do not resize, just fix orientation",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        default=False,
        help="delete original files after processing",
    )
    args = parser.parse_args()
    args.out_dir = args.out_dir or args.img_dir
    args.max_mp = args.max_mp * 1024000
    return args


def images(img_dir):
    """Return each image in the input directory."""
    for file in iglob(f"{img_dir}/*.*"):
        if file.lower().endswith(tuple(SUPPORTED_EXTENSIONS)):
            yield file


def inline(msg, newline=False):
    """Print a message on the same line."""
    msg = f"\r{msg}"
    msg += " " * (79 - len(msg))
    print(msg, end="\n" if newline else "", flush=True)


def launch_workers(queue, args):
    """Launch a pool of workers."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [loop.create_task(worker(queue, args)) for _ in range(10)]
    loop.run_until_complete(asyncio.wait(tasks))


async def open_img(path):
    """Open an image."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, Image.open, path)
    except Exception as err:
        inline(f"[!] Error Opening: {path} - {err}", True)
        return None


def oversize(img, max_mp):
    """Check if an image is larger than the maximum size."""
    return (img.width * img.height) > max_mp


async def process(image, args):
    """Process an image."""
    outfile = image.replace(args.img_dir, args.out_dir).replace(
        os.path.splitext(image)[1], ".webp"
    )
    if args.overwrite or not os.path.exists(outfile):
        img = await open_img(image)
        if img:
            newimg = transpose(img)
            if not args.noresize and oversize(newimg, args.max_mp):
                newimg = shrink(newimg, args)
            if newimg != img:
                await save_img(newimg, outfile, args)
                if args.delete and outfile != image:
                    os.remove(image)


def slow_save(path, args, img):
    """Save an image."""
    try:
        img.save(path, "webp", quality=args.quality)
        inline(f"[+] Compressed: {path}")
    except Exception as err:
        inline(f"[!] Error Saving: {path} - {err}", True)


async def save_img(img, path, args):
    """Save an image."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, slow_save, path, args, img)


def scan_path(queue, args):
    """Scan the input directory for images."""
    inline("[*] Scanning for images...", True)
    for image in images(args.img_dir):
        inline(f"[+] {image}")
        queue.put(image)


def shrink(img, args):
    """Shrink an image."""
    pixels = img.width * img.height
    ratio = args.max_mp / pixels
    try:
        return ImageOps.scale(img, ratio, Image.LANCZOS)
    except Exception as err:
        inline(f"[!] Error Shrinking: {img.filename} - {err}", True)
        return img


def start_compression(queue, args):
    """Start the compression process."""
    inline("[*] Compressing images...", True)
    inline("[-] (scanning...)")
    with ThreadPoolExecutor() as executor:
        workers = {
            executor.submit(launch_workers, queue, args): None
            for _ in range(cpu_count())
        }
        for _ in as_completed(workers):
            pass
    inline("[!] Done!", True)


def transpose(img):
    """Transpose an image."""
    try:
        return ImageOps.exif_transpose(img)
    except Exception as err:
        inline(f"[!] Error Transposing: {img.filename} - {err}", True)
        return img


async def worker(queue, args):
    """Handle images from the queue until they're gone."""
    while not queue.empty():
        image = queue.get()
        await process(image, args)


def main():
    """Run the program."""
    queue = Queue()
    args = get_args(description=SHORT_DESCRIPTION)
    inline(f"[>] Image Compression Utility v{VERSION}", True)
    scan_path(queue, args)
    start_compression(queue, args)


if __name__ == "__main__":
    main()
