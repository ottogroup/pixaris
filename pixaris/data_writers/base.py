from abc import abstractmethod
from typing import Iterable
from PIL import Image


class DataWriter:
    @abstractmethod
    def store_results(
        self,
        eval_set: str,
        run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any],
    ) -> None:
        pass

    def _validate_run_name(
        self,
        run_name: str,
    ):
        pass
