# EveryDream toolkit for fine tuning

This repo will contain tools for data engineering efforts for people interested in taking their fine tuning beyond the initial DreamBooth paper or XavierXiao's original Dreambooth implementation for Stable Diffusion, and may be useful for other projects.

For instance, by using ground truth Laion data mixed in with training data to replace "regularization" images, together with clip-interrogated captioning or original TEXT caption from laion, the final few concepts left of the original DreamBooth paper will have been removed.  This is a significant step towards towards full fine tuning capabilities. 

Captioned training together with regularization has enabled multi-subject and multi-style training at the same time, and can scale to larger training efforts.

For example, you can download a large scale model for Final Fantasy 7 Remake here: https://huggingface.co/panopstor/ff7r-stable-diffusion and be sure to also follow up on the gist link at the bottom for more information along with links to example output of a multi-model fine tuning. 

Since DreamBooth is now fading away in favor of improved techniques, I will call the tecnique of using fully captioned training together with ground truth data "EveryDream" to avoid confusion.

Join the EveryDream discord here: https://discord.gg/uheqxU6sXN

## Tools

[Download scrapes using Laion](./doc/LAION_SCRAPE.md) - Web scrapes images off the web using Laion data files (runs on CPU).

[Auto Captioning](./doc/AUTO_CAPTION.md) - Uses BLIP interrogation to caption images for training (includes colab notebook, needs minimal GPU).

[File renaming](./doc/FILE_RENAME.md) - Simple script for replacing generic pronouns that come out of clip in filenames with proper names (ex "a man" -> "john doe", "a person" -> "jane doe").

See clip_rename.bat for an example to chain captioning and renaming together.

[Training](https://github.com/victorchall/EveryDream-trainer) (separate repo) - Fine tuning with captioned training and ground truth data (needs 24GB GPU).

[Image Caption GUI](./doc/CAPTION_GUI.md) and [Video frame extractor](./doc/VIDEO_EXTRACTOR.md) courtesy of [MStevenson](https://github.com/mstevenson/)

## Install

You can use conda or venv.  This was developed on Python 3.10.5 but may work on older newer versions.

One step venv setup:

    create_venv.bat

Don't forget to activate every time you open the command prompt later.

    activate_venv.bat

To use conda:

    conda env create -f environment.yaml

    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113

    git clone https://github.com/salesforce/BLIP scripts/BLIP

    conda activate everydream

Or you if you wish to configure your own venv, container/WSL, or Linux:

    pip install -r requirements.txt

    pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113

    git clone https://github.com/salesforce/BLIP scripts/BLIP

Thanks to the SalesForce team for the [BLIP tool](https://github.com/salesforce/BLIP). It uses CLIP to produce sane sentences like you would expect to see in alt-text.
