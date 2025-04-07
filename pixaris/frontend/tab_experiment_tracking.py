import gradio as gr
import os
from pixaris.experiment_handlers.base import ExperimentHandler
import pandas as pd


def render_experiment_tracking_tab(
    experiment_tracker: ExperimentHandler,
    results_directory: str,
):
    dataset_experiment_tracking_results = gr.State(pd.DataFrame())
    with gr.Sidebar(open=True):
        gr.Markdown("Experiments")
        with gr.Row(scale=8):
            PROJECTS_DICT = experiment_tracker.load_projects_and_datasets()
            PROJECTS = [""] + list(PROJECTS_DICT.keys())
            project_name = gr.Dropdown(
                choices=PROJECTS,
                value="",
                label="Project",
                filterable=True,
            )

            # initialise hidden feedback iterations and button
            dataset = gr.Dropdown(
                visible=False,
                value="",
                choices=[""],
            )

            def update_dataset_choices(project_name, dataset):
                """Update choices of feedback iterations for selected project and display reload button."""
                dataset_choices = PROJECTS_DICT[project_name]

                dataset = gr.Dropdown(
                    label="Dataset",
                    choices=dataset_choices,
                    filterable=True,
                    multiselect=False,
                    interactive=True,
                    visible=True,
                )
                return dataset

            project_name.change(
                fn=update_dataset_choices,
                inputs=[
                    project_name,
                    dataset,
                ],
                outputs=[dataset],
            )

            experiments = gr.Dropdown(
                visible=False,
                value="",
                choices=[""],
            )

            def update_experiments_choices(
                project_name, dataset, experiments, dataset_experiment_tracking_results
            ):
                """Update choices of feedback iterations for selected project and display reload button."""
                dataset_experiment_tracking_results = (
                    experiment_tracker.load_experiment_results_for_dataset(
                        project=project_name,
                        dataset=dataset,
                    )
                )
                experiment_choices = list(
                    dataset_experiment_tracking_results["experiment_run_name"]
                    .dropna()
                    .unique()
                )
                experiment_choices.sort()
                experiments = gr.Dropdown(
                    choices=experiment_choices,
                    value=experiment_choices[-1],
                    label="Experiments",
                    filterable=True,
                    multiselect=True,
                    max_choices=100,
                    visible=True,
                )
                return experiments, dataset_experiment_tracking_results

            dataset.change(
                fn=update_experiments_choices,
                inputs=[
                    project_name,
                    dataset,
                    experiments,
                    dataset_experiment_tracking_results,
                ],
                outputs=[experiments, dataset_experiment_tracking_results],
            )

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

    with gr.Tab("Images"):

        @gr.render(inputs=[project_name, dataset, experiments, columns, gallery_height])
        def show_gallery(project_name, dataset, experiments, columns, gallery_height):
            """Renders one gallery per experiment. Render decorator enables listening to experiments checkbox group."""
            if not experiments:
                gr.Markdown("No experiment chosen.")
            else:
                for experiment_name in experiments:
                    experiment_images = os.listdir(
                        os.path.join(
                            results_directory,
                            project_name,
                            dataset,
                            experiment_name,
                            "images",
                        )
                    )
                    gr.Gallery(
                        value=experiment_images,
                        label=experiment_name,
                        columns=columns,
                        rows=1,
                        show_download_button=True,
                        show_fullscreen_button=True,
                        height=gallery_height,
                        object_fit="fill",
                    )

    with gr.Tab("Table"):

        @gr.render(inputs=[project_name, dataset])
        def show_experiment_results_table(project_name, dataset):
            if dataset != "":
                gr.DataFrame(
                    experiment_tracker.load_experiment_results_for_dataset(
                        project=project_name,
                        dataset=dataset,
                    ),
                    label="Experiment Results",
                    wrap=True,
                    show_search="filter",
                )
