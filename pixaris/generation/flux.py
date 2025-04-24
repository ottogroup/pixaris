from typing import List
from pixaris.generation.base import ImageGenerator
from PIL import Image
import os
import requests
import base64
from io import BytesIO
import time


class FluxFillGenerator(ImageGenerator):
    """
    FluxFillGenerator is responsible for generating images using the Flux API,
    specifically the fill model, which needs an image and a mask as input.
    """

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

    def _encode_image_to_base64(self, pillow_image: Image.Image) -> str:
        """
        Encodes a PIL image to a base64 string.

        :param pillow_image: The PIL image.
        :type pillow_image: PIL.Image.Image

        :return: Base64 encoded string representation of the image.
        :rtype: str
        """
        buffered = BytesIO()
        # assigning Image format or JPEG as default
        format = pillow_image.format or "JPEG"
        pillow_image.save(buffered, format=format)
        image_data = buffered.getvalue()
        base64_encoded_string = base64.b64encode(image_data).decode("utf-8")
        return base64_encoded_string

    def _run_flux(
        self, pillow_images: List[dict], generation_params: List[dict]
    ) -> Image.Image:
        """
        Generates images using the Flux API and checks the status until the image is ready.

        :param pillow_images: A list of dictionaries containing pillow images and mask images.
          Example:: [{'node_name': 'Load Input Image', 'pillow_image': <PIL.Image>}, {'node_name': 'Load Mask Image', 'pillow_image': <PIL.Image>}]
        :type pillow_images: List[dict]
        :param generation_params: A list of dictionaries containing generation params.
        :type generation_params: list[dict]

        :return: The generated image.
        :rtype: PIL.Image.Image
        """
        input_image = pillow_images[1]["pillow_image"]
        mask_image = pillow_images[0]["pillow_image"]

        api_key = os.environ.get("BFL_API_KEY")

        # Set up basis payload
        payload = {
            "image": self._encode_image_to_base64(input_image),
            "mask": self._encode_image_to_base64(mask_image),
            "prompt": "A beautiful landscape with a sunset",
            "steps": 50,
            "prompt_upsampling": False,
            "seed": 1,
            "guidance": 60,
            "output_format": "jpeg",
            "safety_tolerance": 2,
        }

        # Replace generation parameters in the payload
        for param in generation_params:
            payload[param["node_name"]] = param["value"]

        headers = {"Content-Type": "application/json", "X-Key": api_key}

        # Generate image
        response = requests.post(
            "https://api.us1.bfl.ai/v1/flux-pro-1.0-fill", json=payload, headers=headers
        )
        response.raise_for_status()
        request_id = response.json()["id"]

        # Check image status
        status_url = "https://api.us1.bfl.ai/v1/get_result"

        while True:
            time.sleep(1)
            status_response = requests.get(
                status_url,
                headers={"accept": "application/json", "x-key": api_key},
                params={"id": request_id},
            )
            status_response.raise_for_status()
            result = status_response.json()

            if result["status"] == "Ready":
                image_url = result["result"]["sample"]
                break
            print(f"Status: {result['status']}")

        # Download and return the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        return Image.open(BytesIO(image_response.content))

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
        generation_params = args.get("generation_params", [])

        image = self._run_flux(pillow_images, generation_params)

        # Since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        return image, image_name
