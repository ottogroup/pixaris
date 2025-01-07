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

    failed_args = []

    # TODO: Why and when would yield be beneficial?
    generated_images = []
    for data in dataset:
        args.update(data)
        try:
            result = image_generator.generate_single_image(args)
            generated_images.append(result)
        except Exception as e:
            failed_args.append({"error_message": e, "args": args})
            print("WARNING", e, "continuing with next image.")

    # if all generations fail, raise an exception, because something went wrong here :(
    if len(failed_args) == len(data):
        raise Exception(
            f"Failed to generate images for all {len(data)} images. \nLast error message: {failed_args[-1]['error_message']}"
        )

    print("Generation done.")
    if failed_args:
        print(
            f"Failed to generate images for {len(failed_args)} of {len(data)}. \nFailed arguments: {failed_args}"
        )
    return generated_images


def generate_images_for_hyperparameter_search_based_on_eval_set():
    pass
    # TODO how do we want to call the hyperparameters? We need to distinguish between the args that are passed to workflow, e.g. adjust seed to one, and a set pf generation_params to loop through, e.g. try this workflow with different seeds.
