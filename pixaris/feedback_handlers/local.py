import json
import shutil
from pixaris.feedback_handlers.base import FeedbackHandler
import gradio as gr
from datetime import datetime
import os
import pandas as pd


class LocalFeedbackHandler(FeedbackHandler):
    """
    Local feedback handler for Pixaris. This class is used to handle feedback
    iterations locally. It allows for the creation of feedback iterations,
    writing feedback to local storage, and loading feedback data from local
    storage.

    :param project_feedback_dir: Directory where feedback iterations are stored. Default is "feedback_iterations".
    :type project_feedback_dir: str
    :param project_feedback_file: Name of the feedback file. Default is "feedback_tracking.jsonl".
    :type project_feedback_file: str
    :param local_feedback_directory: Local directory for storing feedback data. Default is "local_results".
    :type local_feedback_directory: str
    """

    def __init__(
        self,
        project_feedback_dir: str = "feedback_iterations",
        project_feedback_file: str = "feedback_tracking.jsonl",
        local_feedback_directory: str = "local_results",
    ):
        os.makedirs(local_feedback_directory, exist_ok=True)
        self.local_feedback_directory = local_feedback_directory
        self.project_feedback_dir = project_feedback_dir
        self.project_feedback_file = project_feedback_file
        self.feedback_df = None
        self.feedback_iteration_choices = None
        self.projects = None

    def write_single_feedback(self, feedback: dict) -> None:
        """
        Writes feedback for one image to local feedback storage.

        :param feedback: dict with feedback information. Dict is expected to have the following keys:
        * project: name of the project
        * feedback_iteration: name of the iteration
        * dataset: name of the evaluation set (optional)
        * image_name: name of the image
        * experiment_name: name of the experiment (optional)
        * feedback_indicator: string with feedback value (either "Like", "Dislike", or "Neither")
        * comment: string with feedback comment (optional)
        :type feedback: dict
        """
        # assert non-nullable values are present
        assert all(
            key in feedback.keys()
            for key in [
                "project",
                "feedback_iteration",
                "image_name",
                "feedback_indicator",
            ]
        ), (
            "Missing required feedback keys. Must have 'project', 'feedback_iteration', 'image_name', 'feedback_indicator'"
        )

        # setup row to insert to table
        row_to_insert = {
            "project": feedback["project"],
            "feedback_iteration": feedback["feedback_iteration"],
            "dataset": feedback.get("dataset", ""),
            "image_name": feedback["image_name"],
            "experiment_name": feedback.get("experiment_name", ""),
            "date": datetime.now().isoformat(),
            "comment": feedback.get("comment", ""),
        }

        # determine what to write to feedback columns
        feedback_indicator = feedback["feedback_indicator"]

        if feedback_indicator == "Like":
            row_to_insert["likes"] = 1
            row_to_insert["dislikes"] = 0
        elif feedback_indicator == "Dislike":
            row_to_insert["likes"] = 0
            row_to_insert["dislikes"] = 1
        elif (
            feedback_indicator == "Neither"
        ):  # Is used when uploading images (no feedback given)
            row_to_insert["likes"] = 0
            row_to_insert["dislikes"] = 0
        else:
            raise ValueError(
                "Invalid feedback indicator. Must be 'Like', 'Dislike', or 'Neither'"
            )

        # Construct the directory and file path
        project_dir = os.path.join(
            self.local_feedback_directory,
            feedback["project"],
        )
        os.makedirs(project_dir, exist_ok=True)
        feedback_file_path = os.path.join(project_dir, "feedback_iterations", self.project_feedback_file)

        # Write feedback to the file
        with open(feedback_file_path, "a") as feedback_file:
            feedback_file.write(json.dumps(row_to_insert) + "\n")

        # Display success message
        gr.Info("Feedback saved locally", duration=1)

    def _save_images_to_feedback_iteration_folder(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
    ):
        """
        Copies images from the experiment directory to the feedback directory.

        :param local_image_directory: Path to the directory containing the images for the feedback iteration
        :type local_image_directory: str
        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        """
        # copy the image folder to the feedback directory
        feedback_dir = os.path.join(
            self.local_feedback_directory,
            project,
            self.project_feedback_dir,
            feedback_iteration,
        )
        os.makedirs(feedback_dir, exist_ok=True)
        shutil.copytree(
            local_image_directory,
            feedback_dir,
            dirs_exist_ok=True,
        )

    def _initialise_feedback_iteration_in_table(
        self,
        project: str,
        feedback_iteration: str,
        image_names: list[str],
        dataset: str = None,
        experiment_name: str = None,
    ):
        """
        Initialise feedback iteration locally

        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_names: List of image names to use in the feedback iteration
        :type image_names: list[str]
        :param dataset: Name of the dataset (optional)
        :type dataset: str
        :param experiment_name: Name of the experiment (optional)
        :type experiment_name: str
        """

        # for each image, create the upload entry in feedback table
        for image_name in image_names:
            feedback = {
                "project": project,
                "feedback_iteration": feedback_iteration,
                "dataset": dataset,
                "experiment_name": experiment_name,
                "image_name": image_name,
                "feedback_indicator": "Neither",  # used only for initialisation of feedback iteration
                "comment": "upload",
            }
            self.write_single_feedback(feedback)

    def create_feedback_iteration(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
        date_suffix: str = None,
        dataset: str = "",
        experiment_name: str = "",
    ):
        """
        Saves images in experiment_directorey to a feedback_iteration folder.
        Puts initial entries into local feedback database.

        :param local_image_directory: Path to the directory containing the images
        :type local_image_directory: str
        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_names: List of image names to use in the feedback iteration
        :type image_names: list[str]
        :param dataset: Name of the dataset (optional)
        :type dataset: str
        :param experiment_name: Name of the experiment (optional)
        :type experiment_name: str
        """
        # add date for versioning if not provided
        if not date_suffix:
            date_suffix = datetime.now().strftime("%y%m%d")
        feedback_iteration = f"{date_suffix}_{feedback_iteration}"

        self._save_images_to_feedback_iteration_folder(
            local_image_directory=local_image_directory,
            project=project,
            feedback_iteration=feedback_iteration,
        )

        image_names = os.listdir(local_image_directory)
        self._initialise_feedback_iteration_in_table(
            project=project,
            feedback_iteration=feedback_iteration,
            image_names=image_names,
            dataset=dataset,
            experiment_name=experiment_name,
        )

    def load_projects_list(self) -> list[str]:
        """
        Retrieves list of projects from local storage.

        :return: List of project names
        :rtype: list[str]
        """
        projects = [
            d
            for d in os.listdir(self.local_feedback_directory)
            if os.path.isdir(os.path.join(self.local_feedback_directory, d))
        ]
        projects.sort()
        self.projects = projects

        print(f"Found projects: {projects}")
        return projects

    def load_all_feedback_iterations_for_project(self, project: str) -> None:
        """
        Retrieves feedback data for a project from local storage. Adds paths for location of images in
        local directory to the dataframe. Saves the resulting df to self.feedback_df.
        Saves the list of feedback iterations to self.feedback_iteration_choices.

        :param project: Name of the project
        :type project: str
        """
        print(f"Searching locally for feedback data for project {project}...")
        feedback_file_path = os.path.join(
            self.local_feedback_directory,
            project,
            "feedback_iterations",
            self.project_feedback_file,
        )

        if not os.path.exists(feedback_file_path):
            raise FileNotFoundError(f"No feedback file found at {feedback_file_path}")

        # Load the feedback data from the local JSONL file
        feedback_data = []
        with open(feedback_file_path, "r") as feedback_file:
            for line in feedback_file:
                feedback_data.append(
                    json.loads(line.strip())
                )  # Parse JSONL line into a dictionary

        # Convert the feedback data to a DataFrame
        df = pd.DataFrame(feedback_data)

        # add paths for images to df
        df["image_path_local"] = df.apply(
            lambda row: os.path.join(
                self.local_feedback_directory,
                row["project"],
                self.project_feedback_dir,
                row["feedback_iteration"],
                row["image_name"],
            ),
            axis=1,
        )

        # determine feedback iterations to choose from in this project
        choices = df["feedback_iteration"].unique().tolist()
        choices.sort()

        self.feedback_iteration_choices = choices
        self.feedback_df = df

        print(f"Done. Found feedback iterations: {choices}")

    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
    ) -> list[str]:
        """
        Returns list of local image paths that belong to the feedback iteration.

        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :return: List of local image paths
        :rtype: list[str]
        """
        print(f"Downloading images for feedback iteration {feedback_iteration}...")

        # get relevant data for this feedback iteration
        iteration_df = self.feedback_df.loc[
            self.feedback_df["feedback_iteration"] == feedback_iteration
        ].copy()

        return iteration_df["image_path_local"].tolist()
