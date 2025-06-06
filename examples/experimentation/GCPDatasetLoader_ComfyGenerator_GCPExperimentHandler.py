# %% [markdown]
# # Pixaris Experimentation: GCP Dataset Loader with Comfy Generator and GCP Experiment Handler
#
# This script demonstrates using the GCP Dataset Loader with ComfyGenerator and GCP Experiment Handler.
# It loads data from GCP storage, processes it with ComfyUI, and saves results back to GCP.
#
# ## Requirements
# - pixaris package installed
# - GCP configuration in config.yaml
# - Access to GCP resources

# %% [markdown]
# ## Import Libraries and Setup

# %%
import os
import yaml
import json
from PIL import Image
from pixaris.data_loaders.gcp import GCPDatasetLoader
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.generation.comfyui import ComfyGenerator
from pixaris.orchestration.base import generate_images_based_on_dataset

# %% [markdown]
# ## Configuration Parameters

# %%
# Load configuration
config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Define project parameters
PROJECT = "dummy_project"
DATASET = "dummy_dataset"
EXPERIMENT_RUN_NAME = "example-run"

# Load workflow data
with open(os.getcwd() + "/test/assets/test_inspo_apiformat.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(os.getcwd() + "/test/assets/test_inspo.png")


# %% [markdown]
# ## Initialize Components

# %%
# Initialize the data loader
data_loader = GCPDatasetLoader(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    project=PROJECT,
    dataset=DATASET,
    eval_dir_local="local_experiment_inputs",
)

# Initialize the image generator
generator = ComfyGenerator(workflow_apiformat_json=WORKFLOW_APIFORMAT_JSON)

# Initialize the experiment handler
experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# Define the arguments for the generation
args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "pillow_images": [
        {
            "node_name": "Load Inspo Image",
            "pillow_image": Image.open("test/assets/test_inspo_image.jpg"),
        }
    ],
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

# %% [markdown]
# ## Execute Generation

# %%
# Execute the generation
out = generate_images_based_on_dataset(
    data_loader=data_loader,
    image_generator=generator,
    experiment_handler=experiment_handler,
    metrics=[],
    args=args,
)

# Display the first generated image
out[0][0].show()

# %% [markdown]
# ## Next Steps
#
# After execution:
# 1. Generated images are stored in the specified GCP bucket.
# 2. Experiment metadata are stored in Google BigQuery.
# 3. View results in the Pixaris UI
