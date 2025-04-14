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
        theme=gr.themes.Monochrome(
            spacing_size=gr.themes.sizes.spacing_sm, radius_size="none"
        ),
        analytics_enabled=False,
        fill_width=False,
    ) as demo:
        # add title
        with gr.Row():
            with gr.Column(scale=1, min_width=100):
                gr.Image(
                    value="test/assets/pixaris_logo.png",
                    elem_id="pixaris-logo",
                    show_label=False,
                    height=100,
                    width=100,
                    show_download_button=False,
                    show_fullscreen_button=False,
                    show_share_button=False,
                    interactive=False,
                )
            with gr.Column(scale=20):
                gr.Markdown(
                    """
                    <div style="display: flex; align-items: center; height: 100%; justify-content: flex-start;">
                        <h1 style="margin-left: 20px;">Pixaris</h1>
                    </div>
                    """
                )
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
