import tensorflow as tf 

tf.nn.conv2d(tf.random.uniform((1,10,10,1)),tf.random.uniform((3,3,1,1)),strides=1,padding='SAME')
