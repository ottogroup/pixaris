from pixaris.data_loaders.google import GCPDatasetLoader
import os


class MockGCPDatasetLoader(GCPDatasetLoader):
    def __init__(
        self,
        eval_set: str = "mock",
        eval_dir_local: str = os.path.abspath(os.getcwd() + "/test/test_eval_data"),
        force_download: bool = False,
    ):
        self.eval_set = eval_set
        self.eval_dir_local = eval_dir_local
        self.force_download = force_download
        self.image_dirs = [
            name
            for name in os.listdir(os.path.join(self.eval_dir_local, self.eval_set))
            if os.path.isdir(os.path.join(self.eval_dir_local, self.eval_set, name))
        ]
