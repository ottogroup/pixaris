from abc import abstractmethod
from typing import Iterator
from PIL import Image


class DataWriter:
    @abstractmethod
    def store_results(
        self,
        eval_set: str,
        run_name: str,
        images: Iterator[Image.Image],
        metrics: dict[str, float],
        args: dict[str, any],
    ) -> None:
        pass
