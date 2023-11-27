import napari
import os
from skimage.io import imread 
# import numpy as np
import argparse

def abs_path(root, listdir_):
    listdir = listdir_.copy()
    for i in range(len(listdir)):
        listdir[i] = root + '/' + listdir[i]
    return listdir

def abs_listdir(path):
    return abs_path(path, os.listdir(path))

def remove_begin(pattern, listdir_):
    listdir = listdir_.copy()
    for i in range(len(listdir)):
        listdir[i] = listdir[i][str.find(listdir[i],pattern):]
    return listdir

# metric definition
# def iou(inputs, targets, smooth=1):
#     inter = (inputs & targets).sum()
#     union = (inputs | targets).sum()
#     return (inter+smooth)/(union+smooth)

# def dice(inputs, targets, smooth=1, axis=None):   
#     inter = (inputs & targets).sum(axis=axis)   
#     dice = (2.*inter + smooth)/(inputs.sum(axis=axis) + targets.sum(axis=axis) + smooth)  
#     return dice.mean()

# def bce(inputs, targets, smooth=1e-7):
#     y_pred = np.reshape(inputs, -1)
#     y_true = np.reshape(targets, -1)
#     y_pred = np.clip(y_pred, smooth, 1 - smooth)
#     term_0 = (1-y_true) * np.log(1-y_pred + smooth)
#     term_1 = y_true * np.log(y_pred + smooth)
#     return -np.mean(term_0+term_1, axis=0)


# napari utils

load_fct = lambda v,idx,spacing: imread(list_abs[v][idx])
# load_fct_lab = lambda v,idx,spacing: load_resample_img(list_abs[v][idx], spacing)//255 * (1+v)
load_fct_lab = lambda v,idx,spacing: imread(list_abs[v][idx])

def replace_layers(viewer):
    global idx, list_abs, name_dict, spacing
    for k, v in name_dict.items():
        if k=='image':
            viewer.layers[k].data = load_fct(v,idx,spacing)
        else: # change color properties
            viewer.layers[k].data = load_fct_lab(v,idx,spacing)
    return viewer
    

if __name__=='__main__':
    # parser
    parser = argparse.ArgumentParser(description="Visualization and sorting tool for napari.")
    parser.add_argument("-i", "--images", type=str,
        help="Name of the image folder.")
    parser.add_argument("-m", "--masks", type=str, default=None,
        help="Name of the mask folder.")
    args = parser.parse_args()

    paths_lab = [args.masks]
    path_raw =  args.images

    list_names = ["Labels", ]

    list_abs = [abs_listdir(p) for p in paths_lab]

    if 'path_raw' in locals():
        list_abs = list_abs + [abs_listdir(path_raw)]

    idx = 0
    name_dict = dict(zip(["image"]+list_names, [-1]+[i for i in range(len(list_names))]))
    # fct = iou # metric to display
    spacing = [1,1,1]

    viewer = napari.Viewer()

    for k,v in name_dict.items():
        if k=='image':
            
            viewer.add_image(load_fct(v,idx,spacing), name=k)
        else: # change color properties
            viewer.add_labels(load_fct_lab(v,idx,spacing), name=k)

    
    @viewer.bind_key('n', overwrite=True)
    def napari_print_next(viewer):
        global idx, list_abs
        if idx < len(list_abs[0])-1:
            idx += 1
            viewer = replace_layers(viewer)

    @viewer.bind_key('b', overwrite=True)
    def napari_print_previous(viewer):
        global idx, list_abs
        if idx > 0:
            idx -= 1
            viewer = replace_layers(viewer)
            
    @viewer.bind_key('p', overwrite=True)
    def napari_print_properties(viewer):
        global idx, list_abs
        print("current idx: ", idx)
        print("image name: ", list_abs[0][idx].split('/')[-1])
        # versus_all(versus_one, fct, np.transpose(list_abs)[idx])
        
    @viewer.bind_key('d', overwrite=True)
    def napari_delete_img_msk(viewer):
        global idx, list_abs
        print("current idx: ", idx)
        for j in range(len(list_abs)):
            print("remove: ", list_abs[j][idx])
            os.remove(list_abs[j][idx])
            list_abs[j].remove(list_abs[j][idx])

    napari.run()