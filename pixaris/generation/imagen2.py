from typing import List
from pixaris.generation.base import ImageGenerator
from PIL import Image
import os
from io import BytesIO
import vertexai
from vertexai.preview.vision_models import Image as GoogleImage
from vertexai.preview.vision_models import ImageGenerationModel


class Imagen2ImageGenerator(ImageGenerator):
    """
    ImagenGenerator is a class that generates images using the Google Gemini API.
    """

    def __init__(self, gcp_project_id: str, gcp_location: str):
        self.gcp_project_id = gcp_project_id
        self.gcp_location = gcp_location

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        Validates the provided dataset and parameters for image generation.

        Args:
            dataset (List[dict[str, List[dict[str, Image.Image]]]]): A list of datasets containing image and mask information.
            parameters (list[dict[str, str, any]]): A list of dictionaries containing generation parameters.

        Raises:
            ValueError: If the validation fails for any reason (e.g., missing fields).
        """
        # Validate dataset
        if not dataset:
            raise ValueError("Dataset cannot be empty.")

        for entry in dataset:
            if not isinstance(entry, dict):
                raise ValueError("Each entry in the dataset must be a dictionary.")

        # Validate parameters, if given
        if parameters:
            for param in parameters:
                if not isinstance(param, dict):
                    raise ValueError("Each parameter must be a dictionary.")  #

    def _encode_image_to_bytes(self, pillow_image: Image.Image) -> bytes:
        """
        Encodes a PIL image to bytes.

        Args:
            pillow_image (Image.Image): The PIL image.

        Returns:
            bytes: Byte representation of the image.
        """
        imgByteArr = BytesIO()
        pillow_image.save(imgByteArr, format=pillow_image.format)
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def _run_imagen(
        self, pillow_images: List[dict], generation_params: List[dict]
    ) -> Image.Image:
        """
        Generates images using the Flux API and checks the status until the image is ready.

        Args:
            pillow_images (List[dict]): A list of dictionaries containing pillow images and mask images.
                Example: [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}, {'node_name': 'Load Mask Image', 'pillow_image': <PIL.Image>}]
            generation_params (list[dict]): A list of dictionaries containing generation params.

        Returns:
            PIL.Image.Image: The generated image.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        vertexai.init(project=self.gcp_project_id, location=self.gcp_location)

        prompt = "A beautiful image of a dog"  # PLACEHOLDER

        input_image_path = "input-image.png"
        mask_image_path = "mask-image.png"
        output_image_path = "output-image.png"

        input_image = pillow_images[0]["pillow_image"]
        input_image.save(input_image_path)

        mask_image = pillow_images[1]["pillow_image"]
        mask_image.save(mask_image_path)

        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        base_img = GoogleImage.load_from_file(location=input_image_path)
        mask_img = GoogleImage.load_from_file(location=mask_image_path)

        images = model.edit_image(
            base_image=base_img,
            mask=mask_img,
            prompt=prompt,
            edit_mode="inpainting-insert",
        )

        images[0].save(output_image_path)
        pillow_image = Image.open(output_image_path)

        os.remove("input-image.png")
        os.remove("mask-image.png")
        os.remove("output-image.png")

        return pillow_image

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.

        Args:
            args (dict[str, any]): A dictionary containing the following keys:
                - pillow_images (list[dict]): A list of dictionaries containing pillow images and mask images.
                - generation_params (list[dict]): A list of dictionaries containing generation params.

        Returns:
            tuple[Image.Image, str]: A tuple containing:
                - image (Image.Image): The generated image.
                - image_name (str): The name of the generated image.
        """
        pillow_images = args.get("pillow_images", [])
        generation_params = args.get("generation_params", [])

        image = self._run_imagen(pillow_images, generation_params)

        # Since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        return image, image_name
