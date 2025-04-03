import os
from datetime import datetime
from pixaris.feedback_handlers.local import LocalFeedbackHandler


def initialise_iteration_locally(
    project: str,
    feedback_iteration: str,
    image_names: list[str],
):
    """
    Initialise feedback iteration locally
    """
    local_feedback_handler = LocalFeedbackHandler()

    # for each image, create the upload entry in feedback table
    for image in image_names:
        feedback = {
            "project": project,
            "feedback_iteration": feedback_iteration,
            "image_name": image,
            "feedback_indicator": "Neither",  # used only for initialisation of feedback iteration
            "comment": "upload",
        }
        local_feedback_handler.write_single_feedback(feedback)


def create_feedback_iteration(
    images_directory: str,
    project: str,
    feedback_iteration: str,
    date_suffix: str = None,
):
    """
    Upload images to a folder and persist initialisation of feedback iteration to BigQuery.

    Args:
        images_directory (str): Path to local directory containing images to upload.
        feedback_iteration (str): Name of feedback iteration.
        date_suffix (str): Suffix to add to feedback iteration
    """
    image_names = os.listdir(images_directory)

    # add date for versioning if not provided
    if not date_suffix:
        date_suffix = datetime.now().strftime("%y%m%d")
    feedback_iteration = f"{date_suffix}_{feedback_iteration}"

    initialise_iteration_locally(
        project=project, feedback_iteration=feedback_iteration, image_names=image_names
    )


# ### Create Feedback Iteration

project = "mock"
feedback_iteration = "test_feedback_iteration_01"
images_directory = (
    "/home/fidelius/tiga_pixaris/local_results/mock/example-run_20250401-115520"
)

create_feedback_iteration(
    images_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
)
