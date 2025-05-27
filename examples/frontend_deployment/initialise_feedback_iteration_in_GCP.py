"""
Script to initialize a feedback iteration in Google Cloud Platform (GCP).

This script creates a new feedback iteration in GCP using the GCPFeedbackHandler.
It loads configuration from the config.yaml file and uploads images from a
local directory to GCP for use in the Pixaris feedback interface.

Usage:
    python initialise_feedback_iteration_in_gcp.py

Requirements:
    - pixaris package installed
    - Valid GCP credentials configured
    - config.yaml with GCP settings (project_id, bucket_name, etc.)
    - Local directory containing images for feedback
"""

from pixaris.feedback_handlers.gcp import GCPFeedbackHandler
import os
import yaml

print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")

config = yaml.safe_load(open("pixaris/config.yaml", "r"))

# Initialize the GCP Feedback Handler
feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
FEEDBACK_ITERATION = "dummy_feedback_iteration"  # Name of this feedback iteration
LOCAL_IMAGE_DIRECTORY = "local_results/dummy_project/feedback_iterations/feedback_iteration_with_dummy_images"
# For dummy data examples, see: examples/dummy_data_creation

# Create feedback iteration with the provided parameters
feedback_handler.create_feedback_iteration(
    local_image_directory=LOCAL_IMAGE_DIRECTORY,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)