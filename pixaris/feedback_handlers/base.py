from abc import abstractmethod
import pandas as pd
from datetime import datetime


class FeedbackHandler:
    feedback_iteration_choices = []
    feedback_df = pd.DataFrame()

    @abstractmethod
    def write_single_feedback(
        self,
        feedback: dict[str, any],
    ) -> None:
        """
        Writes feedback for one image to the feedback table.

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
        pass

    def _construct_feedback_row_to_insert(self, feedback: dict[str, any]) -> None:
        """
        Constructs a row to insert to the feedback table based on the provided feedback dictionary.

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
            "misc": feedback.get("misc", ""),
        }

        # determine what to write to feedback columns
        feedback_indicator = feedback["feedback_indicator"]

        row_to_insert["likes"] = 0
        row_to_insert["dislikes"] = 0

        if feedback_indicator == "Like":
            row_to_insert["likes"] = 1
        elif feedback_indicator == "Dislike":
            row_to_insert["dislikes"] = 1
        elif (
            feedback_indicator
            != "Neither"  # Neither is used when uploading images (no feedback given)
        ):
            raise ValueError(
                "Invalid feedback indicator. Must be 'Like', 'Dislike', or 'Neither'"
            )
        return row_to_insert

    @abstractmethod
    def create_feedback_iteration(
        self,
        local_image_directory: str,
        project: str,
        feedback_iteration: str,
        date_suffix: str = None,
        dataset: str = None,
        experiment_name: str = None,
    ):
        """
        Creates a feedback iteration, which involves persisting the creation to a feedback table as well as
        save the corresponding images.

        :param images_directory: Path to local directory containing images to upload
        :type images_directory: str
        :param project: Name of the project
        :type project: str
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param date_suffix: Date suffix for versioning. Will be set automatically to today if not provided.
        :type date_suffix: str
        :param dataset: Name of the evaluation dataset (optional)
        :type dataset: str
        :param experiment_name: Name of the experiment (optional)
        :type experiment_name: str
        """
        pass

    @abstractmethod
    def load_projects_list(self) -> list[str]:
        """
        Returns the list of projects.

        :return: List of projects
        :rtype: list[str]
        """
        pass

    def get_feedback_per_image(self, feedback_iteration, image_name) -> dict:
        """
        Get feedback for a specific image.

        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_name: Name of the image
        :type image_name: str
        :return: Dictionary with feedback information for the image with the following format:
         {"likes": int, "dislikes": int, "comments_liked": list, "comments_disliked": list}
        :rtype: dict
        """
        # happens because of "batching" of image to display all images the same size
        if image_name == "None":
            return {
                "likes": 0,
                "dislikes": 0,
                "comments_liked": [],
                "comments_disliked": [],
            }
        else:
            feedback_info_df = self.feedback_df.query(
                f'feedback_iteration == "{feedback_iteration}" and image_name == "{image_name}"'
            ).reset_index(inplace=False)
            feedback_info_dict = feedback_info_df.loc[
                0, ["likes", "dislikes", "comments_liked", "comments_disliked"]
            ].to_dict()
            return feedback_info_dict

    def load_all_feedback_iteration_info_for_project(self, project: str) -> None:
        """
        Retrieves feedback data for a project. Adds paths for location of images in
        local directory to the dataframe. Saves the resulting df to self.feedback_df.
        Saves the list of feedback iterations to self.feedback_iteration_choices.

        :param project: Name of the project
        :type project: str
        """
        feedback_df = self._load_feedback_df(project)
        self.feedback_df = feedback_df

        # determine feedback iterations to choose from in this project
        feedback_iteration_choices = feedback_df["feedback_iteration"].unique().tolist()
        feedback_iteration_choices.sort()
        self.feedback_iteration_choices = feedback_iteration_choices

        print(f"Done. Found feedback iterations: {feedback_iteration_choices}")

    @abstractmethod
    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
        sorting: str = "image_name",
    ) -> list[str]:
        """
        Returns list of local image paths that belong to the feedback iteration. Optionally loads images.

        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param sorting: Sorting option for the images. Can be "image_name", "likes", or "dislikes". Default is "image_name".
        :type sorting: str
        :return: List of local image paths
        :rtype: list[str]
        """
        pass

    def _sort_iteration_df(
        self,
        iteration_df: pd.DataFrame,
        sorting: str = "image_name",
    ) -> pd.DataFrame:
        """
        Sorts the iteration dataframe based on the specified sorting option.

        :param iteration_df: DataFrame containing feedback data for one iteration.
        :type iteration_df: pd.DataFrame
        :param sorting: Sorting option for the images. Can be "image_name", "likes", or "dislikes". Default is "image_name".
        :type sorting: str
        :return: Sorted DataFrame
        :rtype: pd.DataFrame
        """
        needed_columns = ["image_name", "image_path_local", "likes", "dislikes"]
        assert all(column in iteration_df.columns for column in needed_columns), (
            f"Expected columns not found in DataFrame. Expected {needed_columns}, found {iteration_df.columns}"
        )

        if sorting == "image_name":
            sorted_df = iteration_df.sort_values("image_name")
        elif sorting == "likes":
            sorted_df = iteration_df.groupby("image_path_local")[
                ["likes", "dislikes"]
            ].agg("sum")
            sorted_df = sorted_df.sort_values("likes", ascending=False).reset_index()
        elif sorting == "dislikes":
            sorted_df = iteration_df.groupby("image_path_local")[
                ["likes", "dislikes"]
            ].agg("sum")
            sorted_df = sorted_df.sort_values("dislikes", ascending=False).reset_index()
        else:
            raise ValueError(
                "Invalid sorting option. Must be 'alphabetical', 'likes', or 'dislikes'"
            )
        return sorted_df
