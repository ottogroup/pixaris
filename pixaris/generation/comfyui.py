from typing import List
from pixaris.generation.base import ImageGenerator
from pixaris.generation.comfyui_utils.workflow import ComfyWorkflow
from PIL import Image
import hashlib


class ComfyGenerator(ImageGenerator):
    """
    ComfyGenerator is a class that extends the ImageGenerator class to provide functionality for generating images using a specified workflow and API host.
    It uses the ComfyUI API to generate images based on the provided workflow and input parameters.
    
    :param workflow_apiformat_json: The workflow file in API format.
    :type workflow_apiformat_json: dict
    :param api_host: The API host URL. For local experimenting, put "localhost:8188". 
      There has to be a tunnel to a running comfyUI instance active on port 8188
    :type api_host: str
    """

    def __init__(
        self,
        workflow_apiformat_json: dict,
        api_host: str = "localhost:8188",
    ):
        self.api_host = api_host
        self.workflow_apiformat_json = workflow_apiformat_json
        self.workflow = ComfyWorkflow(
            api_host=self.api_host,
            workflow_apiformat_json=self.workflow_apiformat_json,
        )

    def _get_unique_int_for_image(self, pillow_image: Image.Image) -> int:
        """
        Gets a unique int for an image calculated from image name and hash. This is needed to have a unique
        seed for the experiments but have the same seed for the same image in different experiments.
        
        :param pillow_image: The PIL image.
        :type pillow_image: Image.Image
        :return: The unique integer for the image.
        :rtype: int
        """
        file_name = pillow_image.filename.split("/")[-1].split(".")[0]
        img_bytes = file_name.encode("utf-8") + pillow_image.tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        unique_number = int(img_hash, 16)
        final_seed = (unique_number % 1000000) + 1  # cannot be too big for comfy
        return final_seed

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        Validates the workflow file to ensure that it is in the correct format.
        
        :param dataset: A list of dictionaries containing the images to be loaded.
        :type dataset: List[dict[str, List[dict[str, Image.Image]]]
        :param parameters: A list of dictionaries containing the parameters to be used for the image generation process.
        :type parameters: list[dict[str, str, any]]
        :return: The path to the validated workflow file.
        :rtype: str
        """

        # assert each existing element of generation_params has the keys "node_name", "input", "value"
        for value_info in parameters:
            if not all(key in value_info for key in ["node_name", "input", "value"]):
                raise ValueError(
                    "Each generation_param dictionary should contain the keys 'node_name', 'input', and 'value'."
                )

        # assert the params can be applied to the workflow
        self.workflow.check_if_parameters_are_valid(parameters)

        # assert each element of pillow_images has the keys "pillow_image", "node_name"
        for image_info in dataset:
            image_set = image_info.get("pillow_images", [])
            # check if "node_name", "pillow_image" are keys in image_info
            if not all(
                key in image_dict
                for image_dict in image_set
                for key in ["node_name", "pillow_image"]
            ):
                raise ValueError(
                    "Each pillow_images dictionary should contain the keys 'node_name' and 'pillow_image'."
                )
            # check if all pillow_images are PIL Image objects
            if not all(
                isinstance(image_dict["pillow_image"], Image.Image)
                for image_dict in image_set
            ):
                wrong_types = [
                    type(image_dict["pillow_image"])
                    for image_dict in image_set
                    if not isinstance(image_dict["pillow_image"], Image.Image)
                ]
                raise ValueError(
                    "All pillow_images should be PIL Image objects. Got: ", wrong_types
                )

    def _modify_workflow(
        self,
        pillow_images: list[dict[str, Image.Image]] = [],
        generation_params: list[dict[str, str, any]] = [],
    ) -> ComfyWorkflow:
        """
        Modifies the workflow to generate a single image based on the provided arguments.

        :param pillow_images: A list of dictionaries containing the images to be loaded.
        :type pillow_images: list[dict[str, Image.Image]], optional
        :param generation_params: A list of dictionaries containing the parameters to be used for the image generation process.
        :type generation_params: list[dict[str, str, any]], optional
        :return: The modified workflow.
        :rtype: ComfyWorkflow
        """
        self.workflow.adjust_workflow_to_generate_one_image_only()

        # adjust all generation_params
        if generation_params:
            self.workflow.set_generation_params(generation_params)

        # Load and set images from pillow_images
        for image_info in pillow_images:
            input_image = image_info["pillow_image"]
            self.workflow.set_image(image_info["node_name"], input_image)

        # set seed or warn if it is not being set.
        if self.workflow.check_if_node_exists(
            "KSampler (Efficient) - Generation"
        ):  # not present e.g. in mask workflows
            self.workflow.set_value(
                "KSampler (Efficient) - Generation",
                "seed",
                self._get_unique_int_for_image(pillow_images[0]["pillow_image"]),
            )
        else:
            print(
                "Node 'KSampler (Efficient) - Generation' not found in the workflow. Seed will not be set."
            )

        return self.workflow

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        # Todo: change the docstring format when this issue is closed: https://github.com/sphinx-doc/sphinx/issues/4220
        """
        Generates a single image based on the provided arguments. For this it modifies and executed the workflow to generate the image.
        
        :param args: A dictionary containing the following keys:
        * "workflow_apiformat_json" (dict): The workflow file in JSON apiformat.
        * "pillow_images" (list[dict]): A dict of [str, Image.Image].
          The keys should be Node names
          The values should be the PIL Image objects to be loaded.
          Should look like this::
          
          "pillow_images": [{
          "node_name": "Load Input Image",
          "pillow_image": Image.new("RGB", (100, 100), color="red")}]
        * "generation_params" (list[dict]): A dictionary of generation_params for the image generation process.
          Should look like this::
        
          "generation_params": [{
          "node_name": "GroundingDinoSAMSegment (segment anything)",
          "input": "prompt",
          "value": "model, bag, hair"}]
          
        :rtype args: dict[str, any]
        :return: The generated image and its name
        :rtype: tuple[Image.Image, str]
        """

        assert "workflow_apiformat_json" in args, (
            "The key 'workflow_apiformat_json' is missing."
        )

        pillow_images = args.get("pillow_images", [])
        generation_params = args.get("generation_params", [])

        # since the names should all be the same, we can just take the first.
        image_name = pillow_images[0]["pillow_image"].filename.split("/")[-1]

        self.workflow = self._modify_workflow(
            pillow_images=pillow_images,
            generation_params=generation_params,
        )

        try:
            self.workflow.execute()
            image = self.workflow.get_image("Save Image")[0]
            return image, image_name
        except ConnectionError as e:
            print(
                "Connection Error. Did you forget to build the iap tunnel to ComfyUI on port 8188?"
            )
            raise e
