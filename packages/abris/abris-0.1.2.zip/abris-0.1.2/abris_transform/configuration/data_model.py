from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


class DataModel(object):
    def __init__(self, data_model_dictionary):
        self.__model = []
        for key, value in data_model_dictionary.items():
            self.__model.append(Feature(key, value))

    def has_any_text_feature(self):
        for feature in self.__model:
            if feature.is_text():
                return True
        return False

    def __iter__(self):
        for feature in self.__model:
            yield feature


class Feature(object):
    def __init__(self, name, characteristics_list):
        self.__name = str(name)
        self.__characteristics = characteristics_list

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__characteristics[0]

    def is_text(self):
        return translate_data_type(self.get_type()) == translate_data_type("string")

    def is_boolean(self):
        return translate_data_type(self.get_type()) == translate_data_type("boolean")

    def is_categorical(self):
        return "categorical" in map(lambda string: string.lower(), self.__characteristics)




