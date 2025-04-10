from abc import abstractmethod
from typing import Iterable


class DatasetLoader:
    """When implementing a new Dataset Loader, inherit from this one and implement all the abstract methods."""

    @abstractmethod
    def load_dataset(self) -> Iterable[dict[str, any]]:
        pass
