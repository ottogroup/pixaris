from typing import List
from pixaris.generation.base import ImageGenerator
from PIL import Image
import os
import requests
import base64
import time


class FluxGenerator(ImageGenerator):
    """
    WIP
    """

    def __init__(
        self,
    ):
        """
        TODO
        """
        pass

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, str]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        TODO
        """
        pass

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encodes an image file to a base64 string.
        Step 1: Read the image file as a byte array.
        Step 2: Encode the byte array to a base64 string.
        :param image_path: Path to the image file
        """
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded_string = base64.b64encode(image_data).decode("utf-8")
        return base64_encoded_string

    def _run_flux(self, image_paths, generation_params):
        image_path = image_paths[0]["image_path"]
        mask_path = image_paths[0]["mask_path"]

        encoded_image = self._encode_image_to_base64(image_path)
        encoded_mask = self._encode_image_to_base64(mask_path)

        prompt = generation_params[0]["prompt"]

        url = "https://api.bfl.ml/v1/flux-pro-1.0-fill"

        headers = {
            "Content-Type": "application/json",
            "X-Key": os.environ.get("BFL_API_KEY"),
        }

        body = {
            "image": encoded_image,
            "mask": encoded_mask,
            "prompt": prompt,
        }

        response = requests.post(url, headers=headers, json=body)

        request_id = response.json()["id"]

        while True:
            time.sleep(2)
            result = requests.get(
                "https://api.bfl.ml/v1/get_result",
                headers={
                    "accept": "application/json",
                    "x-key": os.environ.get("BFL_API_KEY"),
                },
                params={"id": request_id},
            ).json()

            if result["status"] == "Ready":
                print(f"Result: {result['result']['sample']}")
                break
            else:
                print(f"Status: {result['status']}")

        generated_image = "TODO"

        return generated_image

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments.
            args (dict[str, any]): A dictionary containing the following keys:
            - "prompt" (str): The prompt to be used for image generation.
            - "generation_params" (list[dict]): A dictionary of generation_params for the image generation process.
        Returns:
            image (Image.Image): The generated image.
            image_name (str): The name of the generated image.
        """

        image_paths = args.get("image_paths", [])
        generation_params = args.get("generation_params", [])

        # since the names should all be the same, we can just take the first.
        image_name = image_paths[0]["image_path"].split("/")[-1]
        image = self._run_flux(image_paths, generation_params)

        return image, image_name
