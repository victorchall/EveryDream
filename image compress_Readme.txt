# Image Compression Utility

## Overview
The Image Compression Utility is a command-line Python script that compresses images in a specified directory and its subdirectories to a maximum megapixel size. The script supports JPEG, PNG, and WebP formats. The tool can also fix image orientation, and optionally delete the original files after processing.

## Requirements
- Python 3.6 or later
- Pillow library: Install by running `pip install pillow`

## Installation
1. Download the script `image_compression_util.py` to your desired folder.
2. Ensure you have Python 3.6 or later installed. You can check your Python version by running `python --version` in your command prompt or terminal.
3. Install the Pillow library by running `pip install pillow`.

## Usage
Run the script in the command prompt or terminal with the desired options:

```
python image_compression_util.py [options]
```

### Options
```
--img_dir <path>       Path to the image directory (default: 'input')
--out_dir <path>       Path to the output directory (default: IMG_DIR)
--max_mp <float>       Maximum megapixels (default: 1.5)
--quality <int>        Save quality (default: 95, range: 0-100, suggested: 90+)
--overwrite            Overwrite files in the output directory
--noresize             Do not resize, just fix orientation
--delete               Delete original files after processing (default: True)
```

### Example
```
python image_compression_util.py --img_dir images --out_dir compressed --max_mp 2 --quality 90 --overwrite --delete
```

This command will compress images in the 'images' directory, save the compressed images to the 'compressed' directory, with a maximum size of 2 megapixels, a quality of 90, and delete the original files after processing.

## Notes
- The supported image formats are JPEG, PNG, and WebP.
- The script utilizes multi-threading for better performance on multi-core processors.
- Ensure you have the necessary permissions to read and write to the input and output directories, as well as the image files within them.

## License
Original Code by Victorchall add relevant license here
-- this just adds multi folder function to the original code