# Data set Balancer via Image Multiplier Calculator

This script calculates the multiplier that should be applied to the number of images in each subfolder of a given directory, to equalize the number of images across all subfolders. It writes the calculated multiplier to a text file named `multiply.txt` in each subfolder. 

For example, if the average number of images across all subfolders is 50, and a particular subfolder has 25 images, then the multiplier for that folder would be 2. Conversely, if a folder has 100 images, the multiplier would be 0.5. 

## Requirements
- Python 3.7 or higher
- tqdm library (`pip install tqdm`)

## Usage

```bash
python image_multiplier.py /path/to/your/directory
```

Replace `/path/to/your/directory` with the path to the directory you want to process.

## Output

The script will create a `multiply.txt` file in each subfolder of the input directory. This file will contain a single number, which is the multiplier for that folder.

## Progress

The script uses a progress bar to indicate its progress. The progress bar updates after each subfolder's multiplier is calculated and written.

## How it Works

The script works by first traversing the input directory and counting the number of images in each subfolder. It then calculates the average number of images across all subfolders. 

Next, the script calculates a multiplier for each subfolder by dividing the average count by the number of images in that subfolder. If a subfolder contains no images, its multiplier is set to 0.

Finally, the script writes each subfolder's multiplier to a `multiply.txt` file in that subfolder.

## Limitations

This script counts only files with the following extensions as images: .png, .jpg, .jpeg, .gif, .webp. 

If the script is run multiple times on the same directory, it will overwrite the existing `multiply.txt` files.