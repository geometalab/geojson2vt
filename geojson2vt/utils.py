import os
import json


def current_dir(file):
    return os.path.dirname(os.path.abspath(file))


def get_parent_dir(directory):
    return os.path.abspath(os.path.join(directory, os.path.pardir))


def get_json(file_path):
    data = None
    with open(file_path) as json_file:
        data = json.load(json_file)
        _change_int_coords_to_float(data)
    return data


def _change_int_coords_to_float(data):
    if isinstance(data, dict):
        _walk_dict(data)
    if isinstance(data, list):
        _walk_list(data)


def _walk_dict(tree):
    for key, value in tree.items():
        if isinstance(value, dict):
            _walk_dict(value)
        if isinstance(value, list):
            _walk_list(value)


def _walk_list(lst):
    if len(lst) == 0:
        return
    if isinstance(lst[0], list):
        for l in lst:
            _walk_list(l)
    elif isinstance(lst[0], int):
        for i in range(len(lst)):
            lst[i] = float(lst[i])
    elif isinstance(lst[0], dict):
        for i in range(len(lst)):
            _walk_dict(lst[i])
