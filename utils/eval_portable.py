
import os
import numpy as np
import SimpleITK as sitk
from skimage import io
import argparse
import tifffile as tiff

def sitk_imread(img_path, return_spacing=True, return_origin=False, return_direction=False):
    """
    image reader for nii.gz files
    """
    img = sitk.ReadImage(img_path)
    img_np = sitk.GetArrayFromImage(img)
    dim = img.GetDimension()
    returns = [img_np]
    spacing = np.array(img.GetSpacing())
    origin = np.array(img.GetOrigin())
    direction = np.array(img.GetDirection())
    if dim==4: # if dim==4 then turn it into 3...
        spacing = spacing[:-1]
        origin = origin[:-1]
        direction = direction.reshape(4,4)[:-1, :-1].reshape(-1)
    elif dim != 4 and dim != 3: 
        raise RuntimeError("Unexpected dimensionality: %d of file %s, cannot split" % (dim, img_path))
    if return_spacing: returns += [spacing]
    if return_origin: returns += [origin]
    if return_direction: returns += [direction]
    return tuple(returns)


def tif_read_meta(tif_path, display=False):
    """
    read the metadata of a tif file and stores them in a python dict.
    if there is a 'ImageDescription' tag, it transforms it as a dictionary
    """
    meta = {}
    with tiff.TiffFile(tif_path) as tif:
        for page in tif.pages:
            for tag in page.tags:
                tag_name, tag_value = tag.name, tag.value
                if display: print(tag.name, tag.code, tag.dtype, tag.count, tag.value)

                # below; fix storage problem for ImageDescription tag
                if tag_name == 'ImageDescription': 
                    list_desc = tag_value.split('\n')
                    dict_desc = {}
                    for idx, elm in enumerate(list_desc):
                        split = elm.split('=')
                        dict_desc[split[0]] = split[1]
                    meta[tag_name] = dict_desc
                else:
                    meta[tag_name] = tag_value
            break # just check the first image
    return meta

def tif_get_spacing(path, res=1e-6):
    """
    get the image spacing stored in the metadata file.
    """
    img_meta = tif_read_meta(path)

    xres = (img_meta["XResolution"][1]/img_meta["XResolution"][0])*res
    yres = (img_meta["YResolution"][1]/img_meta["YResolution"][0])*res
    zres = float(img_meta["ImageDescription"]["spacing"])*res
    # max_dim = min([xres,yres,zres])
    # xres = max_dim / xres
    # yres = max_dim / yres
    # zres = max_dim / zres
    return (xres, yres, zres)

def adaptive_imread(img_path, return_origin=False, return_direction=False):
    """
    use skimage imread or sitk imread depending on the file extension:
    .tif --> skimage.io.imread
    .nii.gz --> SimpleITK.imread
    """
    extension = img_path[img_path.rfind('.'):]
    if extension == ".tif":
        try:
            spacing = tif_get_spacing(img_path)
        except:
            spacing = []
        returns = [io.imread(img_path), spacing]  # TODO: spacing is set to empty but could be set from tif metadata
        if return_origin: returns += [[]]
        if return_direction: returns += [[]]
        return tuple(returns)
    elif extension == ".npy":
        returns = [np.load(img_path), []]
        if return_origin: returns += [[]]
        if return_direction: returns += [[]]
        return tuple(returns)
    else:
        return sitk_imread(img_path, return_origin=return_origin, return_direction=return_direction)

def one_hot_fast(values, num_classes=None):
    """
    transform the 'values' array into a one_hot encoded one

    Warning ! If the number of unique values in the input array is lower than the number of classes, then it will consider that the array values are all between zero and `num_classes`. If one value is greater than `num_classes`, then it will add missing values systematically after the maximum value, which could not be the expected behavior. 
    """
    # get unique values
    uni = np.sort(np.unique(values)).astype(np.uint8)

    if num_classes==None: 
        n_values = len(uni)
    else: 
        n_values = num_classes
    
        # if the expected number of class is two then apply a threshold
        if n_values==2 and (len(uni)>2 or uni.max()>1):
            print("[Warning] The number of expected values is 2 but the maximum value is higher than 1. Threshold will be applied.")
            values = (values>uni[0]).astype(np.uint8)
            uni = np.array([0,1]).astype(np.uint8)
        
        # add values if uni is incomplete
        if len(uni)<n_values: 
            # if the maximum value of the array is greater than n_value, it might be an error but still, we add values in the end.
            if values.max() >= n_values:
                print("[Warning] The maximum values in the array is greater than the provided number of classes, this might be unexpected and might cause issues.")
                while len(uni)<n_values:
                    uni = np.append(uni, np.uint8(uni[-1]+1))
            # add missing values in the array by considering that each values are in 0 and n_value
            else:
                uni = np.arange(0,n_values).astype(np.uint8)
        
    # create the one-hot encoded matrix
    out = np.zeros((n_values, *values.shape), dtype=np.uint8)
    for i in range(n_values):
        out[i] = (values==uni[i]).astype(np.uint8)
    return out

# metric definitions
def iou(inputs, targets, smooth=1):
    inter = (inputs & targets).sum()
    union = (inputs | targets).sum()
    return (inter+smooth)/(union+smooth)

def dice(inputs, targets, smooth=1, axis=(-3,-2,-1)):   
    """Dice score between inputs and targets.
    """
    inter = (inputs & targets).sum(axis=axis)   
    dice = (2.*inter + smooth)/(inputs.sum(axis=axis) + targets.sum(axis=axis) + smooth)  
    return dice.mean()

def versus_one(fct, in_path, tg_path, num_classes, single_class=None):
    """
    comparison function between in_path image and tg_path and using the criterion defined by fct
    """
    img1,_ = adaptive_imread(in_path)
    print("input path",in_path)
    if len(img1.shape)==3:
        img1 = one_hot_fast(img1.astype(np.uint8), num_classes)[1:,...]
    if single_class is not None:
        img1 = img1[single_class,...]
    img1 = (img1 > 0).astype(int)
    
    img2,_ = adaptive_imread(tg_path)
    print("target path",tg_path)
    if len(img2.shape)==3:
        img2 = one_hot_fast(img2.astype(np.uint8), num_classes)[1:,...]
    if single_class is not None:
        img2 = img2[single_class,...]
    img2 = (img2 > 0).astype(int)
    
    # remove background if needed
    if img1.shape[0]==(img2.shape[0]+1):
        img1 = img1[1:]
    if img2.shape[0]==(img1.shape[0]+1):
        img2 = img2[1:]
    
    if sum(img1.shape)!=sum(img2.shape):
        print("bug:sum(img1.shape)!=sum(img2.shape):")
        print("img1.shape", img1.shape)
        print("img2.shape", img2.shape)
        return
    out = fct(img1, img2)
    return out

def abs_path(root, listdir_):
    listdir = listdir_.copy()
    for i in range(len(listdir)):
        listdir[i] = os.path.join(root, listdir[i])
    return listdir

def abs_listdir(path):
    return abs_path(path, os.listdir(path))

def eval(dir_lab, dir_out, num_classes):
    print("Start evaluation")
    paths_lab = [dir_lab, dir_out]
    list_abs = [sorted(abs_listdir(p)) for p in paths_lab]
    assert sum([len(t) for t in list_abs])%len(list_abs)==0, "[Error] Not the same number of labels and predictions! {}".format([len(t) for t in list_abs])

    results = []
    for idx in range(len(list_abs[0])):
        print("Metric computation for:", list_abs[1][idx])
        res = versus_one(
            fct=dice, 
            in_path=list_abs[1][idx], 
            tg_path=list_abs[0][idx], 
            num_classes=num_classes+1, 
            single_class=None)

        print("Metric result:", res)
        results += [res]
        
    print("Evaluation done! Average result:", np.mean(results))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Prediction evaluation.")
    parser.add_argument("-p", "--dir_pred", type=str, default=None,
        help="Path to the prediction directory")  
    parser.add_argument("-l", "--dir_lab", type=str, default=None,
        help="Path to the label directory")  
    parser.add_argument("--num_classes", type=int, default=1,
        help="(default=1) Number of classes (types of objects) in the dataset. The background is not included.")
    args = parser.parse_args()

    eval(args.dir_pred, args.dir_lab, args.num_classes)