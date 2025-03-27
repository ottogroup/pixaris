import os
from typing import List
from pixaris.data_loaders.base import DatasetLoader
from PIL import Image


class LocalDatasetLoader(DatasetLoader):
    """
    LocalDatasetLoader is a class for loading datasets from a local directory. Upon initialisation,
    the dataset is loaded from the local directory.
    Attributes:
        project (str): The name of the project containing the evaluation set.
        dataset (str): The name of the evaluation set to load images for.
        eval_dir_local (str): The local directory where evaluation images are saved. Defaults to "eval_data".
    """

    def __init__(
        self,
        project: str,
        dataset: str,
        eval_dir_local: str = "eval_data",
    ):
        self.dataset = dataset
        self.project = project
        self.eval_dir_local = eval_dir_local
        self.image_dirs = [
            name
            for name in os.listdir(
                os.path.join(self.eval_dir_local, self.project, self.dataset)
            )
            if os.path.isdir(
                os.path.join(self.eval_dir_local, self.project, self.dataset, name)
            )
        ]

    def _retrieve_and_check_dataset_image_names(self):
        """
        Retrieves the names of the images in the evaluation set and checks if they are the same in each image directory.

        Returns:
            list[str]: The names of the images in the evaluation set.

        Raises:
            ValueError: If the names of the images in each image directory are not the same.
        """
        basis_names = os.listdir(
            os.path.join(
                self.eval_dir_local, self.project, self.dataset, self.image_dirs[0]
            )
        )
        for image_dir in self.image_dirs:
            image_names = os.listdir(
                os.path.join(self.eval_dir_local, self.project, self.dataset, image_dir)
            )
            if basis_names != image_names:
                raise ValueError(
                    "The names of the images in each image directory should be the same. {} does not match {}.".format(
                        self.image_dirs[0], image_dir
                    )
                )
        return basis_names

    def load_dataset(
        self,
    ) -> List[dict[str, List[dict[str, Image.Image]]]]:
        """
        Returns all images in the evaluation set as an iterable of dictionaries containing PIL Images.

        Returns:
            List[dict[str, List[dict[str, Image.Image]]]]: The data loaded from the local directory.
                The key will always be "pillow_images"
                The value is a dict mapping node names to PIL Image objects.
                    This dict has a key for each directory in the image_dirs list representing a Node Name.
        """
        image_names = self._retrieve_and_check_dataset_image_names()

        dataset = []
        for image_name in image_names:
            pillow_images = []
            for image_dir in self.image_dirs:
                image_path = os.path.join(
                    self.eval_dir_local,
                    self.project,
                    self.dataset,
                    image_dir,
                    image_name,
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
