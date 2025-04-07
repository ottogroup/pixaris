from abc import abstractmethod


class ExperimentHandler:
    @abstractmethod
    def load_projects_and_datasets(
        self,
        local_results_folder: str = "local_results",
    ):
        pass

    @abstractmethod
    def load_experiment_results_for_dataset(
        self,
        project: str,
        dataset: str,
        local_results_folder: str = "local_results",
    ):
        pass
