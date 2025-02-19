# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: pixaris-_wOx1PWk-py3.12
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Setup a new eval dataset
# Here, we take a set of images (possibly not all the same size), we standardise it to a target size and then create the masks for it. Lastly, we upload the new data set to gcp.

# %%
import os
from PIL import Image
from pixaris.generation.comfyui import ComfyGenerator
import yaml

config = yaml.safe_load(open("../pixaris/config.yaml"))

# %% [markdown]
# ### 1. Standardise Input Images

# %%
# decide what ratio and minimum size the images should be standardised to.
ratio_in_images = 1.25  # adjust here

target_height = 2048
target_width = int(target_height / ratio_in_images)

print("target_height: ", target_height, "target_width: ", target_width)


# %%
def standardise_image(
    img: Image.Image, target_width: int, target_height: int
) -> Image.Image:
    # resize to max_long_side_length and max_short_side_length, keeping original aspect ratio
    img.thumbnail((target_width, target_height), resample=Image.LANCZOS)

    # paste in middle of image
    x_offset = int((target_width - img.size[0]) / 2)
    y_offset = int((target_height - img.size[1]) / 2)

    # new white image
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    background.paste(img, (x_offset, y_offset))
    return background


# %%
source_directory = "directory_with_input_images"
target_directory = "directory_to_save_standardised_images"

if not os.path.exists(target_directory):
    os.makedirs(target_directory)

img_names = [
    img
    for img in os.listdir(source_directory)
    if img.endswith((".jpg", ".jpeg", ".png", ".tif"))
]
print(img_names)

for img_name in img_names:
    # open image
    img = Image.open(os.path.join(source_directory, img_name))

    # standardise
    standardised_img = standardise_image(img, target_width, target_height)

    # save
    standardised_img.save(
        os.path.join(target_directory, img_name),
        "PNG",
        dpi=(300, 300),
    )  # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts

# %% [markdown]
# ### 2. Generate Masks for Input Images

# %%
# # copy to eval_data directory so that we can create masks

eval_data_directory = "../eval_data"
eval_set_name = "eval_dataset"

eval_set_directory = os.path.join(eval_data_directory, eval_set_name)
os.makedirs(eval_set_directory, exist_ok=True)

input_image_dir = os.path.join(eval_data_directory, eval_set_name, "Input")
os.makedirs(input_image_dir, exist_ok=True)

# make dir for masks
mask_image_dir = os.path.join(eval_data_directory, eval_set_name, "Mask")
os.makedirs(mask_image_dir, exist_ok=True)

# # copy from target_directory to input_image_dir
# !cp  {target_directory}/* {input_image_dir}

# %%
# run mask generation

workflow_apiformat_path = "myworkflows/generate_mask.json"  # adjust here

generator = ComfyGenerator(
    workflow_apiformat_path=workflow_apiformat_path,
)

for input_img_name in img_names:
    print("input_img_name: ", input_img_name)
    args = {
        "eval_set": eval_set_name,
        "workflow_apiformat_path": workflow_apiformat_path,
        "image_paths": [
            {
                "node_name": "Load Input Image",
                "image_path": os.path.join(input_image_dir, input_img_name),
            },
        ],
        "generation_params": [],
    }

    image, name = generator.generate_single_image(args)
    image.save(
        os.path.join(mask_image_dir, input_img_name), "PNG", dpi=(300, 300)
    )  # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts


# %%
# all good? Then upload to bucket

bucket_name = config["gcp_bucket_name"]
# !gsutil -m cp -r {eval_data_directory} gs://{bucket_name}/
