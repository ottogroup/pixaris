from sklearn.model_selection import ParameterGrid


def expand_hyperparameters(params: list[dict]):
    """
    Expands a list of hyperparameters to a list of dictionaries, each containing a single value.
    This will be used to check if each possible hyperparameter is valid.
    Not using generate_hyperparameter_grid to save time and noch check hyperparameter multiple times
    
    :param params: A list of dictionaries where each dictionary represents a hyperparameter with keys "node_name", "input"
      and "value". The "value" key should have a list of possible values for that hyperparameter.
    :type params: list[dict]
    :return: list of dictionaries containing a single value. Length of the list is the sum of all values in the hyperparameters
    :rtype: list[dict]
    """

    hyperparameters = [
        [
            {"node_name": param["node_name"], "input": param["input"], "value": value}
            for value in param["value"]
        ]
        for param in params
    ]
    # flatten the list
    return [item for sublist in hyperparameters for item in sublist]


def generate_hyperparameter_grid(
    params: list[dict],
) -> list[list[dict]]:
    """
    Generates a grid of hyperparameter combinations.

    :param params: A list of dictionaries where each dictionary represents a hyperparameter with keys "node_name", "input"
      and "value". The "value" key should have a list of possible values for that hyperparameter.
    :type params: list[dict]
    :return: list of dictionaries containing a single value. Length of the list is the product of all values 
      in the hyperparameters
    :rtype: list[dict]
    """
    value_grid = ParameterGrid(
        dict((id, param["value"]) for (id, param) in enumerate(params))
    )
    hyperparameters = [
        [
            {
                "node_name": param["node_name"],
                "input": param["input"],
                "value": combination[iterator],
            }
            for iterator, param in enumerate(params)
        ]
        for combination in value_grid
    ]
    return hyperparameters
