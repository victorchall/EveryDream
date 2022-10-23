# EveryDream toolkit for fine tuning

This repo will contain tools for data engineering efforts for people interested in taking their fine tuning beyond the initial DreamBooth paper or XavierXiao's original Dreambooth implementation for Stable Diffusion, and may be useful for other projects.

For instance, by using ground truth Laion data mixed in with training data to replace "regularization" images, together with clip-interrogated captioning or original TEXT caption from laion, the final few concepts left of the original DreamBooth paper will have been removed.  This is a significant step towards towards full fine tuning capabilities. 

Captioned training together with regularization has enabled multi-subject and multi-style training at the same time without

You can download a large scale model for Final Fantasy 7 Remake here: https://huggingface.co/panopstor/ff7r-stable-diffusion and be sure to also follow up on the gist link at the bottom for more information along with links to example output of a multi-model fine tuning. 

Since DreamBooth is now fading away in favor of improved techniques, I will call the tecnique of using fully captioned training together with ground truth data "EveryDream" to avoid confusion.

If you are interested in caption training with stable diffusion and have a 24GB Nvidia GPU I suggest trying this repo out:
https://github.com/victorchall/EveryDream-trainer

## Install

Automatic venv setup scripts for linux and windows are a work in progress.  You can create one yourself or create a conda environment with the environment.yaml, and I suggest you do so to avoid dependecy conflicts.  This repo mainly uses aiohttp, aiofile, and pandas for the time being but expect other packages to be added in the future.

    conda env create -f environment.yaml

Or you can configure your own venv, container, or just on your local Python use:

    pip install -r requirements.txt

## download_laion.py

![](demo/demo03.png)

This script enables you to webscrape using the Laion parquet files which are available on Huggingface.co. 

It has been tested with 2B-en-aesthetic, but may need minor tweaks for some other datasets that contain different columns.

https://huggingface.co/datasets/laion/laion2B-en-aesthetic


 It will rename downloaded files to the best of its ability to the TEXT (caption) of the image with the original file extension, which can be plugged into the new class of caption-capable DreamBooth apps that will use the filename as the prompt for training.  

One suggested use is to take this data and replace regularization images with ground truth data from the Laion dataset.

It should execute quite quickly as it uses async task gathers for the the HTTP and fileio work. 

Default folders are /laion for the parquest files and /output for downloaded images relative to the root folder, but consider disk space and point to another location if needed.

ex. Query all the parquet files in ./laion for any image with a caption (TEXT) containing "a man" and attempt top stop after downloading (approximately) 50 files:

    python scripts/download_laion.py --search_text "a man" --limit 50

Query for person with a leading and trailing space, as they are not stripped:

    python scripts/download_laion.py --search_text " person " --limit 200

Query for both "man" and "photo" anywhere in the caption, and write them to z:/myDumpFolder instead of the default folder.  Useful if you need to put them on another drive, NAS, etc.  The default limit of 100 images will apply since --limit is omitted:

    python scripts/download_laion.py --search_text "man,photo" --out_dir "z:/myDumpFolder" --laion_dir "x:/datahoard/laion5b"

![](demo/demo02.png)

## Other resources

Nvidia has compiled a close up photo set here: https://github.com/NVlabs/ffhq-dataset