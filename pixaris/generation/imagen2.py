from typing import List
from pixaris.generation.base import ImageGenerator
from PIL import Image
import vertexai
from vertexai.preview.vision_models import Image as GoogleImage
from vertexai.preview.vision_models import ImageGenerationModel

from pixaris.generation.utils import (
    encode_image_to_bytes,
    extract_value_from_list_of_dicts,
)


class Imagen2Generator(ImageGenerator):
    """
    ImagenGenerator is a class that generates images using the Google Gemini API.

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
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ):
        """
        Validates the provided dataset and parameters for image generation.

        :param dataset: A list of datasets containing image and mask information.
        :type dataset: List[dict[str, List[dict[str, Image.Image]]]
        :param parameters: A list of dictionaries containing generation parameters.
        :type parameters: list[dict[str, str, any]]
        :raises ValueError: If the validation fails for any reason (e.g., missing fields).
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
                    raise ValueError("Each parameter must be a dictionary.")

    def _run_imagen(self, pillow_images: List[dict], prompt: str) -> Image.Image:
        """
        Generates images using the Imagen API and checks the status until the image is ready.

        :param pillow_images: A list of dictionaries containing pillow images and mask images.
          Example::

          [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}, {'node_name': 'Load Mask Image', 'pillow_image': <PIL.Image>}]
        :type pillow_images: List[dict]
        :param generation_params: A list of dictionaries containing generation params.
        :type generation_params: list[dict]
        :return: The generated image.
        :rtype: PIL.Image.Image
        """

        vertexai.init(project=self.gcp_project_id, location=self.gcp_location)

        # gets input image and mask image from pillow_images
        input_image = extract_value_from_list_of_dicts(
            pillow_images,
            itentifying_key="node_name",
            identifying_value="Load Input Image",
            return_key="pillow_image",
        )
        mask_image = extract_value_from_list_of_dicts(
            pillow_images,
            itentifying_key="node_name",
            identifying_value="Load Mask Image",
            return_key="pillow_image",
        )

        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        base_img = GoogleImage(encode_image_to_bytes(input_image))
        mask_img = GoogleImage(encode_image_to_bytes(mask_image))

        images = model.edit_image(
            base_image=base_img,
            mask=mask_img,
            prompt=prompt,
            edit_mode="inpainting-insert",
        )

        return images[0]._pil_image

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.

        :param args: A dictionary containing the following keys:
        * pillow_images (list[dict]): A list of dictionaries containing pillow images and mask images.
        * generation_params (list[dict]): A list of dictionaries containing generation params.
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
