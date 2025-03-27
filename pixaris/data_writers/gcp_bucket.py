from pixaris.data_writers.base import DataWriter
from typing import Iterable
from PIL import Image
import pickle
import numpy as np
from google.cloud import storage
from pixaris.data_writers.gcp_tensorboard import GCPTensorboardWriter


class GCPBucketWriter(DataWriter):
    def __init__(
        self,
        gcp_project_id: str,
        location: str,
        bucket_name: str,
        bucket_results_path: str,
    ):
        """
        Initializes the GCPBucketWriter.
        Args:
            gcp_project_id (str): The Google Cloud project ID.
            location (str): The Google Cloud location.
            bucket_name (str): The name of the Google Cloud Storage bucket to store the workflow image. If None,
                the workflow image will not be stored in a bucket. Defaults to None.
        """
        self.gcp_project_id = gcp_project_id
        self.location = location
        self.bucket_name = bucket_name
        self.bucket_results_path = bucket_results_path

    def _validate_args(self, args: dict[str, any]):
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

    def _save_results(
        self,
        experiment_run_name: str,
        results: pickle,
    ):
        """Saves pickled results to a bucket."""

        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)

        destination_path = f"{self.bucket_results_path}/{experiment_run_name}.pkl"
        blob = bucket.blob(destination_path)
        blob.upload_from_string(results)
        print(
            f"Results are saved to GCP bucket: 'gs://{self.bucket_name}/{destination_path}"
        )
        print(f"path_in_bucket = '{destination_path}'")

    def store_results(
        self,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
    ):
        """
        Stores the pickled results of an evaluation run to Bucket.

        :param dataset: The name of the evaluation set.
        :type dataset: str
        :param experiment_run_name: The name of the run.
        :type experiment_run_name: str
        :param images: A collection of images to log.
        :type images: Iterable[Image.Image]
        :param metrics: A dictionary of metric names and their corresponding values.
        :type metrics: dict[str, float]
        :param args: args given to the ImageGenerator that generated the images.
        :type args: dict[str, any]

        :raises: AssertionError: If any value in the metrics dictionary is not a number.
        """
        self._validate_args(args)
        experiment_run_name = experiment_run_name + str(np.random.randint(99))
        results = {
            "dataset": dataset,
            "experiment_run_name": experiment_run_name,
            "image_name_pairs": image_name_pairs,
            "metric_values": metric_values,
            "args": args,
        }
        pickled_reults = pickle.dumps(results)

        self._save_results(experiment_run_name, pickled_reults)

    def _write_to_gcp_tensorboard(self, results):
        tensorboard_writer = GCPTensorboardWriter(
            gcp_project_id=self.gcp_project_id,
            location=self.location,
            bucket_name=self.bucket_name,
        )

        tensorboard_writer.store_results(
            dataset=results["dataset"],
            experiment_run_name=results["experiment_run_name"],
            image_name_pairs=results["image_name_pairs"],
            metric_values=results["metric_values"],
            args=results["args"],
        )

    def upload_experiment_from_bucket_to_tensorboard(self):
        """
        Uploads experiment results from a Google Cloud Storage bucket to TensorBoard.
        This method retrieves pickled experiment results stored in a specified GCP bucket,
        deserializes them, writes the results to TensorBoard, and then deletes the blobs
        from the bucket to clean up.
        Steps:
        1. Connects to the GCP bucket using the provided bucket name.
        2. Iterates through blobs in the bucket with a specified prefix.
        3. Downloads and unpickles the experiment results from each blob.
        4. Writes the results to TensorBoard using an internal method.
        5. Deletes the processed blobs from the bucket.
        Raises:
            google.cloud.exceptions.GoogleCloudError: If there is an issue accessing the bucket or blobs.
            pickle.UnpicklingError: If there is an error unpickling the downloaded data.
        Note:
            Ensure that the `self.bucket_name` and `self.bucket_results_path` are correctly set
            before calling this method. Also, the `_write_to_gcp_tensorboard` method must be
            implemented to handle the deserialized results appropriately.
        """

        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        for blob in bucket.list_blobs(prefix=self.bucket_results_path):
            blob = bucket.blob(blob.name)
            pickled_results = blob.download_as_string()
            results = pickle.loads(pickled_results)

            self._write_to_gcp_tensorboard(results)

            blob.delete()  # cleanup bucket
