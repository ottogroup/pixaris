import os
from typing import List
from pixaris.data_loaders.base import DatasetLoader


class LocalDatasetLoader(DatasetLoader):
    def __init__(
        self,
        eval_set: str,
        eval_dir_local: str = "eval_data",
    ):
        self.eval_set = eval_set
        self.eval_dir_local = eval_dir_local
        self.image_dirs = [
            name
            for name in os.listdir(os.path.join(self.eval_dir_local, self.eval_set))
            if os.path.isdir(os.path.join(self.eval_dir_local, self.eval_set, name))
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

    def load_dataset(
        self,
    ) -> List[dict[str, List[dict[str, str]]]]:
        """
        returns all images in the evaluation set as an iterable of dictionaries.

        Returns:
            List[dict[str, List[dict[str, str]]]]: The data loaded from the bucket.
                the key will always be "image_paths"
                The value is a dict mapping node names to image file paths.
                    This dict has a key for each directory in the image_dirs list representing a Node Name,
                    and the corresponding value is an image path.
                    The Node Names are generated using the image_dirs name. The folder name is integrated into the Node Name.
                    E.g. the image_dirs list is ['object', 'mask'] then the corresponding Node Names will be 'Load Object Image' and 'Load Mask Image'.
                    Output in this example:
                    [{'Load object Image': 'eval_data/eval_set/object/image01.jpeg'}, {'Load Mask Image': 'eval_data/eval_set/mask/image01.jpeg'}]
        """
        image_names = self._retrieve_and_check_dataset_image_names()

        dataset = []
        for image_name in image_names:
            image_paths = []
            for image_dir in self.image_dirs:
                image_paths.append(
                    {
                        "node_name": f"Load {image_dir} Image",
                        "image_path": os.path.join(
                            self.eval_dir_local, self.eval_set, image_dir, image_name
                        ),
                    }
                )
            dataset.append({"image_paths": image_paths})
        return dataset
