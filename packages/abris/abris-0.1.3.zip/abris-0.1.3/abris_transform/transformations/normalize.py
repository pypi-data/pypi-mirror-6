import numpy as np

from abris_transform.transformations.base_transformer import BaseTransformer


class NormalizeTransformer(BaseTransformer):
    def __init__(self, config):
        self.__config = config
        self.__columns_to_normalize = None
        self.__normalize_info = None

    def fit(self, data):
        model = self.__config.get_data_model()
        self.__columns_to_normalize = set(model.find_all_columns()) - set(model.find_text_columns()) \
                                      - set(model.find_boolean_columns())
        if model.has_target():
            self.__columns_to_normalize -= {model.find_target_column()}

        self.__normalize_info = {}
        for column_index in self.__columns_to_normalize:
            column = data[:, column_index]
            mean = np.mean(column)
            std = np.std(column)
            self.__normalize_info[column_index] = NormalizeInformation(mean, std)

    def transform(self, data):
        for column_index in self.__columns_to_normalize:
            info = self.__normalize_info[column_index]
            data[:, column_index] = (data[:, column_index] - info.mean) / info.std
        return data


class NormalizeInformation(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std
