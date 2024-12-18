from abc import abstractmethod
from typing import Iterator
from PIL import Image


class Storage:
    @abstractmethod
    def store_results(
        self,
        eval_set: str,
        run_name: str,
        images: Iterator[Image.Image],
        metrics: dict[str, float],
        params: dict[str, any],
        artifacts: dict[str, bytes],
        tags: dict[str, str],
    ) -> None:
        pass
