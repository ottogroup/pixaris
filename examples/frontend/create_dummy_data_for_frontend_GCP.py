# %% [markdown]
# ## Create Dummy Data for Pixaris Frontend: Google Cloud Platform (GCP) Data Handling

# %%
import json
import random
import shutil
import os
from PIL import Image, ImageDraw
import yaml
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler

print(os.getcwd())

if False:  # set to True if executing from notebook
    os.chdir("../../")

config = yaml.safe_load(open("pixaris/config.yaml", "r"))


# %%
# define a function to setup the dummy images


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


img = create_tiger_image(random.randint(0, 10_000_000))
img

# %% [markdown]
# ### Create Dummy Data for Experiment Tracking

# %%
# Define some dummy data for experiment

# Define the number of dummy data entries you want to create
num_entries_per_experiment = 5

PROJECT = "dummy_project"
DATASET = "dummy_dataset"
with open(os.getcwd() + "/test/assets/test-background-generation.json", "r") as file:
    WORKFLOW_APIFORMAT_JSON = json.load(file)
WORKFLOW_PILLOW_IMAGE = Image.open(
    os.getcwd() + "/test/assets/test-background-generation.png"
)
EXPERIMENT_RUN_NAME = "dummy-run"

# %%
# Here, we simulate the case that we generated a bunch of images and want to track this experiment.

experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# these are the images that would come from a Generator.
dummy_image_name_pairs = [
    (create_tiger_image(random.randint(0, 10_000_000)), f"tiger_{i + 1}.png")
    for i in range(num_entries_per_experiment)
]
# args are relevant for the generator mainly, but are expected in an ExperimentHandler as well.
dummy_args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

experiment_handler.store_results(
    project=PROJECT,
    dataset=DATASET,
    experiment_run_name=EXPERIMENT_RUN_NAME,
    image_name_pairs=dummy_image_name_pairs,
    metric_values={},
    args=dummy_args,
)

# %% [markdown]
# ### Create Dummy Data for Feedback Tracking

# %%
# Define some dummy data for feedback
num_entries_per_feedback_iteration = 8

# Here, we pretend we already have a directory where we stored images, that we want to form into a feedback iteration.
temp_directory = "temp_feedback_directory"
os.makedirs("temp_feedback_directory", exist_ok=True)
for i in range(num_entries_per_feedback_iteration):
    img = create_tiger_image(random.randint(0, 10_000_000))
    img.save(f"{temp_directory}/tiger_{i + 1}.png")
local_image_directory = (
    temp_directory  # if you actually have a directory with images, you can use it here
)

# %%
# Create Feedback Iteration
feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
PROJECT = "dummy_project"
FEEDBACK_ITERATION = "dummy_feedback_iteration"

feedback_handler.create_feedback_iteration(
    local_image_directory=local_image_directory,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)

shutil.rmtree(temp_directory)  # cleanup the temp directory
