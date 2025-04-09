# from pixaris.feedback_handlers.gcp import BigqueryFeedbackHandler
from pixaris.feedback_handlers.local import LocalFeedbackHandler
from pixaris.frontend.main import launch_ui
from pixaris.experiment_handlers.local import LocalExperimentHandler
import yaml

# To create dummy data for the frontend: examples/frontend/create_dummy_data_for_frontend.py

config = yaml.safe_load(open("pixaris/config.yaml"))

# feedback_handler = BigqueryFeedbackHandler(
#     gcp_project_id=config["gcp_project_id"],
#     gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
#     gcp_feedback_bucket=config["gcp_feedback_bucket"],
# )
feedback_handler = LocalFeedbackHandler()

experiment_handler = LocalExperimentHandler()

launch_ui(feedback_handler, experiment_handler)
