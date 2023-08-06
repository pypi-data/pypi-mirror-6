from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


def structured_array_to_ndarray(structured_array):
    return structured_array.view((translate_data_type("float"), len(structured_array.dtype.names)))
