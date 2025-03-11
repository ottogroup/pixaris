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
    specifally the fill model, which needs an image and a mask as input.
    """

    def __init__(self):
        pass

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, str]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        Validates the provided dataset and parameters for image generation.

        Args:
            dataset (List[dict[str, List[dict[str, str]]]]): A list of datasets containing image and mask information.
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
                    raise ValueError("Each parameter must be a dictionary.")

        pass

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encodes an image file to a base64 string.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: Base64 encoded string representation of the image.
        """
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded_string = base64.b64encode(image_data).decode("utf-8")
        return base64_encoded_string

    def _run_flux(
        self, image_paths: List[dict], generation_params: List[dict]
    ) -> Image.Image:
        """
        Generates images using the Flux API and checks the status until the image is ready.

        Args:
            image_paths (List[dict]): A list of dictionaries containing image paths and mask paths.
                Example: [{'node_name': 'Load Input Image', 'image_path': 'path/to/image.png'}, {'node_name': 'Load Mask Image', 'image_path': 'path/to/mask.png'}]
            generation_params (list[dict]): A list of dictionaries containing generation params.

        Returns:
            PIL.Image.Image: The generated image.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        image_path = image_paths[0]["image_path"]
        mask_path = image_paths[1]["image_path"]

        api_key = os.environ.get("BFL_API_KEY")

        # Set up basis payload
        payload = {
            "image": self._encode_image_to_base64(image_path),
            "mask": self._encode_image_to_base64(mask_path),
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

        Args:
            args (dict[str, any]): A dictionary containing the following keys:
                - image_paths (list[dict]): A list of dictionaries containing image paths and mask paths.
                - generation_params (list[dict]): A list of dictionaries containing generation params.

        Returns:
            tuple[Image.Image, str]: A tuple containing:
                - image (Image.Image): The generated image.
                - image_name (str): The name of the generated image.
        """
        image_paths = args.get("image_paths", [])
        generation_params = args.get("generation_params", [])

        image = self._run_flux(image_paths, generation_params)

        # Since the names should all be the same, we can just take the first.
        image_name = image_paths[0]["image_path"].split("/")[-1]

        return image, image_name
