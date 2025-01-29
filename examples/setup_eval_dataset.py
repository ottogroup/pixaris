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
#     display_name: pixaris-cO8jBQMx-py3.12
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

config = yaml.safe_load(open("pixaris/config.yaml"))

# %%
source_directory = "/Users/henrike.meyer/Library/CloudStorage/OneDrive-OttoGroup/General/Frankonia-Images/Live-Model-Location/BritishCountry"
img_paths = os.listdir(source_directory)
target_directory = "/Users/henrike.meyer/Library/CloudStorage/OneDrive-OttoGroup/General/Frankonia-Images/Mini_poc_images"

for img_name in img_paths:
    if img_name.endswith([".jpg", ".jpeg", ".png"]):
        img = Image.open(os.path.join(source_directory, img_name))
        img.save(
            os.path.join(target_directory, img_name.split(".")[0] + ".jpg"), "JPEG"
        )
    # if it is a directory continue
    if os.path.isdir(os.path.join(source_directory, img_name)):
        continue


# %%
model_images_directory = "/Users/henrike.meyer/Library/CloudStorage/OneDrive-OttoGroup/General/Frankonia-Images/Mini_poc_images/BritishCountry/models"
standardised_model_images_directory = "/Users/henrike.meyer/Library/CloudStorage/OneDrive-OttoGroup/General/Frankonia-Images/Mini_poc_images/BritishCountry/models_standardised"

if not os.path.exists(standardised_model_images_directory):
    os.makedirs(standardised_model_images_directory)


# %%
ratio_in_images = 1.25  # adjust. In the frankonia images, it was approx 6643/5314=1.25

target_height = 2048
target_width = int(target_height / ratio_in_images)

print("target_height: ", target_height, "target_width: ", target_width)


# %%
img_names = [
    img
    for img in os.listdir(model_images_directory)
    if img.endswith([".jpg", ".jpeg", ".png"])
]

for img_name in img_names:
    # new white image
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    img = Image.open(os.path.join(model_images_directory, img_name))

    # resize to max_long_side_length and max_short_side_length, keeping original aspect ratio
    img.thumbnail((target_width, target_height))

    # paste in middle of image
    x_offset = int((target_width - img.size[0]) / 2)
    y_offset = int((target_height - img.size[1]) / 2)
    background.paste(img, (x_offset, y_offset))

    background.save(os.path.join(standardised_model_images_directory, img_name), "JPEG")

# %%
# # copy to eval_data directory so that we can create masks
eval_data_directory = "../eval_data"
eval_set_name = "frankonia_hq_british_country"

eval_set_directory = os.path.join(eval_data_directory, eval_set_name)
os.makedirs(eval_set_directory, exist_ok=True)

input_image_dir = os.path.join(eval_data_directory, eval_set_name, "Input")
os.makedirs(input_image_dir, exist_ok=True)


# # copy from standardised_model_images_directory to input_image_dir
# !cp  {standardised_model_images_directory}/* {input_image_dir}

# %%


imput_image_names = os.listdir(input_image_dir)
print("input image dir:", input_image_dir)
print(imput_image_names)

# makedir for masks
mask_image_dir = os.path.join(eval_data_directory, eval_set_name, "Mask")
os.makedirs(mask_image_dir, exist_ok=True)

# %%

# loader = GCPDatasetLoader(
#     gcp_project_id=config["gcp_project_id"],
#     gcp_bucket_name=config["gcp_bucket_name"],
#     eval_set=eval_set_name,
#     eval_dir_local="eval_data",
# )
generator = ComfyGenerator(
    workflow_apiformat_path="/Users/henrike.meyer/Downloads/mask-simple-inspyrenet.json",
)

for input_img_name in imput_image_names:
    print("input_img_name: ", input_img_name)
    args = {
        "eval_set": eval_set_name,
        "workflow_apiformat_path": "/Users/henrike.meyer/Downloads/mask-simple-inspyrenet.json",
        "image_paths": [
            {
                "node_name": "Load Input Image",
                "image_path": os.path.join(input_image_dir, input_img_name),
            },
        ],
        "generation_params": [],
    }

    out = generator.generate_single_image(args)
    out.save(os.path.join(mask_image_dir, input_img_name))


# %%
# all good? Then upload to bucket

bucket_name = config["gcp_bucket_name"]
# !gsutil -m cp -r {eval_data_directory} gs://{bucket_name}/

# %%
