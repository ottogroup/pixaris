# Pixaris
Repository for evaluation framework for image generation cases.

## Installation
To install Pixaris, follow these steps:
0. make sure to have python 3.12 and poetry 2.0.1 or higher installed.
1. Clone the repository:
    ```sh
    git clone https://github.com/OG-DW/tiga_pixaris
    ```
2. Navigate to the project directory:
    ```sh
    cd pixaris
    ```
3. Install the required dependencies:
    ```sh
    poetry install
    ```

## Usage
Use Pixaris to compare and evaluate different experiments in image generation
![test/assets/examples.png]

### Setting up an eval set
To run and evaluate an experiment, we need a common base of inputs. These are saved as an eval set. 
For our case of image generation with comfy is a directory with the following structure: We need an input and a mask image for every workflow we want to evaluate. The corresponding nodes are called "Load Input Image" and "Load Mask Image". These are loaded from the folders "Input" and "Mask".
Make sure that in every folder under eval_set_name (e.g. Input and Mask) are files with the same name. If in "Input" there is "image_01.jpg", there must be an "image_01.jpg" in "Mask".
The eval set should look like this:
```
eval_data
└───eval_set_name
    ├───Input
    │   ├───image_01.jpg
    │   └───...
    └───Mask
        ├───image_01.jpg
        └───...
```
When using the ComfyGenerator, the images from the "Input" folder will be loaded into the "Load Input Image" Node. Make sure that names in the eval set and in the workflow fit.
You can set this up yourself using the code snippet in the examples folder.

### Run a single Experiment, once
For examples, see the [examples](examples/local_data.py)!
To Use pixaris to evaluate your experiments, you need a data loader, an image generator, a data writer (and possible some metrics). 
Every one of these should be inheriting from the base classes, either `DatasetLoader`, `ImageGenerator`, `DataWriter` or `Metric`. All these are arguments for the function `generate_images_based_on_eval_set`. 

#### Dataset Loaders
Load your dataset using a `DatasetLoader`
```
from pixaris.data_loaders.local import LocalDatasetLoader
loader = LocalDatasetLoader(eval_set=*your eval_set name here*, eval_dir_local="eval_data")
```
If you have your data in a google cloud bucket, you can use the `GCPDatasetLoader`,
```
from pixaris.data_loaders.google import GCPDatasetLoader
loader = GCPDatasetLoader(
    gcp_project_id=*your cgp_project_id here*,
    gcp_bucket_name=*you gcp_bucket_name here*,
    eval_set=*your eval_dir here*,
    eval_dir_local="eval_data", # this is the local path where all your eval_sets are stored
)
```

#### Generator
We use ComfyUI to generate our images.
You can implement your own generator inheriting from `ImageGenerator`. Make it call your existing generation pipeline. A Generator should parse a dataset into usable arguments for your generation. Override the function `generate_single_image` to call your generation
```
from pixaris.generation.comfyui import ComfyGenerator
comfy_generator = ComfyGenerator(workflow_apiformat_path=*WORKFLOW_PATH*)
```
the workflow_apiformat_path should lead to a JSON file generated from comfyUI.
![test/assets/export_apiformat.png]

#### Writer
To save the generated images, we define a DataWriter. In our case we want to have a nice visualization of all input and output images and metrics, so we chose the TensorboardWriter
```
from pixaris.data_writers.tensorboard import TensorboardWriter
writer = TensorboardWriter(
    project_id=*your gcp_project_id here*,
    location=*your gcp_location here*,
    bucket_name=*your gcp_bucket_name here*,
)
```
You can choose to save your results locally using the `LocalDataWriter`

#### Metrics
Maybe we want to generate some metrics to evaluate our results, e.g. mask generation
```
from pixaris.metrics.iou import IoUMetric
true_masks_path = *path to your true masks*
true_masks = [Image.open(true_masks_path + name) for name in os.listdir(true_masks_path)]
iou_metric = IoUMetric(true_masks)
```

#### Args
Sometimes, depending on the specific components and what they provide, we need or want to give some more arguments.
args can include whatever data is needed by other components, and is not given explicitly through parameters.E.g. the ComfyGenerator can be specified by "generation_params". 
In args you can set a seed, an Inspo Image that will be the same in every run or which workflow image should be uploaded to Tensorboard for documentation.
This is highly dependent on the Components you use.
```
args = {
    "workflow_apiformat_path": WORKFLOW_PATH,
    "workflow_image_path": WORKFLOW_IMAGE_PATH,
    "eval_set": EVAL_SET,
    "generation_params": [
        {
            "node_name": "KSampler (Efficient)",
            "input": "seed",
            "value": 42,
        }
    ]
    "image_paths": [
        {
            "node_name": "Load Inspo Image",
            "image_path": "test/assets/test_inspo_image.jpg",
        }
    ],
    "run_name": "example_run",
}
```

#### Putting it all together
After defining the aforementioned components, we simply pass them to the orchestration
```
from pixaris.orchestration.base import generate_images_based_on_eval_set
out = generate_images_based_on_eval_set(
    data_loader=loader,
    image_generator=comfy_generator,
    data_writer=writer,
    metrics=[iou_metric],
    args=args,
)
```
Internally, it will load data, generate images, calculate metrics and save data using the previously defined objects.

## Naming Conventions
- **workflow execution**: Running a workflow for a single input, e.g., object image + mask image.
- **eval set**: Set of evaluation inputs, e.g., 10 * (object image + mask image).
- **run**: One eval set gets run with 1 workflow and 1 set of generation_params.
- **Hyperparameter Search**: One workflow, one eval set, multiple sets of generation_params, with results in multiple runs.
- **Experiment**: Synonymous to run, use run for clarity.
- **Generation Params**: Set of parameters to execute a single run.
- **Hyperparameters**: Multiple sets of different Generation Params, used in hyperparameter search.
- **args**: Includes inputs, e.g., can include workflow apiformat, input images, generation params, save directory, etc.

## Open Source
We published this project to inspire everyone to contribute their own ideas to this project. 
Feel free to fork and add new data loaders, generators, writers or metrics to pixaris!
