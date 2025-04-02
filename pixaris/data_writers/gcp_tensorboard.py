from pixaris.data_writers.base import DataWriter
from pixaris.data_writers.utils import upload_workflow_file_to_bucket
from typing import Iterable
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from google.api_core.exceptions import AlreadyExists
from google.cloud import aiplatform
import tensorflow as tf
import os
import shutil
from datetime import datetime
import numpy as np
import json
import re


class GCPTensorboardWriter(DataWriter):
    def __init__(
        self,
        gcp_project_id: str,
        location: str,
        bucket_name: str = None,
    ):
        """
        Initializes the GCPTensorboardWriter.

        :param gcp_project_id: The Google Cloud project ID.
        :type gcp_project_id: str
        :param location: The Google Cloud location.
        :type location: str
        :param bucket_name: The name of the Google Cloud Storage bucket to store the workflow image. If None, the workflow image will not be stored in a bucket. Defaults to None.
        :type bucket_name: str, optional
        """
        self.gcp_project_id = gcp_project_id
        self.location = location
        self.bucket_name = bucket_name

    def _validate_experiment_run_name(
        self,
        experiment_run_name: str,
    ):
        # assert experiment_run_name adheres to tensorboard rules
        assert re.match(r"[a-z0-9][a-z0-9-]{0,127}", experiment_run_name), (
            "experiment_run_name must adhere to regex [a-z0-9][a-z0-9-]{0,127} - so only lowercase letters, numbers and '-' are allowed, max length 128"
        )

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

    def _save_args_entry(self, args: (dict[str, any])):
        """
        Saves all args to TensorBoard.
            if value is a Pillow image, save as image
            if value is a dictionary, save as text
            if value is a number, save as scalar
            if key is "pillow_images", save the images under their node names. Validity checked beforehand
            else save value as json dump

        :param args: A dictionary of arguments to be saved to TensorBoard.
        :type args: dict[str, any]
        """
        # save all args depending on their type
        for key, value in args.items():
            if isinstance(value, Image.Image):
                tf.summary.image(
                    key,
                    [np.asarray(value) / 255],
                    step=0,
                )

            elif isinstance(value, dict):
                tf.summary.text(key, json.dumps(value), step=0)

            elif isinstance(value, (int, float)):
                tf.summary.scalar(key, value, step=0)

            elif key == "pillow_images":
                for pillow_image_dict in value:
                    tf.summary.image(
                        pillow_image_dict["node_name"],
                        [np.asarray(pillow_image_dict["pillow_image"]) / 255],
                        step=0,
                    )

            else:
                tf.summary.text(key, json.dumps(value), step=0)

    def _save_workflow_image_to_bucket(
        self, args: dict[str, any], dataset: str, experiment_run_name: str
    ):
        """Saves the workflow image to a bucket, keeping the metadata."""

        workflow_pillow_image = args["workflow_pillow_image"]

        workflow_image_path = os.path.abspath(
            f"temp/logs/{dataset}/{experiment_run_name}/workflow_image.png"
        )
        metadata = PngInfo()
        for key, value in workflow_pillow_image.info.items():
            metadata.add_text(key, str(value))
        workflow_pillow_image.save(workflow_image_path, pnginfo=metadata)
        link_to_workflow_in_bucket = upload_workflow_file_to_bucket(
            gcp_project_id=self.gcp_project_id,
            bucket_name=self.bucket_name,
            dataset=dataset,
            experiment_run_name=experiment_run_name,
            local_file_path=workflow_image_path,
        )
        return link_to_workflow_in_bucket

    def store_results(
        self,
        dataset: str,
        experiment_run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
        project: str = "",
    ):
        """
        Stores the results of an evaluation run to TensorBoard.

        :param dataset: The name of the evaluation set.
        :type dataset: str
        :param experiment_run_name: The name of the run.
        :type experiment_run_name: str
        :param image_name_pairs: A collection of image and name pairs to log.
        :type image_name_pairs: Iterable[tuple[Image.Image, str]]
        :param metric_values: A dictionary of metric names and their corresponding values.
        :type metric_values: dict[str, float]
        :param args: Arguments given to the ImageGenerator that generated the images. Defaults to an empty dictionary.
        :type args: dict[str, any], optional
        :raises AssertionError: If any value in the metrics dictionary is not a number.
        """
        self._validate_args(args)

        aiplatform.init(
            experiment=dataset.replace("_", "-"),
            project=self.gcp_project_id,
            location=self.location,
            experiment_tensorboard=True,
        )

        # remove old logs
        shutil.rmtree(os.path.abspath(f"temp/logs/{dataset}"), ignore_errors=True)

        # add date to experiment_run_name in format YYMMDD-experiment_run_name
        experiment_run_name = (
            f"{datetime.now().strftime('%y%m%d')}-{experiment_run_name}"
        )

        # handle run name if it already exists in dataset
        try:
            aiplatform_run = aiplatform.start_run(experiment_run_name)
        except Exception as e:
            if type(e) is AlreadyExists:
                print(
                    f"Run name {experiment_run_name} already exists in experiment {dataset}. Adding random number."
                )
                experiment_run_name = experiment_run_name + str(np.random.randint(99))
                print(f"New run name: {experiment_run_name}. Continuing.")
                aiplatform_run = aiplatform.start_run(experiment_run_name)
            else:
                raise e

        with aiplatform_run:
            with tf.summary.create_file_writer(
                os.path.abspath(f"temp/logs/{dataset}/{experiment_run_name}"),
            ).as_default():
                # save generated images
                print("Logging generated images")
                for image, name in image_name_pairs:
                    tf.summary.image(
                        name,
                        [np.asarray(image) / 255],
                        step=0,
                    )

                # save metrics
                print("Logging metrics")
                for metric, value in metric_values.items():
                    assert isinstance(value, (int, float)), (
                        f"Value for metric {metric} is not a number."
                    )
                    tf.summary.scalar(metric, value, step=0)

                # save all args depending on their type
                print("Logging args")
                self._save_args_entry(args)

                # save workflow image with metadata to bucket
                if "workflow_pillow_image" in args and self.bucket_name:
                    print("Saving workflow image to bucket")
                    # Save the workflow image locally before uploading
                    link_to_workflow_in_bucket = self._save_workflow_image_to_bucket(
                        args=args,
                        dataset=dataset,
                        experiment_run_name=experiment_run_name,
                    )
                    tf.summary.text(
                        "link_to_workflow_image", link_to_workflow_in_bucket, step=0
                    )

            aiplatform.upload_tb_log(
                tensorboard_experiment_name=dataset.replace("_", "-"),
                experiment_display_name=experiment_run_name,
                logdir=os.path.abspath(f"temp/logs/{dataset}"),
            )
