#!/usr/bin/env python

import tensorflow as tf
import pathlib

from tensorflow.python import keras
from tensorflow.python.keras import layers
from tensorflow.python.keras.models import Sequential

print('Done importing')
###dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
print('access url')
data_dir = tf.keras.utils.get_file("flower_photos", "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz", untar=True)
print('access data_dir')
data_dir = pathlib.Path(data_dir) 
###print(data_dir)                                                             