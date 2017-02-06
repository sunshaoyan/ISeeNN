from abc import ABCMeta, abstractmethod
import numpy as np

class Normalizer(metaclass=ABCMeta):

    """
    :param input shape [feature_number, feature_dimension]
    """
    @abstractmethod
    def normalize(self, input):
        pass


class L2Nomalizer(Normalizer):

    def normalize(self, input):
        return input / np.sqrt(np.square(input).sum(1))[:, np.newaxis]


class RootNormalizer(Normalizer):

    def normalize(self, input):
        return np.sqrt(input / input.sum(1)[:, np.newaxis])


class NormalizerFactory:

    __normalizer_dict = dict(L2=L2Nomalizer, ROOT=RootNormalizer)

    @staticmethod
    def get(name):
        return NormalizerFactory.__normalizer_dict[name]()
