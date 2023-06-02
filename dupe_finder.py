import os
from PIL import Image
from tqdm import tqdm
import numpy as np
import sys
import argparse
from imagehash import average_hash, phash
from pathlib import Path

def hash_image(image_path, accurate=False):
    image = Image.open(image_path)
    image = image.convert("L").resize((8, 8), Image.ANTIALIAS)  # Convert the image to grayscale and resize it

    if accurate:
        original_hash = str(phash(image))
        flipped_hash = str(phash(image.transpose(Image.FLIP_LEFT_RIGHT)))
    else:
        original_hash = str(average_hash(image))
        flipped_hash = str(average_hash(image.transpose(Image.FLIP_LEFT_RIGHT)))
    
    return original_hash, flipped_hash

def find_duplicates(input_dir, quick=False, accurate=False):
    image_files = []
    for dirpath, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                full_path = os.path.join(dirpath, filename)
                image_files.append(full_path)

    duplicates = []
    image_hashes = {}

    print("Hashing images...")
    hashing_progress_bar = tqdm(total=len(image_files), desc="Hashing", position=0, leave=True)

    save_interval = int(len(image_files) * 0.1)  # Save progress every 10%
    if save_interval == 0:
        save_interval = 1

    hash_file_path = os.path.join(input_dir, "image_hashes.txt")

    for i, file1 in enumerate(image_files):
        original_hash, flipped_hash = hash_image(file1, accurate)
        if original_hash in image_hashes:
            duplicates.append((file1, image_hashes[original_hash]))
        elif flipped_hash in image_hashes:
            duplicates.append((file1, image_hashes[flipped_hash]))
        else:
            image_hashes[original_hash] = file1
            image_hashes[flipped_hash] = file1

        # Save progress every 10%
        if i % save_interval == 0:
            with open(hash_file_path, "w") as hash_file:
                for hash_str, file_path in image_hashes.items():
                    hash_file.write(f"{hash_str},{file_path}\n")

        hashing_progress_bar.update(1)

    hashing_progress_bar.close()

    print("Duplicates found:")
    for duplicate, original in duplicates:
        print(f"Duplicate: {duplicate}, Original: {original}")

    # Move duplicates to a new folder
    move_duplicates(duplicates, input_dir)

def move_duplicates(duplicates, input_dir):
    dupe_dir = os.path.join(input_dir, "duplicates")
    if not os.path.exists(dupe_dir):
        os.makedirs(dupe_dir)

    for dupe, original in duplicates:
        dupe_file_path = Path(dupe)
        new_file_path = os.path.join(dupe_dir, dupe_file_path.name)
        os.rename(dupe, new_file_path)

    print(f"Moved {len(duplicates)} duplicate files to {dupe_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and move duplicate images in a directory.")
    parser.add_argument("input_dir", metavar="input_dir", type=str, help="the input directory to search for duplicates")
    parser.add_argument("--quick", action="store_true", help="use quick comparison method (average hash)")
    parser.add_argument("--accurate", action="store_true", help="use accurate comparison method (perceptual hash)")
    args = parser.parse_args()

    find_duplicates(args.input_dir, args.quick, args.accurate)

