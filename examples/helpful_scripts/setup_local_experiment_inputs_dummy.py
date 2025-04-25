# %% [markdown]
# ### Set up your data set
# A aataset is used to store and provide all nessecary input information for an experiment run.
# the structure should look like this:
#   ```
#   eval_data_directory
#   └───project_name
#       └───dataset_name
#           ├───Input
#           │   ├───image_01.jpg
#           │   └───...
#           ├───Mask
#           │   ├───image_01.jpg
#           │   └───...
#           └───...
#   ```
#   In this example, we want to use a ComfyUI workflow to generate images using an Input image and a Mask. In the workflow will be corresonding nodes "Load Input Image" and "Load Mask Image". So, we need to set up the dataset with an input and mask folder.
#   You can adapt the structure to your needs, expand it with arguments or use more kind of input images.
#   Make sure the images in the different folders have the same names.

# %%
import json
import os
from PIL import Image
import yaml
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.utils import normalize_image

if False:  # only set to True if you are running this code from a notebook
    os.chdir("../../")  # adjust working directory to pixaris root

config = yaml.safe_load(open("pixaris/config.yaml"))

PROJECT_NAME = "dummy_project"  # adjust here
DATASET_NAME = "dummy_dataset"  # adjust here
EVAL_DATA_DIR = (
    "local_experiment_inputs"  # default location for the evaluation datasets
)


# %%
# define helper functions
def setup_eval_data_directory(
    eval_data_directory=EVAL_DATA_DIR,
    project_name=PROJECT_NAME,
    dataset_name=DATASET_NAME,
):
    """
    Create the directory structure for the evaluation dataset.
    The directory structure is as follows:
    ```
    eval_data_directory
    └───project_name
        └───dataset_name
            ├───Input
            │   ├───image_01.jpg
            │   └───...
            ├───Mask
            │   ├───image_01.jpg
            │   └───...
            └───...
    ```
    """
    dataset_directory = os.path.join(eval_data_directory, project_name, dataset_name)
    os.makedirs(dataset_directory, exist_ok=True)

    input_image_dir = os.path.join(
        eval_data_directory, project_name, dataset_name, "Input"
    )
    os.makedirs(input_image_dir, exist_ok=True)

    mask_image_dir = os.path.join(
        eval_data_directory, project_name, dataset_name, "Mask"
    )
    os.makedirs(mask_image_dir, exist_ok=True)


def standardise_images_and_save_to_target_directory(
    source_directory="directory_with_input_images",
    target_directory="directory_to_save_standardised_images",
    target_size=(1024, 1024),
):
    """
    Standardise images to a target size and save them in a new directory.
    This is not strictly nessecary for the workflow to work, but it is normally a good idea
    to have a standardised set of images for the best results
    This function also copies the images to the target directory.
    """
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    img_names = [
        img
        for img in os.listdir(source_directory)
        if img.endswith((".jpg", ".jpeg", ".png", ".tif"))
    ]
    print(img_names)

    for img_name in img_names:
        img = Image.open(os.path.join(source_directory, img_name))
        standardised_img = normalize_image(img, target_size)
        standardised_img.save(
            os.path.join(target_directory, img_name),
            "PNG",
        )  # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts

    return img_names


def generate_masks(
    img_names,
    workflow_apiformat="path_to_workflow_apiformat.json",
    target_directory="directory_to_save_masks",
):
    """
    Generate masks for the images in the input directory using a ComfyUI workflow.
    The workflow is specified in the workflow_apiformat JSON file.
    The generated masks are saved in the target directory.
    """
    # make sure to use the loaded workflow_apiformat for the generator
    workflow_apiformat_json = json.load(open(workflow_apiformat))
    generator = ComfyGenerator(
        workflow_apiformat_json=workflow_apiformat_json,
    )

    for input_img_name in img_names:
        print("input_img_name: ", input_img_name)
        args = {
            "project": PROJECT_NAME,
            "dataset": DATASET_NAME,
            "workflow_apiformat_json": workflow_apiformat_json,
            "pillow_images": [
                {
                    "node_name": "Load Image",
                    "pillow_image": Image.open(
                        os.path.join(
                            EVAL_DATA_DIR,
                            PROJECT_NAME,
                            DATASET_NAME,
                            "Input",
                            input_img_name,
                        )
                    ),
                },
            ],
            "generation_params": [],
        }

        image, _ = generator.generate_single_image(args)
        image.save(
            os.path.join(target_directory, input_img_name),
            "PNG",
        )  # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts


# %%
# create the dummy dataset
if not os.path.exists(os.path.join(EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME)):
    setup_eval_data_directory(
        eval_data_directory=EVAL_DATA_DIR,
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
    )
    img_names = standardise_images_and_save_to_target_directory(
        source_directory="test/test_project/mock/input",  # adjust here for your own images
        target_directory=os.path.join(
            EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME, "input"
        ),
        target_size=(1024, 1024),  # adjust here
    )
    generate_masks(
        img_names,
        workflow_apiformat="test/assets/segment_animals_apiformat.json",
        target_directory=os.path.join(
            EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME, "mask"
        ),
    )
