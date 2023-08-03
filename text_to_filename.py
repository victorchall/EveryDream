import os
import argparse
from pathlib import Path
from tqdm import tqdm

def rename_images(input_directory):
    # Counter initialization
    counter = 1

    for root, _, files in os.walk(input_directory):
        # Filter out image and text files
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))]
        text_files = [f for f in files if f.lower().endswith('.txt')]

        # Create a dictionary with the base names of the files as keys and the file names as values
        base_names = {}
        for f in image_files + text_files:
            base_name = os.path.splitext(f)[0]
            if base_name not in base_names:
                base_names[base_name] = []
            base_names[base_name].append(f)

        # Rename image files with the contents of the corresponding text files and add a counter to avoid duplicate file names
        for base_name, file_names in tqdm(base_names.items(), desc="Renaming images", unit="image"):
            if len(file_names) == 2:
                image_file = [f for f in file_names if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'))][0]
                text_file = [f for f in file_names if f.lower().endswith('.txt')][0]

                with open(os.path.join(root, text_file), 'r') as f:
                    new_image_name = f.read().strip()

                # Remove illegal characters from the new_image_name
                illegal_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
                for char in illegal_characters:
                    new_image_name = new_image_name.replace(char, '')

                new_image_name_with_counter = f"{new_image_name}_{counter}{Path(image_file).suffix}"
                os.rename(os.path.join(root, image_file), os.path.join(root, new_image_name_with_counter))

                counter += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename image files with the contents of the corresponding text files.")
    parser.add_argument("input_directory", help="The directory containing the image and text files.")
    args = parser.parse_args()

    rename_images(args.input_directory)
