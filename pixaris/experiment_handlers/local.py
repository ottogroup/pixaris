import json
import os
import time
from typing import Iterable
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from pixaris.experiment_handlers.base import ExperimentHandler
import pandas as pd


class LocalExperimentHandler(ExperimentHandler):
    """
    LocalExperimentHandler is a class that handles the storage and retrieval of experiment results locally.

    :param local_results_folder: The root folder where the experiment subfolder is located. Defaults to 'local_results'.
    :type local_results_folder: str, optional
    """

    def __init__(self, local_results_folder: str = "local_results"):
        """
        Initialize the LocalExperimentHandler.
        Args:
            local_results_folder (str, optional): The root folder where the experiment subfolder is located. Defaults to 'local_results'.
        """
        self.local_results_folder = local_results_folder

    def store_results(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
        dataset_tracking_file_name: str = "experiment_tracking.jsonl",
    ):
        """
        Save a collection of images locally under a specified experiment name.

        :param project: The name of the project. This will be used to create a subfolder where images will be saved.
        :type project: str
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
        :param dataset_tracking_file_name: The name of the tracking file. Defaults to 'experiment_tracking.jsonl'.
        :type dataset_tracking_file_name: str
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        save_dir = os.path.join(
            self.local_results_folder,
            project,
            dataset,
            timestamp + "_" + experiment_run_name,
        )

        os.makedirs(save_dir, exist_ok=True)

        # Save each image in the collection
        if image_name_pairs:
            os.makedirs(os.path.join(save_dir, "generated_images"), exist_ok=True)
        for image, name in image_name_pairs:
            image.save(
                os.path.join(save_dir, "generated_images", name.split(".")[0] + ".png"),
                "PNG",
                # if you switch to JPEG, use quality=95 as input! Otherwise, expect square artifacts
            )

        args_with_files_as_paths = {}
        for key, value in args.items():
            if isinstance(value, Image.Image):
                metadata = PngInfo()
                for metadata_key, metadata_value in value.info.items():
                    metadata.add_text(metadata_key, str(metadata_value))
                image_path = os.path.join(save_dir, key + ".png")
                value.save(image_path, pnginfo=metadata)
                args_with_files_as_paths[key] = image_path
            elif isinstance(value, dict):
                # If the value is a dictionary, save it as a JSON file
                json_path = os.path.join(save_dir, key + ".json")
                with open(json_path, "w") as f:
                    json.dump(value, f)
                args_with_files_as_paths[key] = json_path
            else:
                args_with_files_as_paths[key] = value

        # build experiment tracking info json
        tracking_info = {
            "timestamp": timestamp,
            "experiment_run_name": experiment_run_name,
        }
        tracking_info.update(args_with_files_as_paths)
        tracking_info.update(metric_values)

        # Save the results as JSON files in the experiment subfolder
        with open(os.path.join(save_dir, "args.json"), "w") as f:
            json.dump(tracking_info, f)

        # Append the results to the global tracking file
        with open(
            os.path.join(
                self.local_results_folder, project, dataset, dataset_tracking_file_name
            ),
            "a",
        ) as f:
            f.write(json.dumps(tracking_info) + "\n")

    def load_projects_and_datasets(
        self,
    ):
        """
        Load the projects and datasets from the local results folder.

        :return: A dictionary containing the projects and datasets.
          Example::

          {"project": ["dataset1", "dataset2"]}
        :rtype: dict[str, list[str]]
        """
        projects = os.listdir(self.local_results_folder)
        projects.sort()
        project_dict = {}
        for project in projects:
            project_path = os.path.join(self.local_results_folder, project)
            if os.path.isdir(project_path):
                # list datasets, excluding feedback_iterations folder and feedback_tracking.jsonl
                datasets = os.listdir(project_path)
                datasets = [folder for folder in datasets if "feedback" not in folder]
                project_dict[project] = datasets
        return project_dict

    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
    ) -> pd.DataFrame:
        """
        Load the results of an experiment.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the evaluation set.
        :type dataset: str
        :return: The results of the experiment as a DataFrame.
        :rtype: pd.DataFrame
        """
        results_file = os.path.join(
            self.local_results_folder,
            project,
            dataset,
            "experiment_tracking.jsonl",
        )

        if os.path.exists(results_file) and os.stat(results_file).st_size > 0:
            try:
                return pd.read_json(results_file, lines=True)
            except ValueError:
                pass
        return pd.DataFrame()

    def load_images_for_experiment(
            self,
            project: str,
            dataset: str,
            experiment_run_name: str,
            results_directory: str):
        pass  # todo
