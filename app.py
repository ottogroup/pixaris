import yaml
from pixaris.frontend.main import launch_ui
from pixaris.feedback_handlers.gcp import GCPFeedbackHandler
from pixaris.experiment_handlers.gcp import GCPExperimentHandler


if __name__ == "__main__":
    config = yaml.safe_load(open("pixaris/config.yaml"))
    local_results_dir = "/tmp/local_results/"

    feedback_handler = GCPFeedbackHandler(
        gcp_project_id=config["gcp_project_id"],
        gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
        gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
        local_feedback_directory=local_results_dir,
    )
    experiment_handler = GCPExperimentHandler(
        gcp_project_id=config["gcp_project_id"],
        gcp_bq_experiment_dataset=config["gcp_bq_experiment_dataset"],
        gcp_pixaris_bucket_name=config["gcp_pixaris_bucket_name"],
    )

    launch_ui(
        feedback_handler=feedback_handler,
        experiment_handler=experiment_handler,
        server_name="0.0.0.0",
        results_directory="/tmp/local_experiment_results/",
    )
