import os
from tqdm import tqdm
from pathlib import Path
import argparse

def count_images(input_dir):
    folder_counts = {}
    total_images = 0
    total_folders = 0
    for root, dirs, files in os.walk(input_dir):
        image_count = sum(1 for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')))
        if image_count > 0:
            folder_counts[root] = image_count
            total_images += image_count
            total_folders += 1

    return folder_counts, total_images / total_folders if total_folders > 0 else 0

def write_multiplier(input_dir):
    folder_counts, avg_count = count_images(input_dir)
    progress_bar = tqdm(total=len(folder_counts), desc="Writing multipliers", position=0, leave=True)
    for folder, count in folder_counts.items():
        multiplier = avg_count / count if count > 0 else 0
        with open(Path(folder) / 'multiply.txt', 'w') as f:
            f.write(str(multiplier))
        progress_bar.update(1)
    progress_bar.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate image multiplication factors for subfolders")
    parser.add_argument("input_dir", metavar="input_dir", type=str, help="the input directory to calculate multipliers")
    args = parser.parse_args()

    write_multiplier(args.input_dir)
