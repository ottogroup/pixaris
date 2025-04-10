# +
from google.cloud import storage
import os
import yaml
from datetime import datetime
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler

config = yaml.safe_load(open("pixaris/config.yaml"))

# -

# ### function definitions


def initialise_iteration_in_bigquery(
    project: str,
    feedback_iteration: str,
    image_names: list[str],
):
    """
    Initialise feedback iteration in BigQuery and upload images to GCP bucket.
    """
    gcp_feedback_handler = GCPFeedbackHandler(
        gcp_project_id=config["gcp_project_id"],
        gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
        gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    )

    # for each image, create the upload entry in feedback table
    for image in image_names:
        feedback = {
            "project": project,
            "feedback_iteration": feedback_iteration,
            "image_name": image,
            "feedback_indicator": "Neither",  # used only for initialisation of feedback iteration
            "comment": "upload",
        }
        gcp_feedback_handler.write_single_feedback(feedback)


def upload_images_to_bucket(
    project: str,
    feedback_iteration: str,
    image_names: list[str],
):
    """
    Upload images to GCP bucket.
    """
    storage_client = storage.Client(project=config["gcp_project_id"])
    bucket = storage_client.bucket(config["gcp_pixaris_bucket_name"])

    for filename in image_names:
        if filename.endswith((".jpg", ".jpeg", ".png", ".tif")):
            blob = bucket.blob(f"results/{project}/feedback_iterations/{feedback_iteration}/{filename}")
            blob.upload_from_filename(os.path.join(images_directory, filename))
            print(f"Uploaded {filename} to {feedback_iteration}")


def create_feedback_iteration(
    images_directory: str,
    project: str,
    feedback_iteration: str,
    date_suffix: str = None,
):
    """
    Upload images to GCP bucket and persist initialisation of feedback iteration to BigQuery.

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

    upload_images_to_bucket(
        project=project, feedback_iteration=feedback_iteration, image_names=image_names
    )
    initialise_iteration_in_bigquery(
        project=project, feedback_iteration=feedback_iteration, image_names=image_names
    )


# ### Create Feedback Iteration

project = "name_of_project"
feedback_iteration = "name_of_feedback_iteration"
images_directory = "local_path_to_directory_with_images"

create_feedback_iteration(
    images_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
)
