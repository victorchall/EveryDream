# EveryDream Tools

This repo will contain tools for data engineering efforts for people interested in taking their fine tuning beyond the initial DreamBooth paper implementations for Stable Diffusion, and may be useful for other image projects.

If you are looking for trainers, check out [EveryDream 2.0](https://github.com/victorchall/EveryDream2trainer).  This is just a toolkit repo for data work but works in concert with that trainer.

For instance with Stable Diffusion, by using ground truth Laion data mixed in with training data to replace "regularization" images, together with clip-interrogated captioning or original TEXT caption from laion, or human-geneated labels, training quality can be improved.  These are a significant steps towards towards full fine tuning capabilities. 

Captioned training together with regularization has enabled multi-subject and multi-style training at the same time, and can scale to larger training efforts.

As an example project, you can download a large scale model for Final Fantasy 7 Remake here: https://huggingface.co/panopstor/ff7r-stable-diffusion and be sure to also follow up on the gist link at the bottom for more information along with links to example output of a multi-model fine tuning. 

Join the EveryDream discord here: https://discord.gg/uheqxU6sXN

## Tools

[Download scrapes using Laion](./doc/LAION_SCRAPE.md) - Web scrapes images off the web using Laion data files (runs on CPU).

[Auto Captioning](./doc/AUTO_CAPTION.md) - Uses BLIP interrogation to caption images for training (includes colab notebook, needs minimal GPU).

[File renaming](./doc/FILE_RENAME.md) - Simple script for replacing generic pronouns that come out of clip in filenames with proper names (ex "a man" -> "john doe", "a person" -> "jane doe").

*See clip_rename.bat for an example to chain captioning and renaming together.*

[Compress images](./doc/COMPRESS_IMG.md) - Compresses images to WEBP with a given size (ex 1.5 megapixels) to reduce disk usage if you've downloaded some massive PNG data sets (ex. FFHQ) and wish to save some disk space.

[Training](https://github.com/victorchall/EveryDream2trainer) (separate repo) - Fine tuning

[Image Caption GUI](./doc/CAPTION_GUI.md) and [Video frame extractor](./doc/VIDEO_EXTRACTOR.md) courtesy of [MStevenson](https://github.com/mstevenson/)

[General Tools Notebook](EveryDream_Tools.ipynb) Collection of various tools in this codebase by [Nawnie](https://github.com/nawnie) if you prefer to use Notebook GUI instead of the command line.

## Install

You can use conda or venv.  This was developed on Python 3.10.5 but may work on older newer versions.

One step venv setup:

    create_venv.bat

Don't forget to activate every time you open the command prompt later.

    activate_venv.bat

To use conda instead of venv:

    conda env create -f environment.yaml

    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113

    git clone https://github.com/salesforce/BLIP scripts/BLIP

    conda activate everydream

Or you if you wish to configure your own venv, container/WSL, or Linux:

    pip install -r requirements.txt

    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113

    git clone https://github.com/salesforce/BLIP scripts/BLIP

Thanks to the SalesForce team for the [BLIP tool](https://github.com/salesforce/BLIP). It uses CLIP to produce sane sentences like you would expect to see in alt-text.
