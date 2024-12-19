import os
import shutil
from google.cloud import storage
from google.cloud.storage import transfer_manager
from pixaris.data_loaders.base import DatasetLoader
from typing import Iterable


class GCPDatasetLoader(DatasetLoader):
    """
    GCPDatasetLoader is a class for loading datasets from a Google Cloud Storage bucket.
    Attributes:
        gcp_project_id (str): The Google Cloud Platform project ID.
        gcp_bucket_name (str): The name of the Google Cloud Storage bucket.
        eval_set (str): The name of the evaluation set to download images for.
        inspo_image (str, optional): The path to an inspiration image. Defaults to None.
        eval_dir_local (str): The local directory where evaluation images will be saved. Defaults to "eval_data".
        force_download (bool): Whether to force download the images even if they already exist locally. Defaults to False.
    Methods:
        download_bucket_dir(bucket: storage.Bucket, dir_name: str):
        download_eval_set():
        load_dataset() -> Iterable[dict[str, any]]:
            Returns all images in the evaluation set as an iterator of dictionaries.
    """

    def __init__(
        self,
        gcp_project_id: str,
        gcp_bucket_name: str,
        eval_set: str,
        eval_dir_local: str = "eval_data",
        force_download: bool = False,
    ):
        self.gcp_project_id = gcp_project_id
        self.bucket_name = gcp_bucket_name
        self.eval_set = eval_set
        self.eval_dir_local = eval_dir_local
        self.force_download = force_download
        self.download_eval_set()

        self.image_dirs = [
            name
            for name in os.listdir(os.path.join(self.eval_dir_local, self.eval_set))
            if os.path.isdir(os.path.join(self.eval_dir_local, self.eval_set, name))
        ]

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

        # Create the local directory if it does not exist
        if os.path.exists(os.path.join(self.eval_dir_local, dir_name)):
            return None
        else:
            os.makedirs(os.path.join(self.eval_dir_local, dir_name))

        # List the blobs in the bucket. If no blobs are found, raise an error.
        blobs = bucket.list_blobs(prefix=f"{dir_name}/")
        if not blobs:
            raise ValueError(
                "No images found in bucket or bucket does not exist. Please double-check gs://{self.bucket_name}/{dir_name}/."
            )

        # Download the blobs to the local directory
        blob_names = [blob.name for blob in blobs]
        results = transfer_manager.download_many_to_path(
            bucket,
            blob_names,
            destination_directory=os.path.join(self.eval_dir_local),
        )

        # The results list is either `None` or an exception for each blob.
        for name, result in zip(blob_names, results):
            if isinstance(result, Exception):
                print("Failed to download {} due to exception: {}".format(name, result))
            else:
                print(
                    "Downloaded {} to {}.".format(
                        name, os.path.join(self.eval_dir_local, *name.split("/"))
                    )
                )

    def download_eval_set(self):
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
            if os.path.exists(os.path.join(self.eval_dir_local, self.eval_set)):
                shutil.rmtree(os.path.join(self.eval_dir_local, self.eval_set))

        self.download_bucket_dir(bucket, self.eval_set)

    def _retrieve_and_check_dataset_image_names(self):
        """
        Retrieves the names of the images in the evaluation set and checks if they are the same in each image directory.

        Returns:
            list[str]: The names of the images in the evaluation set.
        """
        basis_names = os.listdir(
            os.path.join(self.eval_dir_local, self.eval_set, self.image_dirs[0])
        )
        for image_dir in self.image_dirs:
            image_names = os.listdir(
                os.path.join(self.eval_dir_local, self.eval_set, image_dir)
            )
            if basis_names != image_names:
                raise ValueError(
                    "The names of the images in each image directory should be the same. {} does not match {}.".format(
                        self.image_dirs[0], image_dir
                    )
                )
        return basis_names

    def load_dataset(self) -> Iterable[dict[str, any]]:
        """
        returns all images in the evaluation set as an iterator of dictionaries.

        Returns:
            Iterable[dict[str, dict]]: The data loaded from the bucket.
                the key will always be "image_paths"
                The value is a dict mapping node names to image file paths.
                    This dict has a key for each directory in the image_dirs list representing a Node Name,
                    and the corresponding value is an image path.
                    The Node Names are generated using the image_dirs name. The folder name is integrated into the Node Name.
                    E.g. the image_dirs list is ['Object', 'Mask'] then the corresponding Node Names will be 'Load Object Image' and 'Load Mask Image'.
                    e.g.  {'Load Object Image': 'eval_data/eval_set/Object/image01.jpeg'}
        """
        image_names = self._retrieve_and_check_dataset_image_names()

        for image_name in image_names:
            image_paths = {}
            for image_dir in self.image_dirs:
                image_paths[f"Load {image_dir} Image"] = os.path.join(
                    self.eval_dir_local, self.eval_set, image_dir, image_name
                )

            yield {"image_paths": image_paths}
