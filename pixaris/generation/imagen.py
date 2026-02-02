from typing import List
from pixaris.generation.base import ImageGenerator
from PIL import Image
from google import genai
from google.genai import types

from pixaris.generation.utils import (
    encode_image_to_bytes,
    extract_value_from_list_of_dicts,
)


class ImagenGenerator(ImageGenerator):
    """
    ImagenGenerator is a class that generates images using Google's Imagen 4 API.

    :param gcp_project_id: The Google Cloud Platform project ID.
    :type gcp_project_id: str
    :param gcp_location: The Google Cloud Platform location.
    :type gcp_location: str
    """

    def __init__(self, gcp_project_id: str, gcp_location: str):
        self.gcp_project_id = gcp_project_id
        self.gcp_location = gcp_location

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]],
        args: dict[str, any] = {},
    ):
        """
        Validates the provided dataset and parameters for image generation.

        :param dataset: A list of datasets containing image and mask information.
        :type dataset: List[dict[str, List[dict[str, Image.Image]]]
        :param args: A dictionary containing the parameters to be used for the image generation process.
        :type args: dict[str, any]
        :raises ValueError: If the validation fails for any reason (e.g., missing fields).
        """
        prompt = args.get("prompt", "")

        # Validate dataset
        if not dataset:
            raise ValueError("Dataset cannot be empty.")

        for entry in dataset:
            if not isinstance(entry, dict):
                raise ValueError("Each entry in the dataset must be a dictionary.")

        # Validate parameters, if given
        if not (
            isinstance(prompt, str) or prompt == []
        ):  # temporary fix until generation.base.generate_images_based_on_dataset has correct way of calling image_generator.validate_inputs_and_parameters(dataset, generation_params)
            raise ValueError("Prompt must be a string.")

    def _run_imagen(self, pillow_images: List[dict], prompt: str) -> Image.Image:
        """
        Generates images using the Imagen 4 API with mask-based inpainting.

        :param pillow_images: A list of dictionaries containing pillow images and mask images.
          Example::

          [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}, {'node_name': 'Load Mask Image', 'pillow_image': <PIL.Image>}]
        :type pillow_images: List[dict]
        :param prompt: The prompt describing the desired edit in the masked region.
        :type prompt: str
        :return: The generated image.
        :rtype: PIL.Image.Image
        """

        client = genai.Client(
            vertexai=True, project=self.gcp_project_id, location=self.gcp_location
        )

        # gets input image and mask image from pillow_images
        input_image = extract_value_from_list_of_dicts(
            pillow_images,
            identifying_key="node_name",
            identifying_value="Load Input Image",
            return_key="pillow_image",
        )
        mask_image = extract_value_from_list_of_dicts(
            pillow_images,
            identifying_key="node_name",
            identifying_value="Load Mask Image",
            return_key="pillow_image",
        )

        base_img_bytes = encode_image_to_bytes(input_image)
        mask_img_bytes = encode_image_to_bytes(mask_image)

        edit_config = types.EditImageConfig(
            reference_images=[
                types.RawReferenceImage(reference_id="raw", image=base_img_bytes),
                types.MaskReferenceImage(reference_id="mask", image=mask_img_bytes),
            ],
            prompt=prompt,
            edit_mode="INPAINT",
        )

        response = client.models.edit_image(
            model="imagen-4.0-generate-001", config=edit_config
        )

        # Get the first generated image
        return response.generated_images[0].image

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.

        :param args: A dictionary containing the following keys:
        * pillow_images (List[dict[str, List[dict[str, Image.Image]]]]): A list of dictionaries containing
            pillow images and mask images.
        * prompt (str): The prompt that should be used for the generation.
        :type args: dict[str, any]

        :return: A tuple containing:
        * image (Image.Image): The generated image.
        * image_name (str): The name of the generated image.
        :rtype: tuple[Image.Image, str]
        """
        pillow_images = args.get("pillow_images", [])
        prompt = args.get("prompt", "")

        image = self._run_imagen(pillow_images, prompt)

        # Since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        return image, image_name
