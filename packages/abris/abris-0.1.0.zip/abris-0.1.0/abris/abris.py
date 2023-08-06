from sklearn.preprocessing import Normalizer
from abris.configuration.configuration import Configuration

from abris.parsing.csv_parsing import parse_csv_structured
from abris.transformations.array_transformations import structured_array_to_ndarray
from abris.transformations.boolean_transformations import BooleanToNumberTransformer
from abris.transformations.one_hot_encoding import OneHotEncodingTransformer
from abris.transformations.text_transformations import TextToNumberStructuredTransformer


class Abris(object):
    """
    Main entry class for the whole preprocessing engine (and probably the only one that needs to be used
    if no more features are needed).
    """
    def __init__(self, config_file):
        self.__config = Configuration(config_file)
        self.__text_to_number_structured_transformer = None
        self.__boolean_to_number_transformer = None
        self.__one_hot_encoding_transformer = None
        self.__normalizer = None

    def fit_transform(self, data_file):
        self.__text_to_number_structured_transformer = TextToNumberStructuredTransformer(self.__config)
        self.__boolean_to_number_transformer = BooleanToNumberTransformer(self.__config)
        self.__one_hot_encoding_transformer = OneHotEncodingTransformer(self.__config)
        if self.__config.is_option_enabled("normalize"):
            self.__normalizer = Normalizer(**self.__config.get_option_parameters("normalize"))

        data = parse_csv_structured(data_file, self.__config)
        data = self.__text_to_number_structured_transformer.fit_transform(data)
        data = self.__boolean_to_number_transformer.fit_transform(data)
        data = structured_array_to_ndarray(data)
        data = self.__one_hot_encoding_transformer.fit_transform(data)
        if self.__config.is_option_enabled("normalize"):
            data = self.__normalizer.fit_transform(data)

        return data

    def transform(self, data_file):
        data = parse_csv_structured(data_file, self.__config)
        data = self.__text_to_number_structured_transformer.transform(data)
        data = self.__boolean_to_number_transformer.transform(data)
        data = structured_array_to_ndarray(data)
        data = self.__one_hot_encoding_transformer.transform(data)
        if self.__config.is_option_enabled("normalize"):
            data = self.__normalizer.transform(data)

        return data





