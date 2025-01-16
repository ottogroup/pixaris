from pixaris.generation.comfyui import ComfyGenerator
from PIL import Image


class ComfyMockGenerator(ComfyGenerator):
    """
    A mock image generator class for ComfyUI.
    Methods
    -------
    generate_single_image(args: dict[str, any]) -> Image.Image:
        returns a single image based on the provided arguments.
        Parameters:
            args (dict[str, any]): A dictionary of arguments.
        Returns:
            Image.Image: The generated image.
        Raises:
            ValueError: If args are invalid.
    """

    def __init__(self, workflow_apiformat_path: str = ""):
        super().__init__(workflow_apiformat_path)

    def generate_single_image(self, args: dict[str, any]) -> Image.Image:
        """
        Returns a single image based on the provided arguments.
        Args:
            args (dict[str, any]): A dictionary containing the arguments for image generation.
                - "image_paths" (list[dict]): A list of dictionaries, each containing an "image_path" key with the path to an image file.
        Returns:
            Image.Image: The first image in "image_paths".
        Raises:
            ValueError: If the arguments are not valid.
        """

        image_paths = args.get("image_paths", [])

        for item in image_paths:
            if item.get("image_path", False):
                return Image.open(item["image_path"])
