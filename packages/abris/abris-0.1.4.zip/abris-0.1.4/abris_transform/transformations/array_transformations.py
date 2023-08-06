from abris_transform.transformations.base_transformer import BaseTransformer
from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


def structured_array_to_ndarray(structured_array):
    return structured_array.view((translate_data_type("float"), len(structured_array.dtype.names)))


class StructuredArrayToNdarrayTransformer(BaseTransformer):
    def fit(self, data):
        pass

    def transform(self, data):
        return structured_array_to_ndarray(data)
