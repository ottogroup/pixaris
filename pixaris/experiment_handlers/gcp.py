from typing import Iterable
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from pixaris.experiment_handlers.base import ExperimentHandler
import json
import pandas as pd
from google.cloud import bigquery, storage
import os
import time
from datetime import datetime
import numpy as np
import gradio as gr


class GCPExperimentHandler(ExperimentHandler):
    def __init__(
        self,
        gcp_project_id: str,
        gcp_bq_experiment_dataset: str,
        gcp_pixaris_bucket_name: str,
    ):
        self.gcp_project_id = gcp_project_id
        self.gcp_bq_experiment_dataset = gcp_bq_experiment_dataset
        self.gcp_pixaris_bucket_name = gcp_pixaris_bucket_name

        self.storage_client = None
        self.bigquery_client = None
        self.pixaris_bucket = None

    def _store_generated_images(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
    ):
        """
        Store generated images in the Google Cloud Storage bucket.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :param experiment_run_name: The name of the experiment run.
        :type experiment_run_name: str
        :param image_name_pairs: An iterable of tuples containing PIL Image objects and their corresponding names.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        """
        if not os.path.exists("tmp"):
            os.makedirs("tmp")  # tmp = app engine local directory - DONT CHANGE

        # Upload each image to the GCS bucket
        for pillow_image, name in image_name_pairs:
            image_path = f"tmp/{name}"
            gcp_image_path = f"results/{project}/{dataset}/{experiment_run_name}/{name}"
            pillow_image.save(image_path)
            blob = self.pixaris_bucket.blob(gcp_image_path)
            blob.upload_from_filename(image_path)
            print(f"Uploaded {name} to {gcp_image_path}")
            os.remove(image_path)

    def _python_type_to_bq_type(self, python_type):
        """
        Maps a Python data type to a corresponding BigQuery data type.

        :param python_type: The Python data type to map.
        :type python_type: type
        :return: The corresponding BigQuery data type as a string.
        :rtype: str
        """
        type_mapping = {
            str: "STRING",
            int: "INTEGER",
            float: "FLOAT",
            bool: "BOOLEAN",
            bytes: "BYTES",
        }
        return type_mapping.get(
            python_type, "STRING"
        )  # Default to STRING if type is unknown, such as datetime

    def _create_schema_from_dict(self, data_dict):
        """
        Creates a BigQuery schema from a dictionary of data.

        :param data_dict: A dictionary where keys are field names and values are field values.
        :type data_dict: dict
        :return: A list of BigQuery SchemaField objects.
        :rtype: list[bigquery.SchemaField]
        """
        schema = []
        for key, value in data_dict.items():
            field_type = self.__python_type_to_bq_type(type(value))
            schema.append(
                bigquery.SchemaField(name=key, field_type=field_type, mode="NULLABLE")
            )
        return schema

    def _store_experiment_parameters_and_results(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        metric_values: dict[str, float],
        args: dict[str, any] = {},
    ):
        """
        Stores experiment parameters and results in BigQuery and Google Cloud Storage.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :param experiment_run_name: The name of the experiment run.
        :type experiment_run_name: str
        :param metric_values: A dictionary of metric names and their values.
        :type metric_values: dict[str, float]
        :param args: Additional arguments, such as images or JSON data.
        :type args: dict[str, any]
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        bigquery_input = {
            "timestamp": timestamp,
            "experiment_run_name": experiment_run_name,
        }

        for key, value in args.items():
            if isinstance(value, Image.Image):
                metadata = PngInfo()
                for metadata_key, metadata_value in value.info.items():
                    metadata.add_text(metadata_key, str(metadata_value))

                image_path = f"tmp/{key}.png"
                value.save(image_path, pnginfo=metadata)
                gcp_image_path = (
                    f"results/{project}/{dataset}/{experiment_run_name}/{key}.png"
                )
                blob = self.pixaris_bucket.blob(gcp_image_path)
                blob.upload_from_filename(image_path)
                os.remove(image_path)

                bigquery_input[key] = str(blob.name)
            elif isinstance(value, dict):
                json_path = f"tmp/{key}.json"
                with open(json_path, "w") as f:
                    json.dump(value, f)
                gcp_json_path = (
                    f"results/{project}/{dataset}/{experiment_run_name}/{key}.json"
                )
                blob = self.pixaris_bucket.blob(gcp_json_path)
                blob.upload_from_filename(json_path)
                os.remove(json_path)
                bigquery_input[key] = str(blob.name)
            else:
                bigquery_input[key] = str(value)

        for key, value in metric_values.items():
            if isinstance(value, Image.Image):
                metadata = PngInfo()
                for metadata_key, metadata_value in value.info.items():
                    metadata.add_text(metadata_key, str(metadata_value))

                image_path = f"tmp/{key}.png"
                value.save(image_path, pnginfo=metadata)
                gcp_image_path = (
                    f"results/{project}/{dataset}/{experiment_run_name}/{key}.png"
                )
                blob = self.pixaris_bucket.blob(gcp_image_path)
                blob.upload_from_filename(image_path)
                os.remove(image_path)

                bigquery_input[key] = str(blob.name)
            elif isinstance(value, dict):
                json_path = f"tmp/{key}.json"
                with open(json_path, "w") as f:
                    json.dump(value, f)
                gcp_json_path = (
                    f"results/{project}/{dataset}/{experiment_run_name}/{key}.json"
                )
                blob = self.pixaris_bucket.blob(gcp_json_path)
                blob.upload_from_filename(json_path)
                os.remove(json_path)
                bigquery_input[key] = str(blob.name)
            else:
                bigquery_input[key] = str(value)

        # Add more to the input if not existing llm and iou metric
        for metric in [
            "llm_reality",
            "llm_similarity",
            "llm_errors",
            "llm_todeloy",
            "iou",
            "hyperparameters",
            "workflow_apiformat_json",
            "workflow_pillow_image",
            "max_parallel_jobs",
        ]:
            if metric not in bigquery_input:
                bigquery_input[metric] = float(0)

        schema = self.__create_schema_from_dict(bigquery_input)

        # Create table if it doesn't exist with table = dataset + _evaluation_results
        table_ref = (
            f"{self.gcp_bq_experiment_dataset}.{project}_{dataset}_experiment_results"
        )
        try:
            table = self.bigquery_client.get_table(table_ref)
        except Exception:
            # Create the table if it doesn't exist
            table = bigquery.Table(table_ref, schema=schema)
            self.bigquery_client.create_table(table)

            print(f"Created table {table_ref}.")
            self.bigquery_client.insert_rows_json(table_ref, [bigquery_input])
            print(f"Inserted row into table {table_ref}.")
        else:
            print(f"Table {table_ref} already exists.")

            # Check if the schema matches
            if table.schema != schema:
                print(f"Schema mismatch for table {table_ref}. UPDATE THIS CODE LOGIC")
                pass  # TODO: Will break at somepoint, need to add logic to update schema
            else:
                self.bigquery_client.insert_rows_json(table_ref, [bigquery_input])
                print(f"Inserted row into table {table_ref}.")

    def _ensure_unique_experiment_run_name(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
    ) -> str:
        """
        Ensures that the experiment run name is unique by appending a timestamp and random number if necessary.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :param experiment_run_name: The base name of the experiment run.
        :type experiment_run_name: str
        :return: A unique experiment run name.
        :rtype: str
        """
        timestamp = datetime.now().strftime("%y%m%d")
        experiment_run_name = f"{timestamp}-{experiment_run_name}"

        blobs = self.pixaris_bucket.list_blobs(prefix=f"results/{project}/{dataset}")
        for blob in blobs:
            if experiment_run_name in blob.name:
                return experiment_run_name + str(np.random.randint(99))
        return experiment_run_name

    def _validate_args(self, args: dict[str, any]):
        """
        Validates the arguments passed to the experiment handler.

        :param args: A dictionary of arguments to validate.
        :type args: dict[str, any]
        :raises AssertionError: If the arguments do not meet the required structure.
        """
        # check if all keys are strings
        assert all(isinstance(key, str) for key in args.keys()), (
            "All keys must be strings."
        )

        # check if "pillow_images" is a list of dictionaries containing the correct keys
        if "pillow_images" in args:
            pillow_images = args["pillow_images"]
            assert isinstance(pillow_images, list), "pillow_images must be a list."
            assert all(isinstance(item, dict) for item in pillow_images), (
                "Each item in the list must be a dictionary."
            )
            assert all(
                all(key in item for key in ["node_name", "pillow_image"])
                for item in pillow_images
            ), "Each dictionary must contain the keys 'node_name' and 'pillow_image'."

    def store_results(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
    ):
        """
        Stores the results of an experiment, including images, metrics, and parameters.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :param experiment_run_name: The name of the experiment run.
        :type experiment_run_name: str
        :param image_name_pairs: An iterable of tuples containing images and their names.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        :param metric_values: A dictionary of metric names and their values.
        :type metric_values: dict[str, float]
        :param args: Additional arguments, such as images or JSON data.
        :type args: dict[str, any]
        """

        self._validate_args(args)

        self.storage_client = storage.Client(project=self.gcp_project_id)
        self.bigquery_client = bigquery.Client(project=self.gcp_project_id)
        self.pixaris_bucket = self.storage_client.bucket(self.gcp_pixaris_bucket_name)

        experiment_run_name = self.__ensure_unique_experiment_run_name(
            project, dataset, experiment_run_name
        )

        self.__store_generated_images(
            project, dataset, experiment_run_name, image_name_pairs
        )
        self.__store_experiment_parameters_and_results(
            project, dataset, experiment_run_name, args, metric_values
        )

    def load_projects_and_datasets(self) -> dict:
        """
        Loads the projects and datasets available in the Google Cloud Storage bucket.

        :return: A dictionary mapping project names to lists of dataset names.
        :rtype: dict
        """
        self.storage_client = storage.Client(project=self.gcp_project_id)
        self.pixaris_bucket = self.storage_client.bucket(self.gcp_pixaris_bucket_name)

        blobs = self.pixaris_bucket.list_blobs()

        project_dict = {}
        for blob in blobs:
            name = blob.name
            if name.startswith("results/") and name != "results/":
                prefix_removed = name.split("results/")[1]
                parts = prefix_removed.split("/")
                if (
                    len(parts) >= 2
                ):  # Ensure there is at least a project and dataset level
                    project, dataset = parts[0], parts[1]
                    if project not in project_dict and project != "pickled_results":
                        project_dict[project] = []
                    if dataset not in project_dict[project] and dataset != "feedback_iterations":
                        project_dict[project].append(dataset)
        return project_dict

    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
    ) -> pd.DataFrame:
        """
        Loads the results of an experiment from a BigQuery dataset.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :return: The results of the experiment as a pandas DataFrame.
        :rtype: pd.DataFrame
        """
        query = f"""
        SELECT *
        FROM `{self.gcp_bq_experiment_dataset}.{project}_{dataset}_experiment_results`
        """

        self.bigquery_client = bigquery.Client(project=self.gcp_project_id)

        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            return results.to_dataframe()
        except Exception as e:
            raise RuntimeError(f"Failed to load experiment results from BigQuery: {e}")

    def load_images_for_experiment(
        self,
        project: str,
        dataset: str,
        experiment_run_name: str,
        results_directory: str,
    ) -> list[str]:
        """
        Downloads images for a feedback iteration from GCP bucket to local directory.
        Returns list of local image paths that belong to the feedback iteration.

        Args:
            experiment_run_name: str - Name of the experiment run.

        Returns:
            List of local image paths.
        """
        print(f"Downloading images for feedback iteration {experiment_run_name}...")
        path_in_parent_folder = f"{project}/{dataset}/{experiment_run_name}/"
        # list images in bucket/project/dataset/experiment_run_name
        blobs = self.pixaris_bucket.list_blobs(
            prefix=f"results/{path_in_parent_folder}",
        )

        local_image_paths = []
        # download images
        for blob in blobs:
            if blob.name.endswith("/"):
                continue # directory, skip.
            image_path_local = os.path.join(results_directory, blob.name.replace("results/", ""))
            local_image_paths.append(image_path_local)

            # download image if not already downloaded
            if not os.path.exists(image_path_local):
                gr.Info(f"Downloading image '{blob.name.split("/")[-1]}'...", duration=1)
                os.makedirs(os.path.dirname(image_path_local), exist_ok=True)
                blob.download_to_filename(image_path_local)

        print("Done.")
        return local_image_paths
