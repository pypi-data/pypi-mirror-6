from abris_transform.configuration.configuration import Configuration
from abris_transform.numpy_helpers.split_last_column import split_last_column
from abris_transform.parsing.csv_parsing import apply_csv_structured, prepare_csv_structured

from abris_transform.transformations.transform_pipeline import TransformPipeline


class Abris(object):
    """
    Main entry class for the whole preprocessing engine (and probably the only one that needs to be used
    if no more features are needed).
    """
    def __init__(self, config_file):
        self.__config = Configuration(config_file)
        self.__pipeline = None

    def prepare(self, data_file):
        """
        Called with the training data.
        """
        self.__pipeline = TransformPipeline().build_from_config(self.__config)

        data = prepare_csv_structured(data_file, self.__config)
        data = self.__pipeline.prepare(data)

        if self.__config.get_data_model().has_target():
            return split_last_column(data)
        else:
            return data

    def apply(self, data_file):
        """
        Called with the predict data (new information).
        """
        data = apply_csv_structured(data_file, self.__config)
        data = self.__pipeline.apply(data)

        return data





