import numpy as np

__data_type_map = {
    "float": np.float_,
    "integer": np.float_,
    "string": "S10",
    "text": "S10",
    "boolean": bool,
    "bool": bool
}


def translate_data_type(data_type):
    return __data_type_map[data_type.lower()]

