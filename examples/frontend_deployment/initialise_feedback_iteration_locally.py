"""
Script to initialize a feedback iteration locally.

This script creates a new feedback iteration using the LocalFeedbackHandler.
It processes images from a local directory for use in the Pixaris feedback 
interface running locally.

Usage:
    python initialise_feedback_iteration_locally.py

Requirements:
    - pixaris package installed
    - Local directory containing images for feedback
"""

from pixaris.feedback_handlers.local import LocalFeedbackHandler
import os

print(f"Current working directory: {os.getcwd()}")

if False:  # set to True if executing from notebook
    os.chdir("../../")

# Configuration parameters - MODIFY THESE VALUES
PROJECT = "dummy_project"  # Your project name
FEEDBACK_ITERATION = "dummy_feedback_iteration"  # Name of this feedback iteration
LOCAL_IMAGE_DIRECTORY = "local_results/dummy_project/feedback_iterations/250428_dummy_feedback_iteration"  
# For dummy data examples, see: examples/dummy_data_creation

# Initialize the Local Feedback Handler
feedback_handler = LocalFeedbackHandler()

# Create feedback iteration with the provided parameters
feedback_handler.create_feedback_iteration(
    local_image_directory=LOCAL_IMAGE_DIRECTORY,
    project=PROJECT,
    feedback_iteration=FEEDBACK_ITERATION,
    dataset=None,  # optional
    experiment_name=None,  # optional
)