import gradio as gr
import os
from pixaris.frontend.tab_feedback import render_feedback_tab
from pixaris.frontend.tab_experiment_tracking import render_experiments_tab

from pixaris.feedback_handlers.gcp import BigqueryFeedbackHandler


import yaml


def launch_ui(feedback_handler):
    with gr.Blocks(
        title="Pixaris",
        theme=gr.themes.Default(
            spacing_size=gr.themes.sizes.spacing_sm, radius_size="none"
        ),
    ) as demo:
        results_directory = "local_results/"
        with gr.Tab("Experiments"):
            render_experiments_tab(results_directory=results_directory)

        with gr.Tab("Feedback"):
            render_feedback_tab(
                feedback_handler=feedback_handler,
            )
    demo.launch(
        server_name="localhost", server_port=7860, allowed_paths=[os.path.abspath("./")]
    )


if __name__ == "__main__":
    config = yaml.safe_load(open("pixaris/config.yaml"))

    feedback_handler = BigqueryFeedbackHandler(
        gcp_project_id=config["gcp_project_id"],
        gcp_bq_feedback_table=config["gcp_bq_feedback_table"],
        gcp_feedback_bucket=config["gcp_feedback_bucket"],
    )
    launch_ui(feedback_handler)
