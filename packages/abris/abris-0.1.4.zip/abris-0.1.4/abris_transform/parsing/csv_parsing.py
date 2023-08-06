import numpy as np

from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


def prepare_csv_structured(data_file, config):
    """
    Parses the given data file following the data model of the given configuration.
    @return: numpy.recarray
    """
    names, dtypes = [], []
    for feature in config.get_data_model():
        assert feature.get_name() not in names
        data_type = feature.get_type()
        dtypes.append(translate_data_type(data_type))
        names.append(feature.get_name())

    data = np.genfromtxt(data_file, delimiter=config.get_delimiter(), dtype=dtypes, names=names)
    return data


def apply_csv_structured(data_file, config):
    """
    Parses the given data file following the data model of the given configuration.
    Ignores the target feature from the config if it exists.
    @return: numpy.recarray
    """
    names, dtypes = [], []
    for feature in config.get_data_model():
        assert feature.get_name() not in names
        if feature.is_target():
            continue
        data_type = feature.get_type()
        dtypes.append(translate_data_type(data_type))
        names.append(feature.get_name())

    data = np.genfromtxt(data_file, delimiter=config.get_delimiter(), dtype=dtypes, names=names)
    return data


def parse_csv_array(data_file):
    """
    Parses the given data file as if it were composed of only numerical values.
    @return: numpy.array
    """
    return np.loadtxt(data_file, dtype=translate_data_type("float"))
