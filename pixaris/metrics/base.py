from abc import abstractmethod


class BaseMetric:
    """When implementing a new Metric, inherit from this one and implement all the abstract methods."""

    @abstractmethod
    def calculate(self, x: any) -> dict:
        """Calculate the metric for the provided input."""
        pass
