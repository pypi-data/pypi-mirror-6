from abris_transform.transformations.array_transformations import StructuredArrayToNdarrayTransformer
from abris_transform.transformations.normalize import NormalizeTransformer
from abris_transform.transformations.one_hot_encoding import OneHotEncodingTransformer
from abris_transform.transformations.boolean_transformations import BooleanToNumberTransformer
from abris_transform.transformations.text_transformations import TextToNumberStructuredTransformer


class TransformPipeline(object):
    def __init__(self):
        self.__transformers = None

    def build_from_config(self, config):
        self.__transformers = []
        self.__transformers.append(TextToNumberStructuredTransformer(config))
        self.__transformers.append(BooleanToNumberTransformer(config))

        self.__transformers.append(StructuredArrayToNdarrayTransformer())

        if config.is_option_enabled("normalize"):
            self.__transformers.append(NormalizeTransformer(config))
        self.__transformers.append(OneHotEncodingTransformer(config))

        return self

    def prepare(self, data):
        for transformer in self.__transformers:
            data = transformer.fit_transform(data)
        return data

    def apply(self, data):
        for transformer in self.__transformers:
            data = transformer.transform(data)
        return data

