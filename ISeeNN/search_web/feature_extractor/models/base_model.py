import inspect
import os
from abc import ABCMeta, abstractmethod

import numpy as np
import tensorflow as tf


class BaseModel(metaclass=ABCMeta):

    def __init__(self, weight_npy_name, mean_value):
        path = inspect.getfile(BaseModel)
        path = os.path.abspath(
            os.path.join(
                path, os.pardir, os.pardir, 'weights'))
        path = os.path.join(path, weight_npy_name)
        self._data_dict = np.load(path,
                                 encoding='latin1').item()
        self.__mean_value = mean_value

    def _set_input(self, rgb):
        rgb_scaled = rgb * 255.0

        # Convert RGB to BGR
        red, green, blue = tf.split(3, 3, rgb_scaled)
        bgr = tf.concat(3, [
            blue - self.__mean_value[0],
            green - self.__mean_value[1],
            red - self.__mean_value[2],
        ])
        self.data = bgr

    @property
    @abstractmethod
    def output(self):
        return None

    @abstractmethod
    def build(self, rgb):
        pass