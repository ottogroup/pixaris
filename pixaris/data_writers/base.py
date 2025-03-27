from abc import abstractmethod
from typing import Iterable
from PIL import Image


class DataWriter:
    @abstractmethod
    def store_results(
        self,
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
