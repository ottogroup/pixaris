# %% [markdown]
# # Create Dummy Data for Pixaris Frontend: Local Data Handling
#
# This script creates dummy experiment and feedback data locally using the LocalExperimentHandler and LocalFeedbackHandler.
# It generates and stores dummy tiger images locally for use in the Pixaris experiment tracking
# and feedback interfaces.
#
# ## Requirements
# - pixaris package installed
# - test assets available in the project structure

# %% [markdown]
# ## Import Libraries and Setup

# %%
import random
import shutil
import os
from PIL import Image, ImageDraw
from pixaris.feedback_handlers.local import LocalFeedbackHandler
from pixaris.experiment_handlers.local import LocalExperimentHandler


print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")

# %% [markdown]
# ## Define Tiger Image Creation Function


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
# ## Configuration Parameters

# %%
# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
DATASET = "dummy_dataset"  # Your dataset name
EXPERIMENT_RUN_NAME = "dummy-run"  # Name of this experiment run
FEEDBACK_ITERATION_NAME = "dummy_feedback_iteration"  # Name for the feedback iteration

# Number of dummy data entries to create
NUM_EXPERIMENT_ENTRIES = 5
NUM_FEEDBACK_ENTRIES = 8

# %%
# Create minimal dummy workflow data
WORKFLOW_APIFORMAT_JSON = {"prompt": "YOUR PROMPT"}

# Create a dummy workflow image using the tiger image function
WORKFLOW_PILLOW_IMAGE = create_tiger_image(random.randint(0, 10_000_000))

# %% [markdown]
# ## PART 1: Create Dummy Data for Experiment Tracking
# %%
print("\n=== Creating Dummy Experiment Data ===")

experiment_handler = LocalExperimentHandler()

# Generate dummy images (simulating images from a Generator)
dummy_image_name_pairs = [
    (create_tiger_image(random.randint(0, 10_000_000)), f"tiger_{i + 1}.png")
    for i in range(NUM_EXPERIMENT_ENTRIES)
]

# Create arguments dictionary for the experiment handler
dummy_args = {
    "workflow_apiformat_json": WORKFLOW_APIFORMAT_JSON,
    "workflow_pillow_image": WORKFLOW_PILLOW_IMAGE,
    "project": PROJECT,
    "dataset": DATASET,
    "experiment_run_name": EXPERIMENT_RUN_NAME,
}

print(
    f"Storing {NUM_EXPERIMENT_ENTRIES} dummy experiment results for project '{PROJECT}', dataset '{DATASET}'"
)
experiment_handler.store_results(
    project=PROJECT,
    dataset=DATASET,
    experiment_run_name=EXPERIMENT_RUN_NAME,
    image_name_pairs=dummy_image_name_pairs,
    metric_values={},
    args=dummy_args,
)
print("Experiment data successfully stored locally")

# %% [markdown]
# ## PART 2: Create Dummy Data for Feedback Tracking

# %%
print("\n=== Creating Dummy Feedback Data ===")

# Create a temporary directory for the images
LOCAL_IMAGE_DIRECTORY = "local_results/dummy_project/feedback_iterations/feedback_iteration_with_dummy_images"
os.makedirs(LOCAL_IMAGE_DIRECTORY, exist_ok=True)

# Generate dummy images and save to temporary directory
print(f"Generating {NUM_FEEDBACK_ENTRIES} dummy feedback images")
for i in range(NUM_FEEDBACK_ENTRIES):
    img = create_tiger_image(random.randint(0, 10_000_000))
    img.save(f"{LOCAL_IMAGE_DIRECTORY}/tiger_{i + 1}.png")
local_image_directory = LOCAL_IMAGE_DIRECTORY

# %%
# Initialize the Local Feedback Handler
feedback_handler = LocalFeedbackHandler()

# Create feedback iteration with the provided parameters
print(
    f"Creating feedback iteration '{FEEDBACK_ITERATION_NAME}' for project '{PROJECT}'"
)
feedback_handler.create_feedback_iteration(
    local_image_directory=local_image_directory,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION_NAME,
    dataset=DATASET,  # optional
    experiment_name=EXPERIMENT_RUN_NAME,  # optional
)
print("Feedback iteration successfully created locally")

# %% [markdown]
# ## Clean Up

# %%
# Clean up the temporary directory
if False:
    shutil.rmtree(LOCAL_IMAGE_DIRECTORY)
    print("Temporary directory cleaned up")
print("\nDummy data creation completed successfully!")
