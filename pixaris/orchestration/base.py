from pixaris.data_loaders.base import DatasetLoader
from pixaris.generation.base import ImageGenerator
from pixaris.data_writers.base import DataWriter
from pixaris.utils.helpers import merge_dicts
from pixaris.utils.hyperparameters import (
    expand_hyperparameters,
    generate_hyperparameter_grid,
)
from typing import Iterable
from PIL import Image


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
    # validate inputs
    dataset = data_loader.load_dataset()
    generation_params = args.get("generation_params", [])
    image_generator.validate_inputs_and_parameters(dataset, generation_params)

    generated_images = []
    failed_args = []
    for data in dataset:
        consolidated_args = merge_dicts(args, data)
        try:
            generated_images.append(
                image_generator.generate_single_image(consolidated_args)
            )
        except Exception as e:
            failed_args.append({"error_message": e, "args": args})
            print("WARNING", e, "continuing with next image.")

    # if all generations fail, raise an exception, because something went wrong here :(
    if len(generated_images) == 0:
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


def generate_images_for_hyperparameter_search_based_on_eval_set(
    data_loader: DatasetLoader,
    image_generator: ImageGenerator,
    data_writer: DataWriter,
    args: dict[str, any],
):
    """
    Generates images for hyperparameter search based on the evaluation set.
    This function performs a hyperparameter search by generating images for each
    combination of hyperparameters provided. It validates the hyperparameters,
    generates a grid of hyperparameter combinations, and then generates images
    for each combination using the provided data loader, image generator, and
    data writer.
    Args:
        data_loader (DatasetLoader): The data loader to load the evaluation set.
        image_generator (ImageGenerator): The image generator to generate images.
        data_writer (DataWriter): The data writer to save generated images.
        args (dict[str, any]): A dictionary of arguments, including:
            - "workflow_apiformat_path" (str): The path to the workflow file in API format.
            - "hyperparameters" list(dict): A dictionary of hyperparameters to search.
                each entry should contain the following keys:
                - "node_name" (str): The name of the node to adjust.
                - "input" (str): The input to adjust.
                - "value" (list): A list of values to search. Each value should be a valid input for the node.
            - "run_name" (str): The base name for each run.
    Raises:
        ValueError: If no hyperparameters are provided.
    """
    hyperparameters = args.get("hyperparameters")
    if not hyperparameters:
        raise ValueError("No hyperparameters provided.")

    # check if all parameters are valid
    expanded_hyperparameters = expand_hyperparameters(hyperparameters)
    dataset = data_loader.load_dataset()
    image_generator.validate_inputs_and_parameters(dataset, expanded_hyperparameters)

    # generate images for each hyperparameter combination
    hyperparameter_grid = generate_hyperparameter_grid(hyperparameters)
    for run_number, hyperparameter in enumerate(hyperparameter_grid):
        print(f"Starting run {run_number + 1} of {len(hyperparameter_grid)}")
        old_name = args["run_name"]
        args["run_name"] = f"hs_{old_name}_{run_number}"
        generate_images_based_on_eval_set(
            data_loader=data_loader,
            image_generator=image_generator,
            data_writer=data_writer,
            args=merge_dicts(args, {"generation_params": hyperparameter}),
        )
