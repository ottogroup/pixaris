from abc import abstractmethod
from typing import Iterable, List
import os
from PIL import Image


class DatasetLoader:
    """When implementing a new Dataset Loader, inherit from this one and implement all the abstract methods."""

    @abstractmethod
    def load_dataset(self) -> Iterable[dict[str, any]]:
        pass

    def _retrieve_and_check_dataset_image_names(
        self, dataset_dir: str, image_dirs: List[str]
    ) -> List[str]:
        """Return all image names and verify directory contents match."""

        basis_names = os.listdir(os.path.join(dataset_dir, image_dirs[0]))
        basis_names = [name for name in basis_names if name != ".DS_Store"]
        for image_dir in image_dirs:
            image_names = os.listdir(os.path.join(dataset_dir, image_dir))
            image_names = [name for name in image_names if name != ".DS_Store"]
            if basis_names != image_names:
                raise ValueError(
                    "The names of the images in each image directory should be the same."
                    f" {image_dirs[0]} does not match {image_dir}."
                )
        return basis_names

    def _assemble_dataset(
        self,
        dataset_dir: str,
        image_dirs: List[str],
        image_names: List[str],
    ) -> List[dict[str, List[dict[str, Image.Image]]]]:
        """Build dataset dictionary from local paths."""

        dataset = []
        for image_name in image_names:
            pillow_images = []
            for image_dir in image_dirs:
                image_path = os.path.join(dataset_dir, image_dir, image_name)
                pillow_image = Image.open(image_path)
                pillow_images.append(
                    {
                        "node_name": f"Load {image_dir.capitalize()} Image",
                        "pillow_image": pillow_image,
                    }
                )
            dataset.append({"pillow_images": pillow_images})
        return dataset
