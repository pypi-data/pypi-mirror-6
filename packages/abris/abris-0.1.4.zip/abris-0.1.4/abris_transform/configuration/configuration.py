import json
import collections

from abris_transform.configuration.data_model import DataModel
from abris_transform.parsing.parameter_parsing import parse_parameter
from abris_transform.string_aliases import true_boolean_aliases


class Configuration(object):

    def __init__(self, config_file=None):
        self.__config = None
        self.__data_model = None

        if config_file:
            self.load_from_file(config_file)

    def load_from_file(self, config_file):
        self.__config = json.load(config_file, object_pairs_hook=collections.OrderedDict)
        self.__data_model = DataModel(self.__config["data_model"])

    def get_data_model(self):
        return self.__data_model

    def get_delimiter(self):
        return self.__config["delimiter"]

    def is_option_enabled(self, name):
        option_dic = self.__config.get(name, False)
        if option_dic and option_dic["activated"] in true_boolean_aliases:
            return True

    def get_option_parameters(self, name):
        option_dic = self.__config[name]
        params = {}
        for key, value in option_dic.items():
            if key != "activated":
                params[key] = parse_parameter(value)
        return params
