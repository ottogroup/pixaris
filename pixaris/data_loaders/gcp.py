import os
import shutil
from google.cloud import storage
from google.cloud.storage import transfer_manager
from pixaris.data_loaders.base import DatasetLoader
from typing import List
from PIL import Image


class GCPDatasetLoader(DatasetLoader):
    """
    GCPDatasetLoader is a class for loading datasets from a Google Cloud Storage bucket. Upon initialisation, the dataset is downloaded to a local directory.
    
    Attributes:
        gcp_project_id (str): The Google Cloud Platform project ID.
        gcp_bucket_name (str): The name of the Google Cloud Storage bucket.
        dataset (str): The name of the evaluation set to download images for.
        eval_dir_local (str): The local directory where evaluation images will be saved. Defaults to "eval_data".
        force_download (bool): Whether to force download the images even if they already exist locally. Defaults to False.
    Methods:
        load_dataset() -> Iterable[dict[str, any]]:
            Returns all images in the evaluation set as an iterator of dictionaries.
    """

    def __init__(
        self,
        gcp_project_id: str,
        gcp_bucket_name: str,
        dataset: str,
        eval_dir_local: str = "eval_data",
        force_download: bool = True,
    ):
        self.gcp_project_id = gcp_project_id
        self.bucket_name = gcp_bucket_name
        self.dataset = dataset
        self.eval_dir_local = eval_dir_local
        os.makedirs(self.eval_dir_local, exist_ok=True)
        self.force_download = force_download
        self.bucket = None
        self.image_dirs = None

    def _download_dataset(self):
        """
        Downloads evaluation images for a given evaluation set.
        """
        storage_client = storage.Client(project=self.gcp_project_id)
        self.bucket = storage_client.get_bucket(self.bucket_name)
        if self.force_download:
            self._verify_bucket_folder_exists()

        # only download if the local directory does not exist or is empty
        if self._decide_if_download_needed():
            self._download_bucket_dir()

        self.image_dirs = [
            name
            for name in os.listdir(os.path.join(self.eval_dir_local, self.dataset))
            if os.path.isdir(os.path.join(self.eval_dir_local, self.dataset, name))
        ]

    def _verify_bucket_folder_exists(self):
        """
        Verifies that the bucket exists and is not empty.

        Raises:
            ValueError: If no files are found in the specified directory in the bucket.
        """
        # List the blobs in the bucket. If no blobs are found, raise an error.
        blobs = list(self.bucket.list_blobs(prefix=f"{self.dataset}/"))
        if not blobs:
            raise ValueError(
                "No images found in bucket or bucket does not exist. Please double-check gs://{self.bucket_name}/{dir_name}/."
            )

    def _decide_if_download_needed(self):
        """
        Decides if the download is necessary based on the force_download attribute and existence of the local directory.
        """
        # delete the local directory if force_download is True
        if self.force_download:
            if os.path.exists(os.path.join(self.eval_dir_local, self.dataset)):
                shutil.rmtree(os.path.join(self.eval_dir_local, self.dataset))

        # Create the local directory if it does not exist
        local_dir = os.path.join(self.eval_dir_local, self.dataset)
        if os.path.exists(local_dir) and len(os.listdir(local_dir)) > 0:
            return False
        else:
            os.makedirs(local_dir, exist_ok=True)
            return True

    def _download_bucket_dir(self):
        """
        Downloads all files from a specified directory in a Google Cloud Storage bucket to a local directory.
        """
        # Download the blobs to the local directory
        blobs = self.bucket.list_blobs(prefix=f"{self.dataset}/")
        blob_names = [
            blob.name for blob in blobs if not blob.name.endswith("/")
        ]  # exclude directories
        results = transfer_manager.download_many_to_path(
            self.bucket,
            blob_names,
            destination_directory=os.path.join(self.eval_dir_local),
            worker_type=transfer_manager.THREAD,
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

    def load_dataset(
        self,
    ) -> List[dict[str, List[dict[str, Image.Image]]]]:
        """
        Returns all images in the evaluation set as an iterator of dictionaries containing PIL Images.

        Returns:
            List[dict[str, List[dict[str, Image.Image]]]]: The data loaded from the bucket.
                The key will always be "pillow_images"
                The value is a dict mapping node names to PIL Image objects.
                    This dict has a key for each directory in the image_dirs list representing a Node Name.
        """
        self._download_dataset()
        image_names = self._retrieve_and_check_dataset_image_names()

        dataset = []
        for image_name in image_names:
            pillow_images = []
            for image_dir in self.image_dirs:
                image_path = os.path.join(
                    self.eval_dir_local, self.dataset, image_dir, image_name
                )
                # Load the image using PIL
                pillow_image = Image.open(image_path)
                pillow_images.append(
                    {
                        "node_name": f"Load {image_dir.capitalize()} Image",
                        "pillow_image": pillow_image,
                    }
                )
            dataset.append({"pillow_images": pillow_images})
        return dataset

    def _retrieve_and_check_dataset_image_names(self):
        """
        Retrieves the names of the images in the evaluation set and checks if they are the same in each image directory.

        Returns:
            list[str]: The names of the images in the evaluation set.

        Raises:
            ValueError: If the names of the images in each image directory are not the same.
        """
        basis_names = os.listdir(
            os.path.join(self.eval_dir_local, self.dataset, self.image_dirs[0])
        )
        for image_dir in self.image_dirs:
            image_names = os.listdir(
                os.path.join(self.eval_dir_local, self.dataset, image_dir)
            )
            if basis_names != image_names:
                raise ValueError(
                    "The names of the images in each image directory should be the same. {} does not match {}.".format(
                        self.image_dirs[0], image_dir
                    )
                )
        return basis_names
