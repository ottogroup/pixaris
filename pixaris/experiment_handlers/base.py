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
        pass

    def _validate_experiment_run_name(
        self,
        experiment_run_name: str,
    ):
        pass

    @abstractmethod
    def load_projects_and_datasets(
        self,
    ):
        pass

    @abstractmethod
    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
    ):
        pass
