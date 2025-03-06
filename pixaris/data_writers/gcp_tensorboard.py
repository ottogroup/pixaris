from pixaris.data_writers.base import DataWriter
from pixaris.data_writers.utils import upload_workflow_file_to_bucket
from typing import Iterable
from PIL import Image
from google.cloud import aiplatform
import tensorflow as tf
import os
import shutil
import numpy as np
import json


class GCPTensorboardWriter(DataWriter):
    def __init__(
        self,
        project_id: str,
        location: str,
        bucket_name: str = None,
    ):
        """
        Initializes the GCPTensorboardWriter.
        Args:
            project_id (str): The Google Cloud project_id ID.
            location (str): The Google Cloud location.
            bucket_name (str): The name of the Google Cloud Storage bucket to store the workflow image. If None,
                the workflow image will not be stored in a bucket. Defaults to None.
        """
        self.project_id = project_id
        self.location = location
        self.bucket_name = bucket_name

    def _validate_args(self, args: dict[str, any]):
        # check if all keys are strings
        assert all(
            isinstance(key, str) for key in args.keys()
        ), "All keys must be strings."

        # check if "image_paths" is a list of dictionaries cointaining the correct keys
        if "image_paths" in args:
            image_paths = args["image_paths"]
            assert isinstance(image_paths, list), "image_paths must be a list."
            assert all(
                isinstance(item, dict) for item in image_paths
            ), "Each item in the list must be a dictionary."
            assert all(
                all(key in item for key in ["node_name", "image_path"])
                for item in image_paths
            ), "Each dictionary must contain the keys 'node_name' and 'image_path'."

    def _save_args_entry(self, args: (dict[str, any])):
        """
        Saves all args to TensorBoard.
            if value is a path to an image, save as image
            if value is a path to a json file, save file as text
            if value is a number, save as scalar
            if key is "image_paths", save the images under their node names. Validity checked beforehand
            else save value as json dump
        Args:
            args (dict[str, any]): A dictionary of arguments to be saved to TensorBoard.
        """
        # save all args depending on their type
        for key, value in args.items():
            if isinstance(value, str):
                # check if value is a path to an image
                if value.endswith((".png", ".jpg", ".jpeg")) and os.path.exists(value):
                    tf.summary.image(
                        key,
                        [np.asarray(Image.open(value)) / 255],
                        step=0,
                    )

                # check if value is a path to a json file
                elif value.endswith(".json") and os.path.exists(value):
                    with open(value, "r") as f:
                        json_data = json.load(f)
                        tf.summary.text(key, json.dumps(json_data), step=0)
                # else log as text
                else:
                    tf.summary.text(key, value, step=0)

            # check if value a number
            elif isinstance(value, (int, float)):
                tf.summary.scalar(key, value, step=0)

            # if key is "image_paths", save the images under their node names. Validity checked beforehand.
            elif key == "image_paths":
                for image_path_dict in value:
                    tf.summary.image(
                        image_path_dict["node_name"],
                        [np.asarray(Image.open(image_path_dict["image_path"])) / 255],
                        step=0,
                    )

            # rest is dumped as a json
            else:
                tf.summary.text(key, json.dumps(value), step=0)

    def store_results(
        self,
        eval_set: str,
        run_name: str,
        image_name_pairs: Iterable[tuple[Image.Image, str]],
        metric_values: dict[str, float],
        args: dict[str, any] = {},
    ):
        """
        Stores the results of an evaluation run to TensorBoard.
        Args:
            eval_set (str): The name of the evaluation set.
            run_name (str): The name of the run.
            images (Iterable[Image.Image]): A collection of images to log.
            metrics (dict[str, float]): A dictionary of metric names and their corresponding values.
            args (dict[str, any], optional): args given to the ImageGenerator that generated the images.
        Raises:
            AssertionError: If any value in the metrics dictionary is not a number.
        """
        self._validate_args(args)

        aiplatform.init(
            experiment=eval_set.replace("_", "-"),
            project=self.project_id,
            location=self.location,
            experiment_tensorboard=True,
        )

        # remove old logs and ignore if not exists
        shutil.rmtree(os.path.abspath(f"temp/logs/{eval_set}"), ignore_errors=True)

        with aiplatform.start_run(run_name.replace("_", "-")):
            with tf.summary.create_file_writer(
                os.path.abspath(f"temp/logs/{eval_set}/{run_name}"),
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
                    assert isinstance(
                        value, (int, float)
                    ), f"Value for metric {metric} is not a number."
                    tf.summary.scalar(metric, value, step=0)

                # save all args depending on their type
                print("Logging args")
                self._save_args_entry(args)

                # save workflow image with metadata to bucket
                if self.bucket_name and args["workflow_image_path"]:
                    print("Saving workflow image to bucket")
                    link_to_workflow_in_bucket = upload_workflow_file_to_bucket(
                        project_id=self.project_id,
                        bucket_name=self.bucket_name,
                        eval_set=eval_set,
                        run_name=run_name,
                        local_file_path=args["workflow_image_path"],
                    )
                    tf.summary.text(
                        "link_to_workflow_image", link_to_workflow_in_bucket, step=0
                    )

            aiplatform.upload_tb_log(
                tensorboard_experiment_name=eval_set.replace("_", "-"),
                experiment_display_name=run_name,
                logdir=os.path.abspath(f"temp/logs/{eval_set}"),
            )
