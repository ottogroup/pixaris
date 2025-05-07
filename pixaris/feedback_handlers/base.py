from abc import abstractmethod


class FeedbackHandler:
    feedback_iteration_choices = []

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
        Upload images to GCP bucket and persist initialisation of feedback iteration to BigQuery.

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
        Returns a list of projects.
        :return: List of projects
        :rtype: list[str]
        """
        pass

    @abstractmethod
    def get_feedback_per_image(self, feedback_iteration, image_name) -> dict:
        """
        Get feedback for specific image.
        :param feedback_iteration: Name of the feedback iteration
        :type feedback_iteration: str
        :param image_name: Name of the image
        :type image_name: str
        :return: Dictionary with feedback information for the image. {"likes": int, "dislikes": int}
        :rtype: dict
        """
        pass

    @abstractmethod
    def load_all_feedback_iterations_for_project(
        self,
        project: str,
    ) -> None:
        """
        Loads all feedback data for all feedback iterations for a project.

        :param project: Name of the project
        :type project: str
        """
        pass

    @abstractmethod
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
        pass
