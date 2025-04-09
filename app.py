import yaml
from pixaris.frontend.main import launch_ui
from pixaris.feedback_handlers.gcp import BigqueryFeedbackHandler
from pixaris.experiment_handlers.local import LocalExperimentHandler


if __name__ == "__main__":
    config = yaml.safe_load(open("pixaris/config.yaml"))
    local_results_dir = "/tmp/local_results/"

    feedback_handler = BigqueryFeedbackHandler(
        gcp_project_id=config["gcp_project_id"],
        gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
        gcp_feedback_bucket=config["gcp_feedback_bucket"],
        local_feedback_directory=local_results_dir,
    )
    experiment_handler = LocalExperimentHandler(
        local_results_folder=local_results_dir
    )  # TODO use BigqueryExperimenthandler

    launch_ui(
        feedback_handler=feedback_handler,
        experiment_handler=experiment_handler,
        server_name="0.0.0.0",
    )
