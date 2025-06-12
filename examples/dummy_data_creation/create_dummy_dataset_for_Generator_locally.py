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
#         ├───Input
#         │   ├───image_01.jpg
#         │   └───image_02.jpg
#         ├───Mask
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
import shutil

print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")


# %%
# Configuration parameters - MODIFY THESE VALUES
BASE_DIR = "local_experiment_inputs"
PROJECT_NAME = "dummy_project"
DATASET_NAME = "dummy_dataset"

# Source and destination directories
src_dir = os.path.join("assets", DATASET_NAME)
dst_dir = os.path.join(BASE_DIR, PROJECT_NAME, DATASET_NAME)

# Copy the entire dummy_dataset directory into the destination
if os.path.exists(dst_dir):
    shutil.rmtree(dst_dir)
shutil.copytree(src_dir, dst_dir)

# %%
print("\n=== Summary ===")
print("Done! Created the following structure:")
print(f"""
local_results
└───{PROJECT_NAME}
    └───{DATASET_NAME}
        ├───Input
        │   ├───{"model_01.png"}
        │   └───{"model_02.png"}
        ├───Mask
        │   ├───{"model_01.png"}
        │   └───{"model_02.png"}
""")
print("Dummy evaluation data creation completed successfully!")
