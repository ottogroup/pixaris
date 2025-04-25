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
import gradio as gr
from pixaris.utils.bigquery import ensure_table_exists


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

        if isinstance(value, Image.Image):
            tmp_path = f"{key}.png"
            metadata = PngInfo()
            for metadata_key, metadata_value in value.info.items():
                metadata.add_text(metadata_key, str(metadata_value))
            value.save(tmp_path, pnginfo=metadata)
        elif isinstance(value, dict):
            tmp_path = f"{key}.json"
            with open(tmp_path, "w") as f:
                json.dump(value, f)
        else:
            raise ValueError("Unsupported value type for upload.")

        # upload to bucket
        gcs_path = f"results/{self.project}/{self.dataset}/{self.experiment_run_name}/{tmp_path}"
        blob = self.pixaris_bucket.blob(gcs_path)
        blob.upload_from_filename(tmp_path)
        # put together the clickable link
        clickable_link = f"https://console.cloud.google.com/storage/browser/_details/{self.gcp_pixaris_bucket_name}/{gcs_path}?project={self.gcp_project_id}"
        # cleanup temporary file
        os.remove(tmp_path)
        return clickable_link

    def _add_default_metrics(self, bigquery_input: dict):
        """
        Adds default metrics to the BigQuery input dictionary if they are not already present.

        :param bigquery_input: The dictionary to update with default metrics.
        :type bigquery_input: dict
        """
        default_metrics = {
            "llm_reality": 0.0,
            "llm_similarity": 0.0,
            "llm_errors": 0.0,
            "llm_todeloy": 0.0,
            "iou": 0.0,
            "hyperparameters": "",
            "generation_params": "",
            "workflow_apiformat_json": "",
            "workflow_pillow_image": "",
            "max_parallel_jobs": 0.0,
        }
        for k, v in default_metrics.items():
            bigquery_input.setdefault(k, v)

    def _prepare_additional_pillow_images_upload(
        self, args: dict[str, any], image_name_pairs: Iterable[tuple[Image.Image, str]]
    ):
        """
        Prepares additional pillow images for upload by saving them under their node names in image_name_pairs.
        This function also removes the pillow_images key from args to prevent re-uploading.

        :param args: A dictionary containing additional arguments, including pillow images.
        :type args: dict[str, any]
        :param image_name_pairs: An iterable of tuples containing images and their names.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        """
        # all images in pillow_images are additional inputs by the user, e.g. inspo images. No dataset is in here.
        if pillow_images := args.get("pillow_images"):
            assert isinstance(pillow_images, list), (
                "pillow_images must be a list of dictionaries."
            )

            # each image in pillow_images needs to be saved under an own key in dict for easier saving
            for image_details in pillow_images:
                image_name = (
                    "z_" + image_details["node_name"].replace(" ", "_") + ".png"
                )
                pillow_image = image_details["pillow_image"]
                # save the image under its node_name
                image_name_pairs.append((pillow_image, image_name))

            # remove pillow_images from args so they are not uploaded later on again
            args.pop("pillow_images", None)

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
        ensure_table_exists(
            table_ref=table_ref,
            bigquery_input=bigquery_input,
            bigquery_client=self.bigquery_client,
        )

        # Insert the row into BigQuery
        errors = self.bigquery_client.insert_rows_json(table_ref, [bigquery_input])

        # Check for errors and display warnings to UI
        if errors == []:
            print(f"Inserted row into table {table_ref}.")
        else:
            raise RuntimeError(f"Failed to insert row into table {table_ref}: {errors}")

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
            gcp_image_path = f"results/{self.project}/{self.dataset}/{self.experiment_run_name}/generated_images/{name}"
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
        self.storage_client = storage.Client(project=self.gcp_project_id)
        self.bigquery_client = bigquery.Client(project=self.gcp_project_id)
        self.pixaris_bucket = self.storage_client.bucket(self.gcp_pixaris_bucket_name)

        # set and adjust experiment_run_name with timestamp
        self.experiment_run_name = experiment_run_name
        self.experiment_run_name = self._ensure_unique_experiment_run_name()
        # prevent that args["experiment_run_name"] will overwrite unique experiment_run_name
        args["experiment_run_name"] = self.experiment_run_name

        self._validate_args(args=args)

        # store images that were generated by the generator AND additional input images from args
        self._prepare_additional_pillow_images_upload(
            args=args, image_name_pairs=image_name_pairs
        )

        # upload all content of metric_values and args to bigquery and bucket if applicable
        self._store_experiment_parameters_and_results(
            metric_values=metric_values, args=args
        )

        self._store_generated_images(image_name_pairs=image_name_pairs)

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
                    if (
                        dataset not in project_dict[project]
                        and dataset != "feedback_iterations"
                    ):
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
        Downloads images for a experiment_run_name from GCP bucket to local directory.
        Returns list of local image paths that belong to the experiment_run_name.

        :param project: The name of the project.
        :type project: str
        :param dataset: The name of the dataset.
        :type dataset: str
        :param experiment_run_name: Name of the experiment run.
        :type experiment_run_name: str
        :param results_directory: The local directory to store the downloaded images.
        :type results_directory: str
        :return: List of local image paths.
        :rtype: list[str]
        """
        self.storage_client = storage.Client(project=self.gcp_project_id)
        self.pixaris_bucket = self.storage_client.bucket(self.gcp_pixaris_bucket_name)

        print(f"Downloading images for experiment_run_name {experiment_run_name}...")
        path_in_parent_folder = (
            f"{project}/{dataset}/{experiment_run_name}/generated_images/"
        )
        # list images in bucket/project/dataset/experiment_run_name
        blobs = self.pixaris_bucket.list_blobs(
            prefix=f"results/{path_in_parent_folder}",
        )

        local_image_paths = []
        # download images
        for blob in blobs:
            if blob.name.endswith("/"):
                continue  # directory, skip.
            image_path_local = os.path.join(
                results_directory, blob.name.replace("results/", "")
            )
            local_image_paths.append(image_path_local)

            # download image if not already downloaded
            if not os.path.exists(image_path_local):
                gr.Info(
                    f"Downloading image '{blob.name.split('/')[-1]}'...", duration=1
                )
                os.makedirs(os.path.dirname(image_path_local), exist_ok=True)
                blob.download_to_filename(image_path_local)

        print("Done.")
        local_image_paths.sort()
        return local_image_paths
