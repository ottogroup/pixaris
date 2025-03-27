import time
import json
from typing import Iterable
from PIL import Image
import os
from pixaris.data_writers.base import DataWriter


class LocalDataWriter(DataWriter):
    def store_results(
        self,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
        local_results_folder: str = "local_results",
        global_tracking_file: str = "all_experiment_results.jsonl",
    ):
        """
        Save a collection of images locally under a specified experiment name.

        :param dataset: The name of the evaluation set.
        :type dataset: str
        :param experiment_run_name: The name of the experiment. This will be used to create a subfolder where images will be saved.
        :type experiment_run_name: str
        :param image_name_pairs: An iterable collection of tuples, where each tuple contains a PIL Image object and its corresponding name.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        :param metric_values: The metrics of the experiment to be saved as a JSON file.
        :type metric_values: dict[str, float]
        :param args: The arguments of the experiment to be saved as a JSON file. If any argument is a PIL Image, it will be saved as an image file.
        :type args: dict[str, any]
        :param local_results_folder: The root folder where the experiment subfolder will be created. Defaults to 'local_results'.
        :type local_results_folder: str, optional
        :param global_tracking_file: The name of the global tracking file. Defaults to 'all_experiment_results.jsonl'.
        :type global_tracking_file: str, optional
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        save_dir = os.path.join(
            local_results_folder, dataset, experiment_run_name + "_" + timestamp
        )

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save each image in the collection
        for image, name in image_name_pairs:
            image.save(
                os.path.join(save_dir, name.split(".")[0] + ".png"),
                "PNG",
                # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts
            )

        # Save images in args
        args_images_dir = os.path.join(save_dir, "args_images")
        if not os.path.exists(args_images_dir):
            os.makedirs(args_images_dir)

        args_copy = {}
        for key, value in args.items():
            if isinstance(value, Image.Image):
                image_path = os.path.join(args_images_dir, key + ".png")
                value.save(image_path, "PNG")
                args_copy[key] = image_path
            else:
                args_copy[key] = value

        # Save the results as JSON files in the experiment subfolder
        with open(os.path.join(save_dir, "results.json"), "w") as f:
            json.dump(metric_values, f)

        # Save the rest of the args as JSON files in the experiment subfolder
        with open(os.path.join(save_dir, "args.json"), "w") as f:
            json.dump(args_copy, f)

        # Append the results to the global tracking file
        with open(os.path.join(local_results_folder, global_tracking_file), "a") as f:
            f.write(json.dumps(metric_values) + "\n")
