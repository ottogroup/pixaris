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
        """Create directories and initialise local feedback storage."""
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
        row_to_insert = self._construct_feedback_row_to_insert(feedback)

        # Construct the directory and file path
        project_dir = os.path.join(
            self.local_feedback_directory,
            feedback["project"],
        )
        os.makedirs(project_dir, exist_ok=True)
        feedback_file_path = os.path.join(
            project_dir, "feedback_iterations", self.project_feedback_file
        )

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
        Initialise feedback iteration locally in tracking table.

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

    def _load_feedback_df(self, project: str) -> pd.DataFrame:
        """
        Retrieves feedback data for a project from local storage. Adds paths for location of images in
        local directory to the dataframe.
        :param project: Name of the project
        :type project: str
        :return: DataFrame containing feedback data
        :rtype: pd.DataFrame
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
                # Parse JSONL line into a dictionary
                feedback_data.append(json.loads(line.strip()))

        # Convert the feedback data to a DataFrame
        feedback_df = pd.DataFrame(feedback_data)

        # add local paths for images to feedback_df
        feedback_df["image_path_local"] = feedback_df.apply(
            lambda row: os.path.join(
                self.local_feedback_directory,
                row["project"],
                self.project_feedback_dir,
                row["feedback_iteration"],
                row["image_name"],
            ),
            axis=1,
        )

        # sum up likes and dislikes, split comments into liked and disliked
        feedback_df = (
            feedback_df.groupby(["project", "feedback_iteration", "image_name"])
            .agg(
                likes=("likes", lambda x: (x == 1).sum()),
                dislikes=("dislikes", lambda x: (x == 1).sum()),
                comments_liked=(
                    "comment",
                    lambda x: list(
                        x[(feedback_df["likes"] == 1) & (~x.isin(["", " "]))]
                    ),
                ),
                comments_disliked=(
                    "comment",
                    lambda x: list(
                        x[(feedback_df["dislikes"] == 1) & (~x.isin(["", " "]))]
                    ),
                ),
                image_path_local=("image_path_local", "first"),
            )
            .reset_index()
        )
        return feedback_df

    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
        sorting: str = "image_name",
    ) -> list[str]:
        """
        Returns list of local image paths that belong to the feedback iteration.

        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param sorting: Sorting option for the images. Can be "image_name", "likes", or "dislikes". Default is "image_name".
        :type sorting: str
        :return: List of local image paths
        :rtype: list[str]
        """
        print(f"Loading images for feedback iteration {feedback_iteration}...")

        # get relevant data for this feedback iteration
        iteration_df = self.feedback_df.loc[
            # only this feedback iteration
            self.feedback_df["feedback_iteration"] == feedback_iteration
        ].copy()

        # sort images according to user preference
        sorted_df = self._sort_iteration_df(
            iteration_df=iteration_df,
            sorting=sorting,
        )
        # deduplicate image paths
        image_paths_local = sorted_df["image_path_local"].unique().tolist()
        return image_paths_local
