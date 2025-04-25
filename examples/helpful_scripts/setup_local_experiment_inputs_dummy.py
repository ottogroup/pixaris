import json
import os
from pathlib import Path
from PIL import Image
import yaml
from google.cloud.storage import Client
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.metrics.utils import normalize_image

config = yaml.safe_load(open("pixaris/config.yaml"))

PROJECT_NAME = "your_project_name"  # adjust here
DATASET_NAME = "your_dataset_name"  # adjust here
EVAL_DATA_DIR = (
    "local_experiment_inputs"  # default location for the evaluation datasets
)


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


def standardise_images(
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
            dpi=(300, 300),
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
            dpi=(300, 300),
        )  # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts


def upload_to_gcs(
    gcp_project_id,
    gcp_pixaris_bucket_name,
    eval_data_dir="local_experiment_inputs",
    project_name="your_project_name",
    dataset_name="your_dataset_name",
):
    """
    Upload the dataset to a Google Cloud Storage bucket.
    """
    # Set up the GCP client and bucket
    gcp_client = Client(project=gcp_project_id)
    gcp_bucket = gcp_client.bucket(gcp_pixaris_bucket_name)

    # get paths of all files to be uploaded
    dataset_dir = os.path.join(eval_data_dir, project_name, dataset_name)
    directory_as_path_obj = Path(dataset_dir)
    paths = directory_as_path_obj.rglob("*")

    # Filter so the list only includes files, not directories themselves.
    file_paths = [path for path in paths if path.is_file()]

    # These paths are relative to the current working directory. Next, make them relative to `dataset_dir`
    relative_paths = [path.relative_to(dataset_dir) for path in file_paths]

    # Finally, convert them all to strings.
    string_paths = [str(path) for path in relative_paths]

    print("Found {} files.".format(len(string_paths)))
    print(string_paths)

    for filename in string_paths:
        blob = gcp_bucket.blob(
            f"experiment_inputs/{project_name}/{dataset_name}/{filename}"
        )
        blob.upload_from_filename(os.path.join(dataset_dir, filename))
        print(
            f"Uploaded {filename} to experiment_inputs/{project_name}/{dataset_name}/{filename}"
        )


# execute the functions above
if not os.path.exists(os.path.join(EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME)):
    setup_eval_data_directory(
        eval_data_directory=EVAL_DATA_DIR,
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
    )
    img_names = standardise_images(
        source_directory="test/test_project/mock/input",
        target_directory=os.path.join(
            EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME, "Input"
        ),
        target_size=(1024, 1024),  # adjust here
    )
    generate_masks(
        img_names,
        workflow_apiformat="test/assets/segment_animals_apiformat.json",
        target_directory=os.path.join(
            EVAL_DATA_DIR, PROJECT_NAME, DATASET_NAME, "Mask"
        ),
    )

# optional: upload to GCS
if False:
    upload_to_gcs(
        gcp_project_id=config["gcp_project_id"],
        gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
        eval_data_dir=EVAL_DATA_DIR,
        project_name=PROJECT_NAME,
        dataset_name=DATASET_NAME,
    )
