import tensorflow as tf
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.utils.generic_utils import CustomObjectScope
from tensorflow.python.keras.layers import Activation, ReLU
from tensorflow.python import keras 
from tensorflow.python.keras import backend as K
from tensorflow.python.platform import gfile
from tensorflow.python.framework import tensor_util
from tensorflow.python.keras.preprocessing import image
import numpy as np
import re
from collections import OrderedDict
import matplotlib.pyplot as plt
import os
import pickle

def dissection(path_to_model):
  if os.path.isfile('app/static/model/layers'):
    with tf.gfile.FastGFile(path_to_model, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      _ = tf.import_graph_def(graph_def, name='')
    layers = pickle.load(open('app/static/model/layers', 'rb'))
    ops =  pickle.load(open('app/static/model/ops', 'rb'))
    return layers, ops
  else:
    with tf.gfile.FastGFile(path_to_model, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      _ = tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
      list_op = sess.graph.get_operations()

      layer_group = []

      for op in list_op:
        a = re.split('/', op.name)
        layer_group.append(a[0])

      po = list(OrderedDict.fromkeys(layer_group))
      po.pop(-1)
      po_dict = {}
      for p in po:
        matching = [op.name for op in list_op if op.name.startswith(p + '/')]
        po_dict[p] = matching
      
      pickle.dump(po, open('app/static/model/layers', 'wb'))
      pickle.dump(po_dict, open('app/static/model/ops', 'wb'))
      return po, po_dict

def results_img(filename, ops, folder):
  with tf.Session() as sess:
    for op, folder in zip(ops, folder):
      img = image.load_img(filename,target_size=(224, 224))
      img_array = image.img_to_array(img)
      img_array_expanded_dims = np.expand_dims(img_array, axis=0)
      opeee = sess.graph.get_tensor_by_name(op + ':0')
      predictions = sess.run(opeee, {'input_1:0': img_array_expanded_dims})
      img_total = predictions.shape[-1]
      o = re.split('/', op)
      for img in range(0, 32):
        plt.xticks([])
        plt.yticks([])
        plt.imshow(predictions[0,:,:,img])
        filename_saved = o[0] + '-' + str(img) + '.png'
        if os.path.isfile(os.path.join(folder, filename_saved)):
          os.remove(os.path.join(folder, filename_saved))
        plt.savefig(os.path.join(folder, filename_saved), bbox_inches='tight')
       
