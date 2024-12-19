from pixaris.data_loaders.base import DatasetLoader
from pixaris.generation.base import ImageGenerator
from typing import Iterable
from PIL import Image


def generate_single_image():
    pass


def generate_images_based_on_eval_set(
    dataset_loader: DatasetLoader, image_generator: ImageGenerator, args: dict[str, any]
) -> Iterable[Image.Image]:
    dataset = dataset_loader.load_dataset()

    # TODO: Why and when would yield be beneficial?
    generated_images = []
    for data in dataset:
        args.update(data)
        generated_images.append(image_generator.generate_single_image(args))

    return generated_images


def generate_images_for_hyperparameters_based_on_eval_set():
    pass
    # TODO how do we want to call the hyperparameters? We need to distinguish between the args that are passed to workflow, e.g. adjust seed to one, and a set pf hyperparameters to loop through, e.g. try this workflow with different seeds.
