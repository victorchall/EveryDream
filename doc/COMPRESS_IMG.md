# Mass compressing images in a folder

This script will sweep a folder and compress all the images to a given total number of megapixels.  Aspect ratio is not changed and nothing is cropped.  

*If an image is already lower than the number of megapixels specified,* **it will be skipped completely.**

This script will also correct issues with images having EXIF directives that rotate the image.  Or, in other words, it will make sure the proper orientation is saved native to the output image as trainers may not respect EXIF rotation directives.

Note this script will not attempt to copy or move any ICC color profiles at this time.  Trainers likely do not respect this anyway...

Defaults are 1.5 megapixels, output is WEBPb at "quality 95" which affects the compression ratio.  90-99 are sane values for quality.  For the purposes of training stable diffusion, 1.5 megapixels is a good balance between quality and file size, and quality of 90-99 is as well. 

If you are hoping to use massive training files in the future as tech advances, you may wish to change the --max_mp setting to a higher value, but for now 1.5MP is more than enough to last for a few more advances in the technology.  Ultimately this is your choice.  EveryDream trainer is built to handle multiple aspects, but if you want to use images for another trainer and will crop square, you may wish to use a higher value to make sure the images remain large after croppy, or consider cropping carefully first *before* running this script. 

    --img_dir: Folder to sweep for images
    --output_dir: Folder to save compressed images to (otherwise it uses the img_dir folder)
    --max_mp: Maximum number of megapixels to compress down to
    --quality: Quality of output image, 90-99 is a good range
    --delete: Delete original images after compression

The most basic form will reduce the size of all the images and write them back to the same folder.  Default size is 1.5 megapixels. 
**If the input file is .WEBP it will be overwritten.**

    python scripts/compress_img.py --img_dir Q:\mldata\nvidia-flickr-itw\test

If you want to ensure no files are overwritten, *use --out_dir to specify a different output folder.*

    python scripts/compress_img.py --img_dir Q:\big_images --out_dir Q:\small_images

To change the max megapixels to 2.0 and also make sure the source images are deleted, see this example:

    python scripts/compress_img.py --img_dir Q:\mldata\nvidia-flickr-itw\test --out_dir Q:\small_images --max_mp 2.0 --delete 

Once you are comfortable with what is going on and OK with removing existing images, you can use this to just replace everything in place, these are my preferred settings:

    python scripts/compress_img.py --img_dir Q:\mldata\nvidia-flickr-itw\00000 --max_mp 1.5 --quality 99 --delete
    