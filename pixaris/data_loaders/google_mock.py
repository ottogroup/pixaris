from typing import Iterable
from pixaris.data_loaders.google import GCPDatasetLoader
import os


class MockGCPDatasetLoader(GCPDatasetLoader):
    def __init__(
        self,
        eval_set: str = "mock",
        eval_dir_local: str = os.path.abspath(os.getcwd() + "/test/test_eval_data"),
        force_download: bool = False,
    ):
        self.eval_set = eval_set
        self.eval_dir_local = eval_dir_local
        self.force_download = force_download
        self.image_dirs = [
            name
            for name in os.listdir(os.path.join(self.eval_dir_local, self.eval_set))
            if os.path.isdir(os.path.join(self.eval_dir_local, self.eval_set, name))
        ]

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
                    Output in this example:
                    [{'Load Object Image': 'eval_data/eval_set/Object/image01.jpeg'}, {'Load Mask Image': 'eval_data/eval_set/Mask/image01.jpeg'}]
        """
        image_names = self._retrieve_and_check_dataset_image_names()

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

            yield {"image_paths": image_paths}
