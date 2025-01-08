# Pixaris
Repository for evaluation framework for image generation cases

# TODO
How to install.

# Naming Convention (wip)
workflow execution: running a workflow for a single input, e.g. object image + mask image
eval set: set of evaluation inputs, e.g. 10 * (object image + mask image) 
run: One eval set gets run with 1 workflow and 1 set of generation_params
Hyperparameter Search: one workflow, one eval set, multiple sets of generation_params, with results in multiple runs
Experiment: synonymous to run, use run for clarity
Generation Params: Set of parameters to execute a single run
Hyperparameters: multiple sets of different Generation Params, used in hyperparameter search
args: includes inputs, e.g. can include workflow apiformat, input images, generation params, save directory, etc.
