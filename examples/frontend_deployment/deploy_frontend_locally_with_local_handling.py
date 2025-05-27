from pixaris.frontend.main import launch_ui
from pixaris.feedback_handlers.local import LocalFeedbackHandler
from pixaris.experiment_handlers.local import LocalExperimentHandler
import yaml


# To create dummy data for the frontend: examples/frontend/create_dummy_data_for_frontend_local.py

config = yaml.safe_load(open("pixaris/config.yaml"))

feedback_handler = LocalFeedbackHandler()
experiment_handler = LocalExperimentHandler()

launch_ui(feedback_handler, experiment_handler)
