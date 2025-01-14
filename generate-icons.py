# prompt = "Generate a single color green logo for an operability best practice called "{{pattern_name}}", that is defined as "{{short_description}}""
import os
import yaml
import re
from PIL import Image
import logging
import stablediff

logging.basicConfig(level=logging.INFO)

white = (255, 255, 255, 255)

def generate_icon(text, icon_file):

    full_prompt = f"""
        Generate a monochrome line art icon with thick lines and a minimalist and modern aesthetic, black on a white background. No shading.
        It represents a {text}.
    """

    payload = {
        "prompt": full_prompt,  # extra networks also in prompts
        "negative_prompt": "shading complex",
#        "seed": 1,
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "sampler_name": "DPM++ 2M Karras",
        "n_iter": 1,
        "batch_size": 1,

        # example args for x/y/z plot
        # "script_name": "x/y/z plot",
        # "script_args": [
        #     1,
        #     "10,20",
        #     [],
        #     0,
        #     "",
        #     [],
        #     0,
        #     "",
        #     [],
        #     True,
        #     True,
        #     False,
        #     False,
        #     0,
        #     False
        # ],

        # example args for Refiner and ControlNet
        # "alwayson_scripts": {
        #     "ControlNet": {
        #         "args": [
        #             {
        #                 "batch_images": "",
        #                 "control_mode": "Balanced",
        #                 "enabled": True,
        #                 "guidance_end": 1,
        #                 "guidance_start": 0,
        #                 "image": {
        #                     "image": encode_file_to_base64(r"B:\path\to\control\img.png"),
        #                     "mask": None  # base64, None when not need
        #                 },
        #                 "input_mode": "simple",
        #                 "is_ui": True,
        #                 "loopback": False,
        #                 "low_vram": False,
        #                 "model": "control_v11p_sd15_canny [d14c016b]",
        #                 "module": "canny",
        #                 "output_dir": "",
        #                 "pixel_perfect": False,
        #                 "processor_res": 512,
        #                 "resize_mode": "Crop and Resize",
        #                 "threshold_a": 100,
        #                 "threshold_b": 200,
        #                 "weight": 1
        #             }
        #         ]
        #     },
        #     "Refiner": {
        #         "args": [
        #             True,
        #             "sd_xl_refiner_1.0",
        #             0.5
        #         ]
        #     }
        # },
        # "enable_hr": True,
        # "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
        # "hr_scale": 2,
        # "denoising_strength": 0.5,
        # "styles": ['style 1', 'style 2'],
        # "override_settings": {
        #     'sd_model_checkpoint': "sd_xl_base_1.0",  # this can use to switch sd model
        # },
    }
    stablediff.call_txt2img_api(icon_file, **payload)    

def get_image_bounds(img):
    img = img.convert('L')
    img = img.point(lambda p: p > 190 and 255)
    img = img.convert('1')
    img = img.point(lambda p: p == 0)
    bbox = img.getbbox()
    return bbox

def generate_icons(yml_file):
    with open(yml_file, newline='') as yamlfile:
        patterns = yaml.load(yamlfile, Loader=yaml.FullLoader)
        for pattern in patterns:
            if pattern['family'] == 'prefix' or pattern['family'] == 'suffix':
                continue

            pattern_slug = pattern['pattern_name'].lower().replace(' ', '-')
            pattern_slug = re.sub(rf'[!]', '', pattern_slug)
            icon_file = f"static/images/icons/{pattern_slug}.png"

            # check if icon already exists
            if not os.path.exists(icon_file):
                print(f"Creating icon for {pattern['pattern_name']}")
                generate_icon(pattern['icon_prompt'], icon_file)

            
            # load image
            img = Image.open(icon_file)

            # check if image needs to be cropped
            bounds = get_image_bounds(img)
            if img.size != (bounds[2], bounds[3]):
                print(f"Cropping icon for {pattern['pattern_name']}")
                img = img.crop(bounds)
            else:
                print(f"Icon for {pattern['pattern_name']} is already cropped")

            if not img.has_transparency_data:
                # convert white to transparent
                img = img.convert('RGBA')
                datas = img.getdata()
                newData = []
                for item in datas:
                    if item[0] > 220 and item[1] > 220 and item[2] > 220:
                        newData.append((255, 255, 255, 0))
                    else:
                        newData.append(item)
                img.putdata(newData)   
                
                # create 1bpp icon
                img = img.point(lambda p: p > 254 and 255)
                img.save(icon_file)

generate_icons('patterns.yaml')
generate_icons('anti_patterns.yaml')