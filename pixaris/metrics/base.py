from abc import abstractmethod


class BaseMetric:
    @abstractmethod
    def calculate(self, x: any) -> dict:
        pass
