from abc import abstractmethod
from typing import Iterable


class DatasetLoader:
    @abstractmethod
    def load_dataset(self) -> Iterable[dict[str, any]]:
        pass
