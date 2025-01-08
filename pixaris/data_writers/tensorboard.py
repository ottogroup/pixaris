from pixaris.data_writers.base import DataWriter
from typing import Iterable
from PIL import Image
from google.cloud import aiplatform
import tensorflow as tf
import os
import shutil
import numpy as np
import json


class TensorboardWriter(DataWriter):
    def __init__(self, project: str, location: str):
        self.project = project
        self.location = location

    def store_results(
        self,
        eval_set: str,
        run_name: str,
        images: Iterable[Image.Image],
        metrics: dict[str, float],
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
        aiplatform.init(
            experiment=eval_set.replace("_", "-"),
            project=self.project,
            location=self.location,
            experiment_tensorboard=True,
        )

        # remove old logs and ignore if not exists
        shutil.rmtree(os.path.abspath(f"temp/logs/{eval_set}"), ignore_errors=True)

        with aiplatform.start_run(run_name.replace("_", "-")):
            with tf.summary.create_file_writer(
                os.path.abspath(f"temp/logs/{eval_set}/{run_name}"),
            ).as_default():
                print("Logging images")
                for index, image in enumerate(images):
                    tf.summary.image(
                        f"generated_image_{index}.jpg",
                        [np.asarray(image) / 255],
                        step=0,
                    )

                for metric, value in metrics.items():
                    assert isinstance(
                        value, (int, float)
                    ), f"Value for metric {metric} is not a number."
                    tf.summary.scalar(metric, value, step=0)

                tf.summary.text("args", json.dumps(args), step=0)

            aiplatform.upload_tb_log(
                tensorboard_experiment_name=eval_set.replace("_", "-"),
                experiment_display_name=run_name,
                logdir=os.path.abspath(f"temp/logs/{eval_set}"),
            )
