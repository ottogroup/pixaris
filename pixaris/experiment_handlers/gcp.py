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


class GCPExperimentHandler(ExperimentHandler):
    """
    GCPExperimentHandler is a class for storing experiment results in Google Cloud Storage and BigQuery.
    It is also used to retrieve the images for display.

    :param gcp_project_id: The Google Cloud Platform project ID.
    :type gcp_project_id: str
    :param gcp_bq_experiment_dataset: The BigQuery dataset for storing experiment results.
    :type gcp_bq_experiment_dataset: str
    :param gcp_pixaris_bucket_name: The name of the Google Cloud Storage bucket for storing images.
    :type gcp_pixaris_bucket_name: str
    :type ExperimentHandler: _type_
    """

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

        self.project = None
        self.dataset = None
        self.experiment_run_name = None

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
            field_type = self._python_type_to_bq_type(type(value))
            schema.append(
                bigquery.SchemaField(name=key, field_type=field_type, mode="NULLABLE")
            )
        return schema

    def _ensure_unique_experiment_run_name(self) -> str:
        """
        Ensures that the experiment run name is unique by appending a timestamp and random number if necessary.

        :return: A unique experiment run name.
        :rtype: str
        """
        timestamp = datetime.now().strftime("%y%m%d")
        self.experiment_run_name = f"{timestamp}-{self.experiment_run_name}"

        blobs = self.pixaris_bucket.list_blobs(
            prefix=f"results/{self.project}/{self.dataset}"
        )
        for blob in blobs:
            if self.experiment_run_name in blob.name:
                return self.experiment_run_name + datetime.now().strftime("%H%M")
        return self.experiment_run_name

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

    def _upload_to_gcs(self, key: str, value: any) -> str:
        """
        Uploads a file (image or JSON) to Google Cloud Storage and returns its GCS path.

        :param key: The key or name of the file.
        :type key: str
        :param value: The content to upload (PIL Image or dict).
        :type value: any
        :return: The GCS path of the uploaded file.
        :rtype: str
        """
        tmp_path = f"{key}"
        gcs_path = (
            f"results/{self.project}/{self.dataset}/{self.experiment_run_name}/{key}"
        )

        if isinstance(value, Image.Image):
            metadata = PngInfo()
            for metadata_key, metadata_value in value.info.items():
                metadata.add_text(metadata_key, str(metadata_value))
            value.save(tmp_path, pnginfo=metadata)
        elif isinstance(value, dict):
            with open(tmp_path, "w") as f:
                json.dump(value, f)
        else:
            raise ValueError("Unsupported value type for upload.")

        blob = self.pixaris_bucket.blob(gcs_path)
        blob.upload_from_filename(tmp_path)
        os.remove(tmp_path)

        return gcs_path

    def _ensure_table_exists(self, table_ref: str, bigquery_input: dict):
        """
        Ensures that the BigQuery table exists with the correct schema.

        :param table_ref: The reference to the BigQuery table.
        :type table_ref: str
        :param bigquery_input: The dictionary used to generate the schema.
        :type bigquery_input: dict
        """
        schema = self._create_schema_from_dict(bigquery_input)

        try:
            table = self.bigquery_client.get_table(table_ref)
            if table.schema != schema:
                raise ValueError(f"Schema mismatch for table {table_ref}.")
        except Exception:
            table = bigquery.Table(table_ref, schema=schema)
            self.bigquery_client.create_table(table)
            print(f"Created table {table_ref}.")

    def _add_default_metrics(self, bigquery_input: dict):
        """
        Adds default metrics to the BigQuery input dictionary if they are not already present.

        :param bigquery_input: The dictionary to update with default metrics.
        :type bigquery_input: dict
        """
        default_metrics = [
            "llm_reality",
            "llm_similarity",
            "llm_errors",
            "llm_todeloy",
            "iou",
            "hyperparameters",
            "workflow_apiformat_json",
            "workflow_pillow_image",
            "max_parallel_jobs",
        ]
        for metric in default_metrics:
            bigquery_input.setdefault(metric, float(0))

    def _store_experiment_parameters_and_results(
        self,
        metric_values: dict[str, float],
        args: dict[str, any] = {},
    ):
        """
        Stores experiment parameters and results in BigQuery and Google Cloud Storage.

        :param metric_values: A dictionary of metric names and their values.
        :type metric_values: dict[str, float]
        :param args: Additional arguments, such as images or JSON data.
        :type args: dict[str, any]
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        bigquery_input = {
            "timestamp": timestamp,
            "experiment_run_name": self.experiment_run_name,
        }

        for key, value in args.items():
            if isinstance(value, (Image.Image, dict)):  # E.g. for workflow images
                gcp_path = self._upload_to_gcs(key, value)
                bigquery_input[key] = gcp_path
            elif isinstance(value, int):
                bigquery_input[key] = value
            elif isinstance(value, float):
                bigquery_input[key] = value
            else:
                bigquery_input[key] = str(value)

        for key, value in metric_values.items():
            if isinstance(value, (dict)):  # E.g. for Hyperparameters
                gcp_path = self._upload_to_gcs(key, value)
                bigquery_input[key] = gcp_path
            elif isinstance(value, int):
                bigquery_input[key] = value
            elif isinstance(value, float):
                bigquery_input[key] = value
            else:
                bigquery_input[key] = str(value)

        # Ensure default metrics are present
        self._add_default_metrics(bigquery_input)

        # Define table reference
        table_ref = f"{self.gcp_bq_experiment_dataset}.{self.project}_{self.dataset}_experiment_results"

        # Ensure table exists with correct schema
        self._ensure_table_exists(table_ref, bigquery_input)

        # Insert the row into BigQuery
        self.bigquery_client.insert_rows_json(table_ref, [bigquery_input])
        print(f"Inserted row into table {table_ref}.")

    def _store_generated_images(
        self,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
    ):
        """
        Store generated images in the Google Cloud Storage bucket.

        :param image_name_pairs: An iterable of tuples containing PIL Image objects and their corresponding names.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        """

        # Upload each image to the GCS bucket
        for pillow_image, name in image_name_pairs:
            image_path = f"{name}"
            gcp_image_path = f"results/{self.project}/{self.dataset}/{self.experiment_run_name}/{name}"
            pillow_image.save(image_path)
            blob = self.pixaris_bucket.blob(gcp_image_path)
            blob.upload_from_filename(image_path)
            print(f"Uploaded {name} to {gcp_image_path}")
            os.remove(image_path)

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

        self.project = project
        self.dataset = dataset
        self.experiment_run_name = experiment_run_name

        self._validate_args(args)

        self.storage_client = storage.Client(project=self.gcp_project_id)
        self.bigquery_client = bigquery.Client(project=self.gcp_project_id)
        self.pixaris_bucket = self.storage_client.bucket(self.gcp_pixaris_bucket_name)

        self.experiment_run_name = self._ensure_unique_experiment_run_name()

        self._store_generated_images(image_name_pairs)
        self._store_experiment_parameters_and_results(args, metric_values)

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
                    if dataset not in project_dict[project]:
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
