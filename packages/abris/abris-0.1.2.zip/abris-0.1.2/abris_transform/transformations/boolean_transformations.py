from abris_transform.type_manipulation.translation.data_type_translation import translate_data_type


class BooleanToNumberTransformer(object):
    def __init__(self, config):
        self.__config = config
        self.__boolean_columns = None

    def fit_transform(self, data):
        """
        @param data: Structured numpy array (numpy.recarray).
        """
        self.__boolean_columns = self.__find_boolean_columns()
        return self.transform(data)

    def transform(self, data):
        for column_index in self.__boolean_columns:
            column_name = data.dtype.names[column_index]
            column = data[column_name]

            numbers = column.astype(translate_data_type("float"))

            # Create a new description so we can change the old dtype to the new numeric type.
            old_type = data.dtype
            description = old_type.descr
            description[column_index] = (description[column_index][0], translate_data_type("float"))

            data[column_name] = numbers
            data = data.astype(description)

        return data

    def __find_boolean_columns(self):
        column_indices = []
        for i, feature in enumerate(self.__config.get_data_model()):
            if feature.is_boolean():
                column_indices.append(i)
        return column_indices