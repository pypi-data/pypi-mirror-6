from sklearn.preprocessing import OneHotEncoder
from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


class OneHotEncodingTransformer(object):
    def __init__(self, config):
        self.__config = config
        self.__encoder = None

    def fit(self, data):
        categorical_features = self.__find_categorical_features()
        self.__encoder = OneHotEncoder(categorical_features=categorical_features, dtype=translate_data_type("float"))
        self.__encoder.fit(data)

    def fit_transform(self, data):
        self.fit(data)
        return self.transform(data)

    def transform(self, data):
        return self.__encoder.transform(data).toarray()

    def __find_categorical_features(self):
        """
        @return: list containing the indices of the categorical features.
        """
        categorical_features = []
        for i, feature in enumerate(self.__config.get_data_model()):
            if feature.is_categorical():
                categorical_features.append(i)
        return categorical_features




