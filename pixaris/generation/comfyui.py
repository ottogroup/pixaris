from typing import List
from pixaris.generation.base import ImageGenerator
from pixaris.generation.comfyui_utils.workflow import ComfyWorkflow
from PIL import Image
import hashlib
import os


class ComfyGenerator(ImageGenerator):
    """
    ComfyGenerator is a class that extends the ImageGenerator class to provide functionality for generating images using a specified workflow and API host.
    Methods:
        __init__(api_host: str):
            Initializes the ComfyGenerator with the specified parameters.
        _get_unique_int_for_image(img: Image.Image) -> int:
            Gets the hash of an image to generate a unique seed for experiments.
        run_workflow(workflow_apiformat_path: str, image_paths: dict[str, str], generation_params: list[dict] = []) -> Image:
        generate_single_image(args: dict[str, any]) -> Image.Image:
            Generates a single image using the specified arguments.
    """

    def __init__(
        self,
        workflow_apiformat_path: str,
        api_host: str = "localhost:8188",
    ):
        """
        api_host (str): The API host URL. For local experimenting, put "localhost:8188".
        """
        self.api_host = api_host
        self.workflow_apiformat_path = workflow_apiformat_path
        self.workflow = ComfyWorkflow(
            api_host=self.api_host,
            workflow_file_url=self.workflow_apiformat_path,
        )

    def _get_unique_int_for_image(self, img_path: str) -> int:
        """
        Gets a unique int for an image calculated from image name and hash. This is needed to have a unique
        seed for the experiments but have the same seed for the same image in different experiments.
        Args:
            img_path (str): The path to the image.
        Returns:
            int: The unique integer for the image.
        """
        img = Image.open(img_path)
        file_name = os.path.basename(img_path)
        img_bytes = file_name.encode("utf-8") + img.tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        unique_number = int(img_hash, 16)
        final_seed = (unique_number % 1000000) + 1  # cannot be too big for comfy
        return final_seed

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, str]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        Validates the workflow file to ensure that it is in the correct format.
        Args:
            workflow_apiformat_path (str): The path to the workflow file.
        Returns:
            str: The path to the validated workflow file.
        """

        # assert each existing element of generation_params has the keys "node_name", "input", "value"
        for value_info in parameters:
            if not all(key in value_info for key in ["node_name", "input", "value"]):
                raise ValueError(
                    "Each generation_param dictionary should contain the keys 'node_name', 'input', and 'value'."
                )

        # assert the params can be applied to the workflow
        self.workflow.check_if_parameters_are_valid(parameters)

        # assert each element of image_paths has the keys "image_path", "node_name", and image paths are strings
        for image_info in dataset:
            image_set = image_info.get("image_paths", [])
            # check if "node_name", "image_path" are keys in image_info
            if not all(
                key in image_dict
                for image_dict in image_set
                for key in ["node_name", "image_path"]
            ):
                raise ValueError(
                    "Each image_paths dictionary should contain the keys 'node_name' and 'image_path'."
                )
            # check if all image_paths are strings
            if not all(
                isinstance(image_dict["image_path"], str) for image_dict in image_set
            ):
                wrong_types = [
                    type(image_dict["image_path"])
                    for image_dict in image_set
                    if not isinstance(image_dict["image_path"], str)
                ]
                raise ValueError(
                    "All image_paths should be strings. Got: ", wrong_types
                )
            # check if all image_paths are valid paths
            if not all(
                os.path.exists(image_dict["image_path"]) for image_dict in image_set
            ):
                raise ValueError(
                    f"All image_paths should be valid paths. These paths do not exist: {
                        [
                            image_dict["image_path"]
                            for image_dict in image_set
                            if not os.path.exists(image_dict["image_path"])
                        ]
                    }"
                )

    def _modify_workflow(
        self,
        image_paths: list[dict[str, str]] = [],
        generation_params: list[dict[str, str, any]] = [],
    ):
        self.workflow.adjust_workflow_to_generate_one_image_only()

        # adjust all generation_params
        if generation_params:
            self.workflow.set_generation_params(generation_params)

        # Load and set images from image_paths
        if (
            self.workflow.count_node_class_occurances(node_class="LoadImage") == 1
            and len(image_paths) == 1
        ):
            input_image = Image.open(image_paths[0]["image_path"])
            self.workflow.set_image(node_name="Load Image", image=input_image)
        else:
            # load and set all images
            for image_info in image_paths:
                input_image = Image.open(image_info["image_path"])
                self.workflow.set_image(image_info["node_name"], input_image)

        # set seed or warn if it is not being set.
        if self.workflow.check_if_node_exists(
            "KSampler (Efficient) - Generation"
        ):  # not present e.g. in mask workflows
            self.workflow.set_value(
                "KSampler (Efficient) - Generation",
                "seed",
                self._get_unique_int_for_image(image_paths[0]["image_path"]),
            )
        else:
            print(
                "Node 'KSampler (Efficient) - Generation' not found in the workflow. Seed will not be set."
            )

        return self.workflow

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments. For this it validates
        the input args, modifies the workflow, and executes it to generate the image.
        Args:
            args (dict[str, any]): A dictionary containing the following keys:
            - "workflow_apiformat_path" (str): The path to the workflow file in API format. (ABSOLUTE PATH)!
                    "example.json"
            - "image_paths" (list[dict]): A dict of [str, str].
                    The keys should be Node names
                    The values should be the paths to the images to be loaded.
                "image_paths": [{
                    "node_name": "Load Input Image",
                    "image_path": "eval_data/test_eval_set/input/model_01.png",}]
            - "generation_params" (list[dict]): A dictionary of generation_params for the image generation process.
                It should look like this:
                [{
                    "node_name": "GroundingDinoSAMSegment (segment anything)",
                    "input": "prompt",
                    "value": "model, bag, hair",
                }],
        Returns:
            Image.Image: The generated image.
        """

        assert (
            "workflow_apiformat_path" in args
        ), "The key 'workflow_apiformat_path' is missing."

        image_paths = args.get("image_paths", [])
        generation_params = args.get("generation_params", [])

        # since the names should all be the same, we can just take the first.
        image_name = image_paths[0]["image_path"].split("/")[-1]

        self.workflow = self._modify_workflow(
            image_paths=image_paths,
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
