# Bulk Image Renaming Utility

## Overview
The Image Renaming Utility is a command-line Python script that renames image files in a specified directory and its subdirectories. The script replaces colons, backslashes, and underscores in the original file and directory names with commas, spaces, and hyphens, respectively. It also removes a specific string from the new names and adds an index number to each file.

## Requirements
- Python 3.6 or later

## Installation
1. Download the script `image_renaming_util.py` to your desired folder.
2. Ensure you have Python 3.6 or later installed. You can check your Python version by running `python --version` in your command prompt or terminal.

## Usage
Run the script in the command prompt or terminal with the desired options:

```
python image_renaming_util.py [options]
```

### Options
```
--img_dir <path>       Path to the image directory (default: 'input')
```

### Example
```
python image_renaming_util.py --img_dir images
```

This command will rename image files in the 'images' directory according to the specified rules.

## Customization
To customize the renaming rules, modify the following lines in the script:
- Replace the specific string you want to remove: `new_root = new_root.replace("C, , Users, shawn, Desktop,", "")`
- Change the characters being replaced: `new_root = root.replace(":", ", ").replace("\\", ", ").replace("_", "-")`

## Notes
- Ensure you have the necessary permissions to read and write to the input directory and the image files within it.
- Be cautious when running the script on important files, as the renaming process is irreversible. Consider creating a backup before using the utility.

## License
This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).