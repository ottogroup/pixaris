from pixaris.frontend.main import launch_ui
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler
from pixaris.experiment_handlers.gcp import GCPExperimentHandler
# from pixaris.feedback_handlers.local import LocalFeedbackHandler
# from pixaris.experiment_handlers.local import LocalExperimentHandler
import yaml


# To create dummy data for the frontend: examples/frontend/create_dummy_data_for_frontend.py

config = yaml.safe_load(open("pixaris/config.yaml"))

feedback_handler = GCPFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
experiment_handler = GCPExperimentHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
    gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
)
# feedback_handler = LocalFeedbackHandler()
# experiment_handler = LocalExperimentHandler()

launch_ui(feedback_handler, experiment_handler)
