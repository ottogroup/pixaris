### Pixaris: An Evaluation Framework for Image Generation
Welcome to Pixaris, designed for data scientists/ ai engineers / creatives experimenting with image generation! Whether you're leveraging APIs or using ComfyUI, Pixaris streamlines your experiment tracking, making it faster and more efficient.

Inspired by the MLOps mindset, we aim to cultivate an ImageOps approach. With Pixaris, you can track, compare and evaluate your experiments.

![Tensorboard](test/assets/tensorboard-example.png)

## Key Features:
- Experiment Tracking with TensorBoard: Compare your experiments side by side
- Run Experiments Against Your Eval Set: Test your ComfyUI workflows against evaluation data set.
- "Hyperparameter" Search: Explore a limitless range of parameters, such as prompt, model, cfg, noise, seed—to discover the optimal settings for your image generation tasks.
- Implement Metrics for Evaluation: Assess your generated images using your own metrics, calling a multimodal llm.
- Trigger ComfyUI on a Remote Server: Seamlessly initiate your workflows from anywhere.



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
4. Optional:  If you prefer working with Notebooks, install [jupytext](https://github.com/mwouts/jupytext) and you can convert our py files to ipynb.
    ```sh
    pip install jupytext
    ```

    Most important jupytext  commands:
    ```sh
    # convert notebook.ipynb to a .py file
    jupytext --to py notebook.ipynb  

    # convert notebook.py to an .ipynb file with no outputs               
    jupytext --to notebook notebook.py              


    ```


## Getting Started
Use Pixaris to compare and evaluate different experiments in image generation! For example usage, please look [here](examples/local_data.py).

### Setting up an eval set
To run and evaluate an experiment, we need a common base of inputs that we iterate over in order to find out if our way of generating images is good and generalises well. Inputs of any format can be saved as an eval set. This could be images we use as inputs. Putting 10 images means that in one experiment, the workflow is run 10 times with the different images as an input accordingly.

Example: We want to generate backgrounds for photos of products with ComfyUI. We need an input and a mask image for the workflows we want to evaluate. In our ComfyUI workflow, the corresponding nodes are called "Load Input Image" and "Load Mask Image" (see [here](test/assets/test-background-generation.png)). In our eval_set, these are loaded from the folders "Input" and "Mask". Make sure that folder names in the eval set and the node titles in the workflow fit. The eval_set directory has the following structure:
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

When using the ComfyGenerator, the images from the "Input" folder will be loaded into the "Load Input Image" Node. Make sure that in each and every folder under eval_set_name (e.g. Input and Mask) are files with the same name. If in "Input" there is "image_01.jpg", there must be an "image_01.jpg" in "Mask". For one workflow execution, one set of images with the same name is loaded into the workflow. At the end of the experiment, all images have been run through the workflow once.


### Run a single Experiment, once
To use pixaris to evaluate your experiments, you always need a data loader, an image generator, and a data writer (and possibly some metrics).
Every one of these should be inheriting from the base classes, either `DatasetLoader`, `ImageGenerator`, `DataWriter` or `Metric`. After the components are all defined, they will be given to the function `generate_images_based_on_eval_set`. This is the main actor that loads the data, executes and experiment and saves the results.

For a simple example how to run an experiment with a local dataset loader and writer, see the [examples](examples/local_data.py)!

#### Dataset Loaders
First step: load your dataset using a `DatasetLoader`. If you have your eval_set saved locally, use the `LocalDatasetLoader`
```
from pixaris.data_loaders.local import LocalDatasetLoader
loader = LocalDatasetLoader(eval_set=<your eval_set name here>, eval_dir_local="eval_data")
```

If you have your data in a google cloud bucket, you can use the `GCPDatasetLoader`,
```
from pixaris.data_loaders.google import GCPDatasetLoader
loader = GCPDatasetLoader(
    gcp_project_id=<your cgp_project_id here>,
    gcp_bucket_name=<you gcp_bucket_name here>,
    eval_set=<your eval_dir here>,
    eval_dir_local="eval_data", # this is the local path where all your eval_sets are stored
)
```

#### Generator
We implemented a neat `ImageGenerator` that uses ComfyUI.
```
from pixaris.generation.comfyui import ComfyGenerator
comfy_generator = ComfyGenerator(workflow_apiformat_path=<WORKFLOW_PATH>)
```
the workflow_apiformat_path should lead to a JSON file exported from ComfyUI. You can export your workflow in apiformat as shown [here][test/assets/export_apiformat.png].

You can implement your own `ImageGenerator` for image generation with different tools, an API, or whatever you like. Your class needs to inherit from `ImageGenerator` and should call any image generation pipeline. A generator should parse a dataset into usable arguments for your generation. Override the function `generate_single_image` to call your generation.

#### Writer
To save the generated images and possibly metrics, we define a `DataWriter`. In our case we want to have a nice visualization of all input and output images and metrics, so we choose the `TensorboardWriter`.
```
from pixaris.data_writers.tensorboard import TensorboardWriter
writer = TensorboardWriter(
    project_id=<your gcp_project_id here>,
    location=<your gcp_location here>,
    bucket_name=<your gcp_bucket_name here>,
)
```
You can choose to save your results locally using the `LocalDataWriter` or implement your own class that inherits from the `DataWriter`. Usually, it would save images and possibly metrics from your experiment.

#### Metrics
Maybe we want to generate some metrics to evaluate our results, e.g. for mask generation, calculate the IoU with the correct masks.
```
from pixaris.metrics.iou import IoUMetric
correct_masks_path = <path to your correct masks>
correct_masks = [Image.open(correct_masks_path + name) for name in os.listdir(correct_masks_path)]
iou_metric = IoUMetric(true_masks)
```

As always, it is intended for you to implement your own metrics by inheriting from the `BaseMetric` class.

#### Args
Depending on the specific components we defined and what they provide, we need to give some more arguments.
`args` can include whatever data is needed by any of the components, and is not given explicitly through parameters of a component. The content of `args` is highly dependent on the components you use.

For example, additional parameters you want to set in the workflow for the the `ComfyGenerator` can be specified by `generation_params`.
In `args` you can set a seed, an inspiration image for the workflow or which workflow image should be uploaded for documentation. In contrast to the inputs in the eval_set, these will be the same for each execution over the workflow within your experiment.

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
After defining all aforementioned components, we simply pass them to the orchestration
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
- **Hyperparameter Search**: One workflow, one eval set, multiple sets of generation_params, which results in multiple runs.
- **Experiment**: Synonymous to run, use run for clarity.
- **Generation Params**: Set of parameters to execute a single run.
- **Hyperparameters**: Multiple sets of different Generation Params, used in hyperparameter search.
- **args**: Includes inputs, e.g., can include workflow apiformat, input images, generation params, save directory, etc.


## License Information
Pixaris is open-source software licensed .... TODO


## Contribute 
We published this project to inspire everyone to contribute their own ideas to this project. Feel free to fork and add new data loaders, generators, writers or metrics to pixaris! Learn here how: https://opensource.guide/how-to-contribute/
