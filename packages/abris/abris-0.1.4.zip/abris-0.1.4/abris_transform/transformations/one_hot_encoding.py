from sklearn.preprocessing import OneHotEncoder

from abris_transform.transformations.base_transformer import BaseTransformer
from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


class OneHotEncodingTransformer(BaseTransformer):
    def __init__(self, config):
        self.__config = config
        self.__encoder = None

    def fit(self, data):
        categorical_features = self.__config.get_data_model().find_categorical_columns()
        self.__encoder = OneHotEncoder(categorical_features=categorical_features, dtype=translate_data_type("float"))
        self.__encoder.fit(data)

    def transform(self, data):
        return self.__encoder.transform(data).toarray()



