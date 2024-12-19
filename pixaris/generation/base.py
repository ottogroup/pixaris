from abc import abstractmethod
from PIL import Image


class ImageGenerator:
    @abstractmethod
    def generate_single_image(self, args: dict[str, any]) -> Image.Image:
        pass
