from pixaris.feedback_handlers.gcp import BigqueryFeedbackHandler
from pixaris.frontend.main import launch_ui
import yaml

config = yaml.safe_load(open("pixaris/config.yaml"))

feedback_handler = BigqueryFeedbackHandler(
    gcp_project_id=config["gcp_project_id"],
    gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
    gcp_feedback_bucket=config["gcp_feedback_bucket"],
)
launch_ui(feedback_handler)
