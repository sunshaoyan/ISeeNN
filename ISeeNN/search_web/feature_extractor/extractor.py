from abc import ABCMeta, abstractmethod
import tensorflow as tf

from .models import Vgg16P5, Vgg16FC6
from .util import load_image

class Extractor(metaclass=ABCMeta):

    __models = dict(VGG16P5=Vgg16P5, VGG16FC6=Vgg16FC6)

    def __init__(self, model_type):
        self._graph = tf.Graph()
        with self._graph.as_default():
            self._model = self.__models[model_type]()
            self._inputs = None
            self._build_model()

    def _get_feature(self, img):
        config = tf.ConfigProto(
            device_count = {'GPU': 0}
        )
        with tf.Session(graph=self._graph, config=config) as sess:
            batch = img.reshape((1, img.shape[0], img.shape[1], 3))
            feed_dict = {self._inputs: batch}
            output = sess.run(self._model.output, feed_dict=feed_dict)
            return output


    @abstractmethod
    def _build_model(self):
        pass

    @abstractmethod
    def extract(self, image_path):
        pass


class ResizeExtractor(Extractor):

    def __init__(self, model_type, input_size):
        self.__input_size = input_size
        Extractor.__init__(self, model_type=model_type)

    def _build_model(self):
        self._inputs = tf.placeholder("float", [1, self.__input_size[0], self.__input_size[1], 3])
        self._model.build(self._inputs)

    def extract(self, image_path):
        img = load_image(image_path, self.__input_size[0], self.__input_size[1])
        return Extractor._get_feature(self, img)


class NoResizeExtractor(Extractor):
    def __init__(self, model_type):
        Extractor.__init__(self, model_type=model_type)

    def _build_model(self):
        self._inputs = tf.placeholder("float", None)
        self._model.build(self._inputs)

    def extract(self, image_path):
        img = load_image(image_path)
        return Extractor._get_feature(self, img)
