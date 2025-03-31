import os
from pixaris.experiments_tracker.base import ExperimentTracker
import pandas as pd


class LocalExperimentTracker(ExperimentTracker):
    def load_projects_and_datasets(
        self,
        local_results_folder: str = "local_results",
    ):
        """
        Load the projects and datasets from the local results folder.
        Args:
            local_results_folder (str, optional): The root folder where the projects and datasets are located. Defaults to 'eval_data/generated_images'.
        Returns:
            dict: A dictionary containing the projects and datasets. {"project": ["dataset1", "dataset2"]}
        """
        projects = os.listdir(local_results_folder)
        projects.sort()
        project_dict = {}
        for project in projects:
            project_path = os.path.join(local_results_folder, project)
            if os.path.isdir(project_path):
                project_dict[project] = os.listdir(project_path)
        return project_dict

    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
        local_results_folder: str = "local_results",
    ):
        """
        Load the results of an experiment.
        Args:
            project (str): The name of the project.
            dataset (str): The name of the evaluation set.
            local_results_folder (str, optional): The root folder where the experiment subfolder is located. Defaults to 'local_results'.
        Returns:
            pd.DataFrame: The results of the experiment as a DataFrame.
        """
        results_file = os.path.join(
            local_results_folder,
            project,
            dataset,
            "experiment_results.jsonl",
        )

        if os.path.exists(results_file) and os.stat(results_file).st_size > 0:
            try:
                return pd.read_json(results_file, lines=True)
            except ValueError:
                pass
        return pd.DataFrame()
