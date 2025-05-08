import gradio as gr
from pixaris.feedback_handlers.base import FeedbackHandler

PROJECTS = []


def render_feedback_tab(
    feedback_handler: FeedbackHandler,
):
    # initially load all projects
    global PROJECTS
    PROJECTS = [""] + feedback_handler.load_projects_list()

    feedback_details = (
        gr.State(  # is adjusted from inside a gr.render decorated function. See below.
            value={
                "project": "",
                "feedback_iteration": "",
                "image_name": "",
                "feedback_indicator": False,
                "comment": "",
            }
        )
    )

    def adjust_feedback_details(
        img_path: str, feedback_indicator: bool, comment: str, previous_details: dict
    ):
        """
        This function is only here to adjust the feedback details (that are a gr.State object). This is
        necessary because the feedback details are determined within a function that has the gr.render
        decorator. Thus, the only way to trigger a function within the gr.render function (in this case
        we want to write the feedback) is to write the inputs to a gr.State object and then call the
        respective function within here.
        See here https://www.gradio.app/guides/state-in-blocks (see example with cart).
        """
        previous_details["project"] = img_path.split("/")[-4]  # todo make more robust
        previous_details["feedback_iteration"] = img_path.split("/")[-2]
        previous_details["image_name"] = img_path.split("/")[-1]
        previous_details["feedback_indicator"] = feedback_indicator
        previous_details["comment"] = comment
        feedback_handler.write_single_feedback(feedback=previous_details)
        return previous_details

    with gr.Sidebar(open=True, position="right"):
        with gr.Row(scale=8):
            project_name = gr.Dropdown(
                choices=PROJECTS,
                label="Project",
                filterable=True,
            )

            # initialise hidden feedback iterations and define updating function
            feedback_iterations = gr.Dropdown(visible=False)

            def update_feedback_iteration_choices(project_name, feedback_iterations):
                """Update choices of feedback iterations for selected project."""
                feedback_handler.load_all_feedback_iterations_for_project(project_name)
                feedback_iteration_choices = feedback_handler.feedback_iteration_choices

                feedback_iterations = gr.Dropdown(
                    label="Feedback Iterations",
                    value=None,
                    choices=feedback_iteration_choices,
                    visible=True,
                    filterable=True,
                    multiselect=True,
                    max_choices=100,
                    interactive=True,
                )
                return feedback_iterations

            # update feedback iterations choices upon project change
            project_name.change(
                fn=update_feedback_iteration_choices,
                inputs=[
                    project_name,
                    feedback_iterations,
                ],
                outputs=[feedback_iterations],
            )
        with gr.Row(scale=1):
            reload_projects_button = gr.Button(
                "Reload projects",
                variant="secondary",
                interactive=True,
                size="sm",
            )

            def reload_projects(project_name):
                global PROJECTS
                PROJECTS = feedback_handler.load_projects_list()
                project_name = gr.Dropdown(
                    choices=PROJECTS,
                    label="Project",
                    filterable=True,
                )
                return project_name

            reload_projects_button.click(
                fn=reload_projects,
                inputs=[project_name],
                outputs=[project_name],
            )
        with gr.Row(scale=1):
            columns = gr.Slider(
                minimum=1,
                maximum=7,
                value=5,
                label="Number of images per row",
                step=1,
            )
        with gr.Row(scale=1):
            display_feedback_checkbox = gr.Checkbox(
                value=False,
                label="Show previous feedback",
                interactive=True,
            )
            sorting_of_images = gr.Radio(
                choices=["image_name", "likes", "dislikes"],
                label="Sorting of images",
                value="image_name",
            )
            reload_feedback_button = gr.Button(
                "Reload feedback",
                variant="secondary",
                interactive=True,
                size="sm",
            )
            reloaded_feedback_count = gr.State(value=1)

            def reload_feedback(project_name, reloaded_feedback_count):
                feedback_handler.load_all_feedback_iterations_for_project(project_name)
                reloaded_feedback_count += 1
                gr.Info("Reloaded feedback.", duration=2)
                return reloaded_feedback_count

            reload_feedback_button.click(
                fn=reload_feedback,
                inputs=[project_name, reloaded_feedback_count],
                outputs=[reloaded_feedback_count],
            )

    @gr.render(
        inputs=[
            feedback_iterations,
            columns,
            display_feedback_checkbox,
            sorting_of_images,
            reloaded_feedback_count,
        ]
    )
    def render_images_per_iteration(
        feedback_iterations,
        columns,
        display_feedback_checkbox,
        sorting_of_images,
        reloaded_feedback_count,
    ):
        """
        This function renders the images for each feedback iteration. It is decorated with gr.render
        to allow for dynamic rendering of the images based on the selected feedback iterations.
        - for each feedback_iteration, there is a separate accordion
        - each accordion contains rows of images with the number of columns specified by the user
        - each image is associated with feedback functionality
        """
        if not feedback_iterations:
            gr.Markdown("No feedback iteration selected.")
            return
        for feedback_iteration in feedback_iterations:
            # load the images corresponding to this feedback iteration
            feedback_iteration_images = (
                feedback_handler.load_images_for_feedback_iteration(
                    feedback_iteration, sorting_of_images
                )
            )

            # split images into batches of number of columns
            num_images = len(feedback_iteration_images)
            images_batches = [
                feedback_iteration_images[i : i + columns]
                for i in range(0, num_images, columns)
            ]

            # fill up last batch with Nones to have same number of images in each row
            if len(images_batches[-1]) < columns:
                images_batches[-1] += [None] * (columns - len(images_batches[-1]))

            # render images
            min_width_elements = "10px"
            with gr.Accordion(label=f"Iteration {feedback_iteration}"):
                for batch in images_batches:
                    with gr.Row(variant="compact"):
                        for img in batch:
                            # string of image_name is needed later on, img will be modified by gradio hereafter.
                            img_path = str(img)
                            img_name = img_path.split("/")[-1]
                            # only display image with buttons if it exists
                            element_visible_bool = bool(img)
                            with gr.Column(
                                variant="compact", min_width=min_width_elements
                            ):
                                gr.Image(
                                    value=img,
                                    label=img_name,
                                    show_download_button=True,
                                    show_fullscreen_button=True,
                                    visible=element_visible_bool,
                                    min_width=min_width_elements,
                                    scale=1,
                                )
                                img_textbox = gr.Textbox(
                                    value=img_path, visible=False
                                )  # needed bc gr.render
                                comment = gr.Textbox(
                                    label="Comment",
                                    value="",
                                    visible=element_visible_bool,
                                    min_width=min_width_elements,
                                    scale=1,
                                    interactive=True,
                                )
                                feedback_indicator = gr.Radio(
                                    choices=["Like", "Dislike"],
                                    label="Feedback",
                                    visible=element_visible_bool,
                                )
                                feedback_button = gr.Button(
                                    "Send feedback for this image",
                                    visible=element_visible_bool,
                                    size="sm",
                                    min_width=min_width_elements,
                                    scale=1,
                                    variant="primary",
                                    interactive=False,
                                )

                                # feedback button is only clickable if feedback indicator is changed recently
                                def change_feedback_button_interactivity(
                                    feedback_indicator,
                                    feedback_button,
                                ):
                                    if feedback_indicator:
                                        feedback_button = gr.Button(interactive=True)
                                    else:
                                        feedback_button = gr.Button(interactive=False)

                                    return feedback_button

                                feedback_indicator.change(
                                    fn=change_feedback_button_interactivity,
                                    inputs=[feedback_indicator, feedback_button],
                                    outputs=[feedback_button],
                                )

                                # adjusts gr.State object with feedback details and writes feedback
                                feedback_button.click(
                                    fn=adjust_feedback_details,
                                    inputs=[
                                        img_textbox,
                                        feedback_indicator,
                                        comment,
                                        feedback_details,
                                    ],
                                    outputs=[feedback_details],
                                ).then(
                                    # change feedback button to non-interactive again (avoid double feedback)
                                    fn=lambda: gr.update(interactive=False),
                                    inputs=None,
                                    outputs=feedback_button,
                                )

                                feedback = feedback_handler.get_feedback_per_image(
                                    feedback_iteration=feedback_iteration,
                                    image_name=img_name,
                                )
                                gr.Markdown(
                                    label="Previous Feedback",
                                    value=f"Likes: {feedback['likes']} - Comments: {feedback['comments_liked']}"
                                    if feedback and reloaded_feedback_count > 0
                                    else "",
                                    visible=display_feedback_checkbox
                                    and element_visible_bool,
                                )
                                gr.Markdown(
                                    label="Previous Feedback",
                                    value=f"Dislikes: {feedback['dislikes']} - Comments: {feedback['comments_disliked']}"
                                    if feedback and reloaded_feedback_count > 0
                                    else "",
                                    visible=display_feedback_checkbox
                                    and element_visible_bool,
                                )
