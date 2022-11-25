from PIL import Image, ImageOps
import os
import glob
import argparse
import aiofiles

def get_parser(**parser_kwargs):
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--img_dir",
        type=str,
        nargs="?",
        const=True,
        default="input",
        help="directory with images to be compressed",
    ),
    parser.add_argument(
        "--max_mp",
        type=float,
        nargs="?",
        const=True,
        default=1.5,
        help="maximum megapixels to compress to",
    ),
    parser.add_argument(
        "--quality",
        type=int,
        nargs="?",
        const=True,
        default=95,
        help="quality of compressed image, 0-100, suggest 90+",
    ),
    parser.add_argument(
        "--delete",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="delete original image after compression even if out_dir is different than img_dir",
    ),
    parser.add_argument(
        "--out_dir",
        type=str,
        nargs="?",
        const=True,
        default=None,
        help="output folder, default is to overwrite original",
    ),
    parser.add_argument(
        "--noresize",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="fixes EXIF rotation, saves WEBP, but do not resize",
    ),

    return parser

if __name__ == '__main__':
    parser = get_parser()
    opt = parser.parse_args()

    max_pixels = opt.max_mp * 1024000

    if opt.out_dir == None:
        opt.out_dir = opt.img_dir

    print(f"scanning: {opt.img_dir}, max pixels: {opt.max_mp}, quality: {opt.quality}")
    for infile in glob.glob(f"{opt.img_dir}/*"):
        ext = os.path.splitext(infile)[1]
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            outfile = os.path.splitext(infile)[0] + ".webp"
            outfile = os.path.join(opt.out_dir, os.path.basename(outfile))
            try:
                img = Image.open(infile)
                exif = img.getexif()
                
                w, h = img.size
                pixels = w * h

                if pixels <= max_pixels and not opt.noresize:
                    print(f"skipping {infile}, {pixels} already under max of {pixels}")
                elif opt.noresize:
                    print(f"exif rotation and WEBP compression on {infile}, to: {outfile}")
                    img = ImageOps.exif_transpose(img)
                    img.save(outfile, "WEBP", quality=opt.quality, method=5)
                else:
                    # calculate new size
                    ratio = max_pixels / pixels
                    new_w = int(w * pow(ratio, 0.5))
                    new_h = int(h * pow(ratio, 0.5))
                    new_size = (new_w, new_h)

                    try:
                        img = img.resize(new_size)
                        img = ImageOps.exif_transpose(img)
                        #img = ImageOps.fit(image = img, size = (1536,1536))
                        print(f"compressing: {pixels} to {new_w*new_h} pixels, in: {infile}, out: {outfile}")

                        if opt.delete:
                            print(f"deleting: {infile}")
                            os.remove(infile)

                        img.save(outfile, "WEBP", quality=opt.quality, method=5)
                    except Exception as ex:
                        print(f"error in {infile}")
                        raise ex

            except Exception as ex:
                print(f"cannot open {infile}")
                raise ex
