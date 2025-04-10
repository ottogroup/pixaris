def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries recursively by looping through all keys and updating
    the value lists, so that the resulting dictionary contains all keys and values
    from both dictionaries.

    :param dict1: The first dictionary to merge.
    :type dict1: dict
    :param dict2: The second dictionary to merge.
    :type dict2: dict
    :return: A new dictionary containing all keys and values from both dictionaries.
    :rtype: dict
    """
    resulting_dict = {}
    for key, value in dict1.items():
        if key in dict2:
            if isinstance(value, list) and isinstance(dict2[key], list):
                resulting_dict[key] = value + dict2[key]
            else:
                resulting_dict[key] = dict2[key]
        else:
            resulting_dict[key] = value
    for key, value in dict2.items():
        if key not in resulting_dict:
            resulting_dict[key] = value
    return resulting_dict
