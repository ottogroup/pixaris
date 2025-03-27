from abc import abstractmethod


class FeedbackHandler:
    @abstractmethod
    def write_single_feedback(
        self,
        feedback: dict[str, any],
    ) -> None:
        """Writes feedback for one image to the feedback table."""
        pass

    @abstractmethod
    def load_projects_list(self) -> list[str]:
        """Returns a list of projects."""
        pass

    @abstractmethod
    def load_all_feedback_iterations_for_project(
        self,
        project: str,
    ) -> None:
        """
        Loads all feedback data for all feedback iterations for a project.

        Args:
            project: str Name of the project.
        """
        pass

    @abstractmethod
    def load_images_for_feedback_iteration(
        self,
        feedback_iteration: str,
    ) -> list[str]:
        """
        Loads all images for a feedback iteration. Reutrns a list of image paths that should be rendered
        for this feedback iteration.

        Args:
            feedback_iteration: str Name of the feedback iteration.

        Returns:
            list[str] List of image paths.
        """
        pass
