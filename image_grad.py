import numpy as np 
import matplotlib.pyplot as plt 
from skimage import io

path_im = "data/cat.jpg"

im = io.imread(path_im)
plt.imshow(im)
plt.show()