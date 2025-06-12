from abc import abstractmethod
from typing import Iterable
from PIL import Image


class ExperimentHandler:
    """When implementing a new Experiment Handler, inherit from this one and implement all the abstract methods."""

    @abstractmethod
    def store_results(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any],
    ) -> None:
        """Persist images, metrics and parameters for an experiment run."""
        pass

    def _validate_experiment_run_name(
        self,
        experiment_run_name: str,
    ):
        """Ensure the experiment run name is valid for storage backends."""
        pass

    @abstractmethod
    def load_projects_and_datasets(
        self,
    ):
        """Return a mapping of projects to their available datasets."""
        pass

    @abstractmethod
    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
    ):
        """Load result records for a given project and dataset."""
        pass

    @abstractmethod
    def load_images_for_experiment(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        local_results_directory: str,
    ):
        """Download images for a specific experiment run to a local folder."""
        pass
