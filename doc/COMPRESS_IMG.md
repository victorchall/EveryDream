# Mass compressing images in a folder

## How it Works

This script will sweep a folder and compress all the images to a given total number of megapixels.  Aspect ratio is not changed and nothing is cropped.

*Images will only be resized if they exceed the specified megapixel limit.* Images within the limit will not be resized.

This script will also correct issues with images having EXIF directives that rotate the image.  Or, in other words, it will make sure the proper orientation is saved native to the output image as trainers may not respect EXIF rotation directives.

EXIF rotation correction will take place regardless of whether images are resized.

Note this script will not attempt to copy or move any ICC color profiles at this time.  Trainers likely do not respect this anyway...

Defaults are 1.5 megapixels, output is WEBPb at "quality 95" which affects the compression ratio.  90-99 are sane values for quality.  For the purposes of training stable diffusion, 1.5 megapixels is a good balance between quality and file size, and quality of 90-99 is as well. 

If you are hoping to use massive training files in the future as tech advances, you may wish to change the --max_mp setting to a higher value, but for now 1.5MP is more than enough to last for a few more advances in the technology.  Ultimately this is your choice.  EveryDream trainer is built to handle multiple aspects, but if you want to use images for another trainer and will crop square, you may wish to use a higher value to make sure the images remain large after croppy, or consider cropping carefully first *before* running this script. 

## Usage

    usage: compress_img_2.py [-h] [--img_dir IMG_DIR] [--out_dir OUT_DIR]
                            [--max_mp MAX_MP] [--quality QUALITY] [--overwrite]
                            [--noresize] [--delete]

    Compress images in a directory.

    options:
    -h, --help         show this help message and exit
    --img_dir IMG_DIR  path to image directory (default: 'input')
    --out_dir OUT_DIR  path to output directory (default: IMG_DIR)
    --max_mp MAX_MP    maximum megapixels (default: 1.5)
    --quality QUALITY  save quality (default: 95, range: 0-100, suggested: 90+)
    --overwrite        overwrite files in output directory
    --noresize         do not resize, just fix orientation
    --delete           delete original files after processing

The most basic use will load images from the local `input` directory, scale and rotate all the images, then write them back to the same folder. Default size is 1.5 megapixels.

    python scripts/compress_img.py

To specify the image source directory, specify the `--img_dir`:

    python scripts/compress_img.py --img_dir Q:\big_images

To save compressed images to a different path, specify the `--out_dir`:

    python scripts/compress_img.py --img_dir Q:\big_images --out_dir Q:\small_images

If a specific image already exists in the output path, **it will be skipped**. For example, if you run the script twice, existing `.webp` images in the output directory will be skipped entirely. To overwrite existing files, use the `--overwrite` directive:

    python scripts/compress_img.py --img_dir Q:\big_images --overwrite

If you want to ensure no files are skipped, *without overwriting existing images,* use `--out_dir` to specify an empty output folder.

If you want to delete the *original source image* after it has been resized, use the `--delete` directive:

    python scripts/compress_img.py --img_dir Q:\big_images --delete

The `--delete` directive will not delete the original if it was overwritten or skipped.

To change the max megapixels, use the `--max_mp` option. For example, to set max megapixels to 2.0 and overwrite existing images in the output directory, see this example:

    python scripts/compress_img.py --img_dir Q:\big_images --out_dir Q:\small_images --max_mp 2.0 --overwrite

Once you are comfortable with what is going on and OK with removing original images, you can use this to just replace everything in-place (these are my preferred settings):

    python scripts/compress_img.py --img_dir Q:\big_images --max_mp 1.5 --quality 99 --overwrite --delete

This will compress all images in the `Q:\big_images` directory down to a maximum `1.5` megapixels, at quality `99`, and will `overwrite` any existing output images and `delete` the original, un-altered image.
