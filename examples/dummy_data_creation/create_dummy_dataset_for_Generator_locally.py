# %% [markdown]
# # Create Dummy Evaluation Data for Pixaris Generator: Local Data Handling
#
# This script creates a basic folder structure with dummy image files for evaluation purposes.
# It generates input images and corresponding mask images organized in a dataset structure.
#
# ## Folder structure created:
# ```
# local_results
# └───dummy_project
#     └───dummy_dataset
#         ├───input
#         │   ├───image_01.jpg
#         │   └───image_02.jpg
#         ├───mask
#         │   ├───image_01.jpg
#         │   └───image_02.jpg
# ```
#
# ## Requirements
# - PIL and numpy packages installed

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import random
from PIL import Image, ImageDraw

print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")

# %% [markdown]
# ## Configuration Parameters

# %%
# Configuration parameters - MODIFY THESE VALUES
BASE_DIR = "local_experiment_inputs"
PROJECT_NAME = "dummy_project"
DATASET_NAME = "dummy_dataset"
IMAGE_NAMES = ["tiger_01.png", "tiger_02.png"]

# %% [markdown]
# ## Define Helper Functions


# %%
# Function to create a directory if it doesn't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")


# Function to create a tiger image
def create_tiger_image(background_color_int: int):
    # Create a blank 64x64 pixel image
    img = Image.new("RGB", (64, 64), background_color_int)
    draw = ImageDraw.Draw(img)

    # Define colors
    orange = (255, 165, 0)
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Draw a simple tiger head shape
    draw.ellipse([16, 16, 48, 48], fill=orange)  # Head

    # Draw ears
    draw.polygon([(16, 16), (20, 8), (24, 16)], fill=orange)
    draw.polygon([(48, 16), (44, 8), (40, 16)], fill=orange)

    # Draw black stripes
    draw.line([(28, 20), (24, 28)], fill=black, width=2)  # Left stripe
    draw.line([(36, 20), (40, 28)], fill=black, width=2)  # Right stripe
    draw.arc([24, 28, 40, 44], start=0, end=180, fill=black, width=2)  # Top stripe
    draw.arc([20, 36, 44, 52], start=180, end=360, fill=black, width=2)  # Bottom stripe

    # Draw eyes
    draw.ellipse([(26, 30), (30, 34)], fill=white)  # Left eye
    draw.ellipse([(38, 30), (42, 34)], fill=white)  # Right eye
    draw.point([(28, 32), (40, 32)], fill=black)  # Pupils

    # Draw nose
    draw.polygon([(31, 40), (33, 38), (35, 40)], fill=black)

    # Draw mouth
    draw.arc([30, 42, 34, 46], start=0, end=180, fill=black, width=1)
    draw.arc([32, 42, 36, 46], start=0, end=180, fill=black, width=1)

    img = img.resize((200, 200))
    return img


# %%
# Create an example image
img = create_tiger_image(random.randint(0, 10_000_000))

# %% [markdown]
# ## Create Directory Structure

# %%
# Create the directory structure
print("\n=== Creating Directory Structure ===")
dataset_path = os.path.join(BASE_DIR, PROJECT_NAME, DATASET_NAME)
input_dir = os.path.join(dataset_path, "input")
mask_dir = os.path.join(dataset_path, "mask")

create_directory(input_dir)
create_directory(mask_dir)

# %% [markdown]
# ## Generate Input Images

# %%
print("\n=== Creating Input Images ===")
# Create input images
for i, img_name in enumerate(IMAGE_NAMES):
    image_path = os.path.join(input_dir, img_name)
    img = create_tiger_image(random.randint(0, 10_000_000))
    img.save(image_path)
    print(f"Created image: {image_path}")

# %% [markdown]
# ## Generate Mask Images

# %%
print("\n=== Creating Mask Images ===")
# Create mask images
for i, img_name in enumerate(IMAGE_NAMES):
    mask_path = os.path.join(mask_dir, img_name)
    # Create a tiger image and convert it to grayscale for mask
    img = create_tiger_image(random.randint(0, 10_000_000))
    # Convert to grayscale and threshold to binary
    mask_img = img.convert("L")
    # Apply threshold to create binary mask
    mask_img = mask_img.point(lambda x: 0 if x < 128 else 255, "1")
    mask_img.save(mask_path)
    print(f"Created mask image: {mask_path}")

# %% [markdown]
# ## Summary of Created Data

# %%
print("\n=== Summary ===")
print("Done! Created the following structure:")
print(f"""
local_results
└───{PROJECT_NAME}
    └───{DATASET_NAME}
        ├───Input
        │   ├───{IMAGE_NAMES[0]}
        │   └───{IMAGE_NAMES[1]}
        ├───Mask
        │   ├───{IMAGE_NAMES[0]}
        │   └───{IMAGE_NAMES[1]}
""")
print("Dummy evaluation data creation completed successfully!")
