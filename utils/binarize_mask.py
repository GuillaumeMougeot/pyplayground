import os
import numpy as np
from skimage import io

def threshold_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tif'):  # assuming files are in TIFF format
            file_path = os.path.join(folder_path, file_name)
            data = io.imread(file_path)
            data[data != 0] = 1  # threshold to binary (0 or 1) intensity
            io.imsave(file_path, data)

# Example usage:
folder_path = 'D:\\data\\cours_dl\\mask'
threshold_folder(folder_path)
