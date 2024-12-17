import os
import shutil
from PIL import Image
from google.cloud import storage
from generation.generation import DatasetLoader
from typing import Iterable


class GCPDatasetLoader(DatasetLoader):
    def __init__(
        self,
        gcp_project_id: str,
        gcp_bucket_name: str,
        object_dir: str = None,
        mask_dir: str = None,
        inspo_dir: str = None,
        eval_dir_local: str = "eval_data",
        force_download: bool = False,
    ):
        self.gcp_project_id = gcp_project_id
        self.bucket_name = gcp_bucket_name
        self.object_dir = object_dir
        self.mask_dir = mask_dir
        self.inspo_dir = inspo_dir
        self.eval_dir_local = eval_dir_local
        self.force_download = force_download
        self.download_eval_images()

    def download_bucket_dir(self, bucket: storage.Bucket, dir_name: str):
        """
        Downloads all files from a specified directory in a Google Cloud Storage bucket to a local directory.
        Args:
            bucket (storage.Bucket): The Google Cloud Storage bucket object.
            dir_name (str): The name of the directory in the bucket to download.
        Raises:
            ValueError: If no files are found in the specified directory in the bucket.
        Returns:
            None
        """

        if os.path.exists(os.path.join(self.eval_dir_local, dir_name)):
            return None
        else:
            os.makedirs(os.path.join(self.eval_dir_local, dir_name))

        blobs = bucket.list_blobs(prefix=f"{dir_name}/")
        if not blobs:
            raise ValueError(
                "No images found in bucket or bucket does not exist. Please double-check gs://{self.bucket_name}/{dir_name}/."
            )

        for blob in blobs:
            filename = blob.name.split("/")[-1]
            if filename:
                print("downloading", filename)
                blob.download_to_filename(
                    os.path.join(self.eval_dir_local, dir_name, filename)
                )

    def download_eval_images(self):
        """
        Downloads evaluation images for a given evaluation set.

        Args:
            eval_dir_local (str): The directory where the images will be saved.
                should be of 'eval_images' or 'original_images'.
                should be defined in constants.py.
            eval_dir_bucket (str): The type of images to download.
                should be either 'eval_images' or 'reference_images'.
                should be defined in constants.py.
            eval_set (str): The name of the evaluation set to download images for.

        Returns:
            None
        """
        storage_client = storage.Client(project=self.gcp_project_id)
        bucket = storage_client.get_bucket(self.bucket_name)

        if self.force_download:
            if os.path.exists(self.eval_dir_local):
                shutil.rmtree(self.eval_dir_local)

        if self.object_dir:
            self.download_bucket_dir(bucket, self.object_dir)

        if self.mask_dir:
            self.download_bucket_dir(bucket, self.mask_dir)

        if self.inspo_dir:
            self.download_bucket_dir(bucket, self.inspo_dir)

    def load_dataset(self) -> Iterable[dict[str, any]]:
        """
        returns all images in the evaluation set as an iterator of dictionaries.

        Returns:
            Iterable[dict[str, any]]: The data loaded from the bucket.
        """
        names = os.listdir(os.path.join(self.eval_dir_local, self.object_dir))
        for name in names:
            datapoint = {}
            if self.object_dir:
                datapoint["input_image"] = Image.open(
                    os.path.join(self.eval_dir_local, self.object_dir, name)
                )
            if self.mask_dir:
                datapoint["mask_image"] = Image.open(
                    os.path.join(self.eval_dir_local, self.mask_dir, name)
                )
            if self.inspo_dir:
                datapoint["inspo_image"] = Image.open(
                    os.path.join(self.eval_dir_local, self.inspo_dir, name)
                )
            yield datapoint
