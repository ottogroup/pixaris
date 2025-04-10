import concurrent.futures
from pixaris.data_loaders.base import DatasetLoader
from pixaris.generation.base import ImageGenerator
from pixaris.experiment_handlers.base import ExperimentHandler
from pixaris.metrics.base import BaseMetric
from pixaris.utils.merge_dicts import merge_dicts
from pixaris.utils.hyperparameters import (
    expand_hyperparameters,
    generate_hyperparameter_grid,
)
from typing import Iterable
from PIL import Image


def generate_image(data, image_generator, args, failed_args):
    """
    Generates a single image based on the provided data and image generator.

    :param data: input data, e.g. a dictionary containing images and masks
    :type data: dict
    :param image_generator: the image generator to use for generating images
    :type image_generator: ImageGenerator
    :param args: additional arguments for image generation. To be set during generation
    :type args: dict
    :param failed_args: list to store failed arguments. Has to exist and be handled outside this function.
    :type failed_args: list
    :return: generated image and name
    :rtype: tuple[PIL.Image.Image, str]
    """
    consolidated_args = merge_dicts(data, args)
    try:
        return image_generator.generate_single_image(consolidated_args)
    except Exception as e:
        failed_args.append({"error_message": str(e), "args": consolidated_args})
        print("WARNING", e)
        print("continuing with next image.")
        return None


def generate_images_based_on_dataset(
    data_loader: DatasetLoader,
    image_generator: ImageGenerator,
    experiment_handler: ExperimentHandler,
    metrics: list[BaseMetric],
    args: dict[str, any],
) -> Iterable[tuple[Image.Image, str]]:
    """
    Generates images based on an evaluation set.
    This function loads a dataset using the provided data loader, generates images
    using the provided image generator, and stores the results using the provided
    experiment handler.
    
    :param data_loader: An instance of DatasetLoader to load the dataset.
    :type data_loader: DatasetLoader
    :param image_generator: An instance of ImageGenerator to generate images.
    :type image_generator: ImageGenerator
    :param experiment_handler: An instance of ExperimentHandler to store the generated images and results.
    :type experiment_handler: ExperimentHandler
    :param metrics: A list of metrics to calculate.
    :type metrics: list[BaseMetric]
    :param args: A dictionary of arguments to be used for image generation and storing results.
    :type args: dict[str, any]
    :return: A list of generated images and names
    :rtype: list[tuple[PIL.Image.Image, str]]
    """

    # Validate inputs
    dataset = data_loader.load_dataset()
    generation_params = args.get("generation_params", [])
    image_generator.validate_inputs_and_parameters(dataset, generation_params)
    experiment_handler._validate_experiment_run_name(args["experiment_run_name"])
    max_parallel_jobs = args.get("max_parallel_jobs", 1)

    generated_image_name_pairs = []
    failed_args = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_jobs) as pool:
        results = list(
            pool.map(
                lambda data: generate_image(data, image_generator, args, failed_args),
                dataset,
            )
        )

    # Filter out None results and create pairs
    for result in results:
        if result is not None:
            generated_image_name_pairs.append(result)

    # If all generations fail, raise an exception
    if len(generated_image_name_pairs) == 0:
        raise ValueError(
            f"Failed to generate images for all {len(dataset)} images. \nLast error message: {failed_args[-1]['error_message']}"
        )

    print("Generation done.")
    if failed_args:
        print(f"Failed to generate images for {len(failed_args)} of {len(dataset)}.")
        print(f"Failed arguments: {failed_args}")

    metric_values = {}
    for metric in metrics:
        metric_values.update(
            metric.calculate([pair[0] for pair in generated_image_name_pairs])
        )

    experiment_handler.store_results(
        project=args["project"],
        dataset=args["dataset"],
        experiment_run_name=args["experiment_run_name"],
        image_name_pairs=generated_image_name_pairs,
        metric_values=metric_values,
        args=args,
    )
    return generated_image_name_pairs


def generate_images_for_hyperparameter_search_based_on_dataset(
    data_loader: DatasetLoader,
    image_generator: ImageGenerator,
    experiment_handler: ExperimentHandler,
    metrics: list[BaseMetric],
    args: dict[str, any],
):
    """
    Generates images for hyperparameter search based on the evaluation set.
    This function performs a hyperparameter search by generating images for each
    combination of hyperparameters provided. It validates the hyperparameters,
    generates a grid of hyperparameter combinations, and then generates images
    for each combination using the provided data loader, image generator, and
    experiment handler.
    
    :param data_loader: The data loader to load the evaluation set.
    :type data_loader: DatasetLoader
    :param image_generator: The image generator to generate images.
    :type image_generator: ImageGenerator
    :param experiment_handler: The experiment handler to save generated images.
    :type experiment_handler: ExperimentHandler
    :param metrics: A list of metrics to calculate.
    :type metrics: list[BaseMetric]
    :param args: A dictionary of arguments, including:
    * "workflow_apiformat_json" (str): The path to the workflow file in API format.
    * "hyperparameters" list(dict): A dictionary of hyperparameters to search.
      each entry should contain the following keys:
        * "node_name" (str): The name of the node to adjust.
        * "input" (str): The input to adjust.
        * "value" (list): A list of values to search. Each value should be a valid input for the node.
    * "experiment_run_name" (str): The base name for each run.
    :type args: dict[str, any]
    :raises ValueError: If no hyperparameters are provided or if the hyperparameters are invalid.
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
        run_args = merge_dicts(args, {"generation_params": hyperparameter})
        run_args["experiment_run_name"] = (
            f"hs-{args['experiment_run_name']}-{run_number}"
        )

        generate_images_based_on_dataset(
            data_loader=data_loader,
            image_generator=image_generator,
            experiment_handler=experiment_handler,
            metrics=metrics,
            args=run_args,
        )
