# Duplicate Image Finder

This script helps you find and move duplicate images in a given directory. It supports various image formats, including PNG, JPG, JPEG, GIF, and WEBP. The script can compare images by their content or by their names in a quick mode.

## Requirements

- Python 3.6 or higher
- Pillow (PIL) library
- tqdm library

To install the required libraries, run:

## Usage

To use the script, navigate to the directory containing the script and run the following command:

- <input_dir>: The input directory containing the images you want to check for duplicates.
- --quick: (Optional) Use this flag to enable quick mode, which compares images by their names instead of their content.

The script will create a folder named "dupe" within the input directory and move the detected duplicate images into it.
This is done instead of deleting so the user can double check on the results

## Example

To find and move duplicate images in the "C:\Users\username\Desktop\Data_set" directory, run:
python Dupe_finder.py "C:\Users\username\Desktop\Data_set"

To use quick mode for the same directory, run:
python Dupe_finder.py "C:\Users\username\Desktop\Data_set" --quick

## How it works

The script first indexes the image hashes and stores them in a file named "imagehashes.txt" within the input directory. It saves the progress every 10% to ensure that most of the progress is retained in case of a crash. The script then compares the images to find duplicates and moves them to the "dupe" folder.

In quick mode, the script compares images by their names instead of their content, which can be faster but far less accurate. (uses string before _ in filenames)