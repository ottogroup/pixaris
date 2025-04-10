import gradio as gr
import os
from pixaris.frontend.tab_feedback import render_feedback_tab
from pixaris.frontend.tab_experiment_tracking import render_experiment_tracking_tab
from pixaris.feedback_handlers.base import FeedbackHandler
from pixaris.experiment_handlers.base import ExperimentHandler


def launch_ui(
    feedback_handler: FeedbackHandler,
    experiment_handler: ExperimentHandler,
    results_directory="local_results/",
    server_name="localhost",
):
    """
    Launches the Gradio UI for Pixaris.
    Args:
        feedback_handler: The feedback handler to use.
        experiment_handler: The experiment handler to use.
        results_directory: The directory to save the results in.
        server_name: The name of the server to launch the UI on. Set "localhost" for local testing and "0.0.0.0" for app engine deployment.
    """
    with gr.Blocks(
        title="Pixaris",
        theme=gr.themes.Default(
            spacing_size=gr.themes.sizes.spacing_sm, radius_size="none"
        ),
        analytics_enabled=False,
    ) as demo:
        with gr.Tab("Experiment Tracking"):
            render_experiment_tracking_tab(
                experiment_handler=experiment_handler,
                results_directory=results_directory,
            )

        with gr.Tab("Feedback"):
            render_feedback_tab(
                feedback_handler=feedback_handler,
            )
    demo.launch(
        server_name=server_name, server_port=8080, allowed_paths=[os.path.abspath("./")]
    )
