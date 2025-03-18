from typing import List
from pixaris.generation.base import ImageGenerator
from pixaris.generation.comfyui import ComfyGenerator
from PIL import Image
import os


from kubernetes import client, config
from threading import Lock, Thread
import requests
import time

DEV_MODE = os.getenv("DEV_MODE", "false") == "true"
mutex = Lock()


class ComfyClusterGenerator(ImageGenerator):
    """
    Cluster to run Comfy workflows. It will automatically fetch available hosts, initiate a new ComfyGenerator for each and distribute the workflows to them.
    If the environment variable DEV_MODE is set to true, it will run the workflows locally and it uses localhost:8188.
    """

    def __init__(
        self,
        workflow_apiformat_json: str,
    ):
        self.workflow_apiformat_json = workflow_apiformat_json
        self.hosts = {}
        self.run_background_task = False

    def _fetch_pod_ips(self) -> list[str]:
        """
        Fetch the IPs of the pods running the Comfy UI in the cluster. If the environment variable DEV_MODE is set to true, it will return localhost.

        Returns:
            list[str]: List of IPs of the pods
        """
        if DEV_MODE:
            return ["127.0.0.1"]
        v1 = client.CoreV1Api()
        pod_list = v1.list_namespaced_pod(
            namespace="batch", label_selector="app=comfy-ui", watch=False
        )
        ips = []
        for pod in pod_list.items:
            ips.append(pod.status.pod_ip)
        print(f"Found Pod IPs: {ips}")
        return ips

    def _fetch_available_hosts(self) -> list[str]:
        """
        Fetch the available hosts by checking if the Comfy UI is running on the pod.

        Returns:
            list[str]: List of available hosts
        """
        hosts = []
        for ip in self._fetch_pod_ips():
            host = f"{ip}:8188"
            try:
                resp = requests.get(f"http://{host}", timeout=5)
                if resp.status_code == 200:
                    hosts.append(host)
            except Exception:
                pass
        return hosts

    def update_available_hosts(self):
        """
        Update the available hosts by fetching the IPs of the pods and checking if the Comfy UI is running on them. Use mutex to avoid conflicts.
        """
        available_hosts = self._fetch_available_hosts()
        global mutex
        with mutex:
            for host in available_hosts:
                if host not in self.hosts:
                    self.hosts[host] = {"in_use": False, "unresponsive": False}
                else:
                    self.hosts[host]["unresponsive"] = False
        print(f"Available hosts: {self.hosts}")

    def _get_host(self) -> str:
        """
        Get an available host. If no host is available, it will wait with a exponential backoff and try again, after the 15th retry, it will raise an exception. Use mutex to avoid conflicts.

        Returns:
            str: The host to use
        """
        global mutex
        for i in range(1, 15 + 1):
            with mutex:
                for host, info in self.hosts.items():
                    if not info["in_use"] and not info["unresponsive"]:
                        self.hosts[host]["in_use"] = True
                        return host
            time.sleep(i * i)
        raise Exception("Timeout for getting host")

    def _release_host(self, host: str):
        """
        Release a host. Use mutex to avoid conflicts.

        Args:
            host (str): The host to release
        """
        global mutex
        with mutex:
            self.hosts[host]["in_use"] = False

    def _mark_host_as_unresponsive(self, host: str):
        """
        Mark a host as unresponsive. Use mutex to avoid conflicts.

        Args:
            host (str): The host to mark as unresponsive
        """
        global mutex
        with mutex:
            self.hosts[host]["unresponsive"] = True

    def start_background_task(self):
        """
        Start a background task to update the available hosts every minute.
        """

        def task():
            while self.run_background_task:
                self.update_available_hosts()
                time.sleep(60)

        self.background_task = Thread(target=task, daemon=True)
        self.background_task.start()

    def close(self):
        """
        Close the cluster and release all hosts.
        """
        self.run_background_task = False

    def validate_inputs_and_parameters(
        self,
        dataset: List[dict[str, List[dict[str, Image.Image]]]] = [],
        parameters: list[dict[str, str, any]] = [],
    ) -> str:
        """
        Creates a dummy generator and then calls ComfyGenerator's validate_inputs_and_parameters method.
        Args:
            dataset (List[dict[str, List[dict[str, Image.Image]]]): A list of dictionaries containing the images to be loaded.
            parameters (list[dict[str, str, any]]): A list of dictionaries containing the parameters to be used for the image generation process.
        """
        dummy_generator = ComfyGenerator(self.workflow_apiformat_json)
        dummy_generator.validate_inputs_and_parameters(dataset, parameters)

    def generate_single_image(self, args: dict[str, any]) -> tuple[Image.Image, str]:
        """
        Generates a single image based on the provided arguments. For this it searches for a host, initialises a ComfyGenerator,
        and lets it modify and execute the workflow to generate the image.
        Args:
            args (dict[str, any]): A dictionary containing the following keys:
            - "workflow_apiformat_json" (str): The path to the workflow file in API format. (ABSOLUTE PATH)!
                    "example.json"
            - "pillow_images" (list[dict]): A dict of [str, Image.Image].
                    The keys should be Node names
                    The values should be the PIL Image objects to be loaded.
                "pillow_images": [{
                    "node_name": "Load Input Image",
                    "pillow_image": Image.new("RGB", (100, 100), color="red"),
                }]
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
        # on first execution, load config and start background task while ensuring only one worker will do it.
        global mutex
        with mutex:
            if not self.run_background_task:
                if DEV_MODE:
                    config.load_kube_config()
                else:
                    config.load_incluster_config()
                self.run_background_task = True
                self.start_background_task()

        for retry in range(3):
            host = self._get_host()

            # initialize comfy generator for this host
            comfy_generator = ComfyGenerator(
                workflow_apiformat_json=self.workflow_apiformat_json,
                api_host=host,
            )
            try:
                # generate image and release host
                generated_image = comfy_generator.generate_single_image(args)
                self._release_host(host)
                return generated_image

            except Exception as e:
                print(f"Error in ComfyGenerator: {e}")
                self._mark_host_as_unresponsive(host)
                time.sleep((retry + 1) ** 2)
                if retry == 2:
                    raise e

            finally:
                self._release_host(host)
