import os
from typing import List
from pixaris.data_loaders.base import DatasetLoader
from PIL import Image


class LocalDatasetLoader(DatasetLoader):
    """
    LocalDatasetLoader is a class for loading datasets from a local directory.
        Upon initialisation, the dataset is loaded from the local directory.

    :param project: The name of the project containing the evaluation set.
    :type project: str
    :param dataset: The name of the evaluation set to load images for.
    :type dataset: str
    :param eval_dir_local: The local directory where evaluation images are saved. Defaults to "local_experiment_inputs".
    :type eval_dir_local: str
    """

    def __init__(
        self,
        project: str,
        dataset: str,
        eval_dir_local: str = "local_experiment_inputs",
    ):
        self.dataset = dataset
        self.project = project
        self.eval_dir_local = eval_dir_local

        # Check if the dataset directory exists
        dataset_path = os.path.join(self.eval_dir_local, self.project, self.dataset)
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(
                f"Dataset directory does not exist: {dataset_path}. "
                f"Please create the directory structure or check your project and dataset names."
            )

        self.image_dirs = [
            name
            for name in os.listdir(dataset_path)
            if os.path.isdir(os.path.join(dataset_path, name))
        ]

        if not self.image_dirs:
            raise ValueError(
                f"No image directories found in {dataset_path}. "
                f"Please ensure the dataset contains subdirectories with images."
            )

    def load_dataset(
        self,
    ) -> List[dict[str, List[dict[str, Image.Image]]]]:
        """Return all images for this dataset."""
        dataset_dir = os.path.join(self.eval_dir_local, self.project, self.dataset)
        image_names = self._retrieve_and_check_dataset_image_names(
            dataset_dir, self.image_dirs
        )
        return self._assemble_dataset(dataset_dir, self.image_dirs, image_names)
