# from pixaris.feedback_handlers.gcp import BigqueryFeedbackHandler
from pixaris.feedback_handlers.local import LocalFeedbackHandler
from pixaris.frontend.main import launch_ui
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
import yaml


# To create dummy data for the frontend: examples/frontend/create_dummy_data_for_frontend.py

config = yaml.safe_load(open("pixaris/config.yaml"))

feedback_handler = LocalFeedbackHandler()  # TODO

experiment_tracker = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
)

launch_ui(feedback_handler, experiment_tracker)
