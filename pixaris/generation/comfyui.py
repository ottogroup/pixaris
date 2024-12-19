from pixaris.generation.base import ImageGenerator
from pixaris.generation.comfyui_utils.workflow import ComfyWorkflow
from PIL import Image
import hashlib


class ComfyGenerator(ImageGenerator):
    """
    ComfyGenerator is a class that extends the ImageGenerator class to provide functionality for generating images using a specified workflow and API host.
    Methods:
        __init__(api_host: str, workflow_apiformat_path: str):
            Initializes the ComfyGenerator with the specified parameters.
        _get_unique_int_for_image(img: Image.Image) -> int:
            Gets the hash of an image to generate a unique seed for experiments.
        run_workflow_from_local(image_paths: dict[str, str], hyperparameters: list[dict] = []) -> Image:
        generate_single_image(args: dict[str, any]) -> Image.Image:
            Generates a single image using the specified arguments.
    """

    def __init__(
        self,
        api_host: str,
        workflow_apiformat_path: str,
    ):
        """
        api_host (str): The API host URL. For local experimenting, put "localhost:8188".
        workflow_apiformat_path (str): The path to the workflow file in API format.
        """
        self.api_host = api_host
        self.workflow_apiformat_path = workflow_apiformat_path

    def _get_unique_int_for_image(self, img: Image.Image) -> int:
        """
        Gets the hash of an image. This is needed to have a unique seed for the experiments but have the same seed for the same image in different experiments.
        Args:
            img (Image): The image to get the hash from.
        Returns:
            int: The unique integer for the image.
        """
        img_bytes = img.tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()
        unique_number = int(img_hash, 16)
        final_seed = (unique_number % 1000000) + 1  # cannot be too big for comfy
        return final_seed

    def run_workflow(
        self,
        image_paths: dict[str, str],
        hyperparameters: list[dict] = [],
    ):
        """
        Executes a workflow from a local file and processes images according to the specified parameters.
        Args:
            image_paths (dict[str, str]): A dictionary mapping node names to image file paths.
            hyperparameters (list[dict], optional): A list of dictionaries containing hyperparameters. Defaults to [].
        Returns:
            Image: The generated image.
        Raises:
            ConnectionError: If there is an issue connecting to the API host.
        """
        workflow = ComfyWorkflow(
            api_host=self.api_host,
            workflow_file_url=self.workflow_apiformat_path,
        )

        workflow.adjust_workflow_to_generate_one_image_only()

        if hyperparameters:
            workflow.set_hyperparameters(hyperparameters)

        # If only one node of type "LoadImage" with name "Load Image" exists and only one image is passed, set the image.
        if (
            workflow.count_node_class_occurances(
                node_name="Load Image", node_class="LoadImage"
            )
            == 1
            and len(image_paths) == 1
        ):
            input_image = Image.open(list(image_paths.values())[0])
            workflow.set_image(node_name="Load Image", image=input_image)
        else:
            # load and set all images
            for node_name, image_path in image_paths.items():
                input_image = Image.open(image_path)
                workflow.set_image(node_name, input_image)

        # set seed
        if workflow.check_if_node_exists(
            "KSampler (Efficient) - Generation"
        ):  # not present e.g. in mask workflows
            workflow.set_value(
                "KSampler (Efficient) - Generation",
                "seed",
                self._get_unique_int_for_image(input_image),
            )

        try:
            workflow.execute()
            return workflow.get_image("Save Image")[0]
        except ConnectionError as e:
            print(
                "Connection Error. Did you forget to build the iap tunnel to ComfyUI on port 8188?"
            )
            raise e

    def generate_single_image(self, args: dict[str, any]) -> Image.Image:
        """
        Generates a single image based on the provided arguments.
        Args:
            args (dict[str, any]): A dictionary containing the following keys:
            - "image_paths" (dict): A dict of [str, str].
                The keys should be Node names
                The values should be the paths to the images to be loaded.
            - "hyperparameters" (list[dict]): A dictionary of hyperparameters for the image generation process.
                The dict should look like this:
                {
                    "node_name": "GroundingDinoSAMSegment (segment anything)",
                    "input": "prompt",
                    "value": "model, bag, hair",
                },
        Returns:
            Image.Image: The generated image.
        """
        return self.run_workflow(
            image_paths=args["image_paths"], hyperparameters=args["hyperparameters"]
        )
