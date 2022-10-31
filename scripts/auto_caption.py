import argparse
import glob
import os
from PIL import Image
import sys
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
import torch
import aiohttp
import asyncio

SIZE = 384

def get_parser(**parser_kwargs):
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--img_dir",
        type=str,
        nargs="?",
        const=True,
        default="input",
        help="directory with images to be captioned",
    ),
    parser.add_argument(
        "--out_dir",
        type=str,
        nargs="?",
        const=True,
        default="output",
        help="directory to put captioned images",
    ),
    parser.add_argument(
        "--format",
        type=str,
        nargs="?",
        const=True,
        default="filename",
        help="'filename', 'json', or 'parquet'",
    ),
    parser.add_argument(
        "--nucleus",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="use nucleus sampling instead of beam",
    ),
    parser.add_argument(
        "--q_factor",
        type=float,
        nargs="?",
        const=True,
        default=0.8,
        help="adjusts the likelihood of a word being repeated",
    ),
    parser.add_argument(
        "--min_length",
        type=int,
        nargs="?",
        const=True,
        default=24,
        help="adjusts the likelihood of a word being repeated",
    ),

    return parser

def load_image(raw_image, device):
    transform = transforms.Compose([
        #transforms.CenterCrop(SIZE),
        transforms.Resize((SIZE, SIZE), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])
    image = transform(raw_image).unsqueeze(0).to(device)
    return image

async def main(opt):
    print("starting")
    import models.blip

    sample = False
    if opt.nucleus:
        sample = True

    input_dir = opt.img_dir
    print("input_dir: ", input_dir)

    config_path = "scripts/BLIP/configs/med_config.json"

    model_cache_path = ".cache/model_base_caption_capfilt_large.pth"

    if not os.path.exists(model_cache_path):
        print(f"Downloading model to {model_cache_path}... please wait")
        blip_model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_caption_capfilt_large.pth'
        async with aiohttp.ClientSession() as session:
            async with session.get(blip_model_url) as res:
                result = await res.read()
                with open(model_cache_path, 'wb') as f:
                    f.write(result)
        print(f"Model cached to: {model_cache_path}")
    else:
        print(f"Model already cached to: {model_cache_path}")

    blip_decoder = models.blip.blip_decoder(pretrained=model_cache_path, image_size=384, vit='base', med_config=config_path)
    blip_decoder.eval()

    print("loading model to cuda")

    blip_decoder = blip_decoder.to(torch.device("cuda"))

    ext = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tga', '.tiff', '.bmp', '.gif')

    i = 0

    for idx, img_file_name in enumerate(glob.iglob(os.path.join(opt.img_dir, "*.*"))):
        if img_file_name.endswith(ext):
            caption = None
            file_ext = os.path.splitext(img_file_name)[1]
            if (file_ext in ext):
                with open(img_file_name, "rb") as input_file:
                    print("working image: ", img_file_name)

                    image = Image.open(input_file)

                    image = load_image(image, device=torch.device("cuda"))

                    if opt.nucleus:
                        captions = blip_decoder.generate(image, sample=True, top_p=opt.q_factor)
                    else:
                        captions = blip_decoder.generate(image, sample=sample, num_beams=16, min_length=opt.min_length, \
                            max_length=48, repetition_penalty=opt.q_factor)

                    caption = captions[0]

                    input_file.seek(0)
                    data = input_file.read()
                    input_file.close()

                    if opt.format in ["mrwho","joepenna"]:
                        prefix = f"{i:05}@"
                        i += 1
                        caption = prefix+caption
                    
                    out_file = os.path.join(opt.out_dir, f"{caption}{file_ext}")
                    print("   out_file:", out_file)
                    print()
                    
                    if opt.format in ["filename","mrwho"]:
                        #out_file = os.path.join(out_file)                    
                        with open(out_file, "wb") as out_file:
                            out_file.write(data)
                    elif opt.format == "json":
                        raise NotImplementedError
                    elif opt.format == "parquet":
                        raise NotImplementedError

def isWindows():
    return sys.platform.startswith("win")

if __name__ == "__main__":
    print(f"starting in {print(os.getcwd())}")
    parser = get_parser()
    opt = parser.parse_args()

    if opt.format not in ["filename", "json", "mrwho", "joepenna", "parquet"]:
        raise ValueError("format must be 'filename', 'json', or 'parquet'")
    
    if (isWindows()): 
        print("Windows detected, using asyncio.WindowsSelectorEventLoopPolicy")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        print("Unix detected, using default asyncio event loop policy")

    blip_path = "scripts/BLIP"
    sys.path.append(blip_path)

    asyncio.run(main(opt))
  