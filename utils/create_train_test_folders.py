# created by ChatGPT

import os
import shutil

# Set the path to the folder containing the images and labels sub-folders
parent_folder = '/path/to/parent/folder'

# Set the names of the sub-folders
subfolder_names = ['images', 'labels']

# Set the names of the train and test sub-folders
subfolder_extensions = ['_train', '_test']

# Set the fraction of files to use for training
train_fraction = 0.5

for subfolder_name in subfolder_names:
    # Create the train and test sub-folders for the current sub-folder
    for subfolder_extension in subfolder_extensions:
        subfolder_path = os.path.join(parent_folder, subfolder_name + subfolder_extension)
        os.makedirs(subfolder_path, exist_ok=True)
    
    # Get the list of files in the current sub-folder
    files = sorted(os.listdir(os.path.join(parent_folder, subfolder_name)))
    
    # Determine the number of files to use for training
    num_train_files = int(len(files) * train_fraction)
    
    # Copy the first half of the sorted files to the train sub-folders
    for i in range(num_train_files):
        file_name = files[i]
        src_path = os.path.join(parent_folder, subfolder_name, file_name)
        dst_path = os.path.join(parent_folder, subfolder_name + '_train', file_name)
        shutil.copy(src_path, dst_path)
        
    # Copy the second half of the sorted files to the test sub-folders
    for i in range(num_train_files, len(files)):
        file_name = files[i]
        src_path = os.path.join(parent_folder, subfolder_name, file_name)
        dst_path = os.path.join(parent_folder, subfolder_name + '_test', file_name)
        shutil.copy(src_path, dst_path)
