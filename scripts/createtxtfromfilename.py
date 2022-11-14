import glob
import os
import argparse


def create_txt_from_filename(path):
    """
    create a .txt file for each file in the path so you can lengthen the caption
    """
    print(f"Creating .txt files from filenames in {path}")
    for idx, f in enumerate(glob.iglob(f"{path}/**", recursive=True)):
        print(f"Creating {f}.txt")
        if not os.path.isfile(f) or not os.path.splitext(f)[1] in ['.jpg', '.png', '.jpeg', '.webp', '.bmp']:
            continue

        path_without_filename = os.path.dirname(f)
        base_name = os.path.splitext(os.path.basename(f))[0]
        caption = os.path.splitext(base_name)[0].split("_")[0]
        target = f"{path_without_filename}/{base_name}.txt"
        print (f"Creating file: {target} from {f}")
        with open(target, "w") as text_file:
            text_file.write(caption)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="path to folder")
    args = parser.parse_args()
    create_txt_from_filename(args.path)
