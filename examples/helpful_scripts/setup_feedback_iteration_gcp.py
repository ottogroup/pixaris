import yaml
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler

config = yaml.safe_load(open("pixaris/config.yaml"))

# ### Create Feedback Iteration
gcp_feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
project = "dummy_project"
feedback_iteration = "dummy_feedback_iteration"
images_directory = "path_to_local_directory_containing_images"

gcp_feedback_handler.create_feedback_iteration(
    local_image_directory=images_directory,
    project=project,
    feedback_iteration=feedback_iteration,
    dataset=None,  # optional
    experiment_name=None,  # optional
)
