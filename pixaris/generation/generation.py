from abc import abstractmethod
from typing import Iterable
from PIL import Image


class DatasetLoader:
    @abstractmethod
    def load_dataset(self) -> Iterable[dict[str, any]]:
        pass


class ImageGenerator:
    @abstractmethod
    def generate_single_image(self, args: dict[str, any]) -> Image.Image:
        pass


def generate_images(
    dataset_loader: DatasetLoader, image_generator: ImageGenerator, args: dict[str, any]
) -> Iterable[Image.Image]:
    dataset = dataset_loader.load_dataset()
    for data in dataset:
        args.update(data)
        yield image_generator.generate_single_image(args)
