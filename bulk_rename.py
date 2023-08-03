import os
import argparse

# Set up argument parser
def get_args(**parser_kwargs):
    """Get command-line options."""
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--img_dir",
        type=str,
        default="input",
        help="path to image directory (default: 'input')",
    )
    args = parser.parse_args()
    return args

# Get the input directory from parsed arguments
args = get_args()
input_directory = args.img_dir

# Iterate through directories and files
for root, dirs, files in os.walk(input_directory):
    # Replace ":" and "\\" with a space
    new_root = root.replace(":", ", ").replace("\\", ", ").replace("_", "-")
    # Remove the string "c  Users shawn Desktop"
    new_root = new_root.replace("C, , Users, shawn, Desktop,", "")
    
    # Iterate through files and rename them
    for i, file in enumerate(files):
        old_path = os.path.join(root, file)
        new_name = new_root + "_" + str(i + 1) + os.path.splitext(file)[1]
        new_path = os.path.join(root, new_name)
        
        # Rename the file
        os.rename(old_path, new_path)

