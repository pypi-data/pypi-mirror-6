import abc


class BaseTransformer(object):
    __metaclass__ = abc.ABCMeta

    def fit_transform(self, data):
        self.fit(data)
        return self.transform(data)

    @abc.abstractmethod
    def fit(self, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def transform(self, data):
        raise NotImplementedError()
