import time
import json
from typing import Iterable
from PIL import Image
import os
from pixaris.data_writers.base import DataWriter


class LocalDataWriter(DataWriter):
    def store_results(
        self,
        eval_set: str,
        run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
        experiment_folder: str = "local_experiment_tracking",
        global_tracking_file: str = "all_experiment_results.jsonl",
    ):
        """
        Save a collection of images locally under a specified experiment name.
        Args:
            eval_set (str): The name of the evaluation set.
            run_name (str): The name of the experiment. This will be used to create a subfolder where images will be saved.
            images (Iterable[Image.Image]): An iterable collection of PIL Image objects to be saved.
            metrics (dict): The metrics of the experiment to be saved as a JSON file.
            args (dict): The arguments of the experiment to be saved as a JSON file.
            experiment_folder (str, optional): The root folder where the experiment subfolder will be created. Defaults to 'eval_data/generated_images'.
            global_tracking_file (str, optional): The name of the global tracking file. Defaults to 'all_experiment_results.jsonl'.
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        save_dir = os.path.join(experiment_folder, eval_set, run_name + "_" + timestamp)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save each image in the collection
        for image, name in image_name_pairs:
            image.save(os.path.join(save_dir, name))

        # Save the results as JSON files in the experiment subfolder
        with open(os.path.join(save_dir, "results.json"), "w") as f:
            json.dump(metric_values, f)

        # Save the results as JSON files in the experiment subfolder
        with open(os.path.join(save_dir, "args.json"), "w") as f:
            json.dump(args, f)

        # Append the results to the global tracking file
        with open(os.path.join(experiment_folder, global_tracking_file), "a") as f:
            f.write(json.dumps(metric_values) + "\n")
