from generation.generation import ImageGenerator
from utils.load_images import normalize_image, open_image
from generation.workflow import ComfyWorkflow
from PIL import Image
import hashlib


class ComfyGenerator(ImageGenerator):
    def __init__(
        self,
        api_host: str,
        workflow_apiformat_path: str,
        norm_image: bool = False,
        adjust_to_one_image: bool = True,
    ):
        self.api_host = api_host
        self.workflow_apiformat_path = workflow_apiformat_path
        self.norm_image = norm_image
        self.adjust_to_one_image = adjust_to_one_image

    def get_unique_int_for_image(self, img: Image.Image) -> int:
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
    
    def run_workflow_from_local(
        self,
        api_host: str,
        workflow_apiformat_path: str,
        input_image: Image.Image,
        image_paths: list[dict],
        hyperparameters: list[dict] = [],
        norm_image: bool = False,
        adjust_to_one_image: bool = True,
    ):
        """
        Runs a workflow from the local machine using the specified workflow file and object image file.
        The workflow is modified to only generate one image.

        Args:
            workflow_apiformat_path (str): The path to the workflow file.
            input_file_path (str): The path to the input image file.
            hyperparameters (list[dict]): The hyperparameters to be used in the workflow. Defaults to []. This means that no modifications will be performed to the workflow's hyperparameters.
            mask_file_path (str): The path to the mask image file. Defaults to None.
            object_file_path (str): The path to the object image file. Defaults to None.
            inspiration_file_path (str): The path to the inspiration image file. Defaults to None. This is used in IP Adapter!
            norm_image (bool): Whether to normalize (make square) the object image before running the workflow.
                Defaults to True.
            adjust_to_one_image (bool): Whether to adjust the workflow to generate only one image.

        Returns:
            PIL.Image.Image: The resulting image generated by the workflow.

        Raises:
            ConnectionError: If there is a connection error while executing the workflow.
                Likely to happen if you dont have a running virtual machine

        """
        workflow = ComfyWorkflow(
            api_host=api_host,
            workflow_file_url=workflow_apiformat_path,
        )
        if adjust_to_one_image:
            workflow.adjust_workflow_to_generate_one_image_only()

        if hyperparameters:
            workflow.set_hyperparameters(hyperparameters)

        workflow = self.set_image(workflow, input_image, "Load Image", norm_image)
        
        # assert each element of image_paths has the keys "image_path", "node_name", and image paths are strings
        for image_info in image_paths:
            if not all(key in image_info for key in ["node_name", "image_path"]):
                raise ValueError(
                    "Each image dictionary should contain the keys 'image_path', and 'node_name'."
                )
            if not isinstance(image_info["image_path"], str):
                raise ValueError(
                    "The image_path should be a string. Do not pass the image object directly."
                )
        
        # load and set all images
        for image_info in image_paths:
            input_img = open_image(image_info["image_path"], norm_image)
            workflow.set_image(image_info["node_name"], input_img)

        # set seed
        if workflow.check_if_node_exists(
            "KSampler (Efficient) - Generation"
        ):  # not present e.g. in mask workflows
            workflow.set_value(
                "KSampler (Efficient) - Generation",
                "seed",
                self.get_unique_int_for_image(input_image),
            )

        try:
            workflow.execute()
            return workflow.get_image("Save Image")[0]
        except ConnectionError as e:
            print(
                "Connection Error. Did you forget to build the iap tunnel to ComfyUI on port 8188?"
            )
            raise e

    def set_image(
        self,
        workflow: ComfyWorkflow,
        img: Image.Image,
        node_name: str,
        norm_image: bool = False,
    ):
        if norm_image:
            img = normalize_image(img)

        workflow.set_image(node_name, img)
        return workflow

    def generate_single_image(self, args: dict[str, any]) -> Image.Image:
        return self.run_workflow_from_local(
            api_host=self.api_host,
            workflow_apiformat_path=self.workflow_apiformat_path,
            input_image=args['input_image'],
            image_paths=args['image_paths'],
            hyperparameters=args['hyperparameters'],
            norm_image=self.norm_image,
            adjust_to_one_image=self.adjust_to_one_image,
        )
