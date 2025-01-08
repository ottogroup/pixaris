from pixaris.data_loaders.base import DatasetLoader
from pixaris.generation.base import ImageGenerator
from pixaris.data_writers.base import DataWriter
from pixaris.utils.helpers import merge_dicts
from typing import Iterable
from PIL import Image


def generate_single_image():
    pass


def generate_images_based_on_eval_set(
    data_loader: DatasetLoader,
    image_generator: ImageGenerator,
    data_writer: DataWriter,
    args: dict[str, any],
) -> Iterable[Image.Image]:
    """
    Generates images based on an evaluation set.
    This function loads a dataset using the provided data loader, generates images
    using the provided image generator, and stores the results using the provided
    data writer.
    Args:
        data_loader (DatasetLoader): An instance of DatasetLoader to load the dataset.
        image_generator (ImageGenerator): An instance of ImageGenerator to generate images.
        data_writer (DataWriter): An instance of DataWriter to store the generated images and results.
        args (dict[str, any]): A dictionary of arguments to be used for image generation and storing results.
    Returns:
        Iterable[Image.Image]: A list of generated images.
    """

    dataset = data_loader.load_dataset()

    # TODO: Why and when would yield be beneficial?
    generated_images = []
    failed_args = []
    for data in dataset:
        consolidated_args = merge_dicts(args, data)
        generated_images.append(
            image_generator.generate_single_image(consolidated_args)
        )
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

    data_writer.store_results(
        eval_set=args["eval_set"],
        run_name=args["run_name"],
        images=generated_images,
        metrics={},  # TODO: change this to calculated metrics
        args=args,
    )
    return generated_images


def generate_images_for_hyperparameter_search_based_on_eval_set():
    pass
    # TODO how do we want to call the hyperparameters? We need to distinguish between the args that are passed to workflow, e.g. adjust seed to one, and a set pf generation_params to loop through, e.g. try this workflow with different seeds.
