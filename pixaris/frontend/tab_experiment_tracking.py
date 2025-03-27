import gradio as gr
import os


def load_images(folder_name: str):
    """Loads Images from specified folder."""
    images = []
    for filename in os.listdir(folder_name):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            images.append(os.path.join(folder_name, filename))
    return images


def render_experiments_tab(results_directory: str):
    with gr.Sidebar(open=False):
        gr.Markdown("Experiments")
        with gr.Row(scale=1):
            columns = gr.Slider(
                minimum=1,
                maximum=20,
                value=8,
                label="Number of images per row",
                step=1,
            )
        with gr.Row(scale=1):
            gallery_height = gr.Slider(
                minimum=100,
                maximum=1000,
                value=360,
                label="Gallery height",
                step=10,
            )
        with gr.Row(scale=8):
            experiment_choices = os.listdir(results_directory)
            experiment_choices.sort()
            if not experiment_choices:
                experiment_choices = ["No experiments loaded"]
            experiments = gr.Dropdown(
                choices=experiment_choices,
                value=[experiment_choices[-1]],
                label="Experiments",
                filterable=True,
                multiselect=True,
                max_choices=100,
            )
    gr.Markdown("Gallery")

    @gr.render(inputs=[experiments, columns, gallery_height])
    def show_gallery(experiments, columns, gallery_height):
        """Renders one gallery per experiment. Render decorator enables listening to experiments checkbox group."""
        if len(experiments) == 0:
            gr.Markdown("No experiment chosen.")
        else:
            for experiment_name in experiments:
                experiment_images = load_images(
                    os.path.join(results_directory, experiment_name)
                )
                gr.Gallery(
                    value=experiment_images,
                    label=experiment_name,
                    columns=columns,
                    rows=1,
                    show_download_button=True,
                    show_fullscreen_button=True,
                    height="cover",
                    object_fit="fill",
                )
