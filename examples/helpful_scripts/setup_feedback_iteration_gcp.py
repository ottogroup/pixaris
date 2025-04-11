import yaml
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler

config = yaml.safe_load(open("pixaris/config.yaml"))

# ### Create Feedback Iteration
gcp_feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
project = "name_of_project"
feedback_iteration = "name_of_feedback_iteration"
images_directory = "local_path_to_directory_with_images"

gcp_feedback_handler.create_feedback_iteration(
    local_image_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
    dataset="your_dataset",  # optional
    experiment_name="your_experiment",  # optional
)
