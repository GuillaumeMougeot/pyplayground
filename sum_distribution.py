import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from skimage import io
import tifffile as tiff

# np.random.seed(42)

# u = np.random.normal(2,1,(1000,10))
# v = np.random.normal(1,1,(1000,100))
# t = np.hstack((u,v))
# # x = t/t.sum()

# print("number big:", u.size)
# print("number small:", v.size)

# # y = 0.1*np.square(t).sum(axis=0)/t.sum(axis=0)
# y = 0.1*t.mean(axis=0)
# y=y.mean()
# print("threshold 1:", y)

# print("removed big:", (u<y).sum())
# print("removed small:", (v<y).sum())


# y = 0.1*np.square(t).sum(axis=0)/t.sum(axis=0)
# y=y.mean()
# print("threshold 2:", y)

# print("removed big:", (u<y).sum())
# print("removed small:", (v<y).sum())


def compute_otsu_criteria(im, th):
    """Otsu's method to compute criteria."""
    # create the thresholded image
    thresholded_im = np.zeros(im.shape)
    thresholded_im[im >= th] = 1

    # compute weights
    nb_pixels = im.size
    nb_pixels1 = np.count_nonzero(thresholded_im)
    weight1 = nb_pixels1 / nb_pixels
    weight0 = 1 - weight1

    # if one of the classes is empty, eg all pixels are below or above the threshold, that threshold will not be considered
    # in the search for the best threshold
    if weight1 == 0 or weight0 == 0:
        return np.inf

    # find all pixels belonging to each class
    val_pixels1 = im[thresholded_im == 1]
    val_pixels0 = im[thresholded_im == 0]

    # compute variance of these classes
    var1 = np.var(val_pixels1) if len(val_pixels1) > 0 else 0
    var0 = np.var(val_pixels0) if len(val_pixels0) > 0 else 0

    return weight0 * var0 + weight1 * var1

def otsu_thresholding(im):
    """Otsu's thresholding.
    """
    threshold_range = np.linspace(im.min(), im.max()+1, num=255)
    criterias = [compute_otsu_criteria(im, th) for th in threshold_range]
    best_th = threshold_range[np.argmin(criterias)]
    return best_th

def dist_vec(v1,v2):
    """
    euclidean distance between two vectors (np.array)
    """
    v = v2-v1
    return np.sqrt(np.sum(v*v))

def center(labels, idx):
    """
    return the barycenter of the pixels of label = idx
    """
    return np.mean(np.argwhere(labels == idx), axis=0)

def closest(labels, num):
    """
    return the index of the object the closest to the center of the image.
    num: number of label in the image (background does not count)
    """
    labels_center = np.array(labels.shape)/2
    centers = [center(labels,idx+1) for idx in range(num)]
    dist = [dist_vec(labels_center,c) for c in centers]
    return np.argmin(dist)+1

def keep_center_only(msk):
    """
    return mask (msk) with only the connected component that is the closest 
    to the center of the image.
    """
    labels, num = measure.label(msk, background=0, return_num=True)
    close_idx = closest(labels,num)
    return (labels==close_idx).astype(msk.dtype)*255

def volumes(labels):
    """
    returns the volumes of all the labels in the image
    """
    # return [((labels==idx).astype(int)).sum() for idx in np.unique(labels)]
    return np.unique(labels, return_counts=True)[1]

def keep_big_volumes(msk, thres_rate=0.3):
    """
    Return the mask (msk) with less labels/volumes. Select only the biggest volumes with
    the following strategy: minimum_volume = thres_rate * np.sum(np.square(vol))/np.sum(vol)
    This computation could be seen as the expected volume if the variable volume follows the 
    probability distribution: p(vol) = vol/np.sum(vol) 
    """
    # transform image to label
    labels = measure.label(msk, background=0)

    # compute the volume
    unq_labels,vol = np.unique(labels, return_counts=True)

    # remove bg
    unq_labels = unq_labels[1:]
    vol = vol[1:]

    # compute the expected volume
    # expected_vol = np.sum(np.square(vol))/np.sum(vol)
    # min_vol = expected_vol * thres_rate
    min_vol = thres_rate*otsu_thresholding(vol)

    # keep only the labels for which the volume is big enough
    unq_labels = unq_labels[vol > min_vol]

    # compile the selected volumes into 1 image
    s = (labels==unq_labels[0])
    for i in range(1,len(unq_labels)):
        s += (labels==unq_labels[i])

    return s

im = io.imread("D:\\tmp\\WORKINGTIFF_before.tif")
# print(im.shape)
msk = keep_big_volumes(im[0])
print(msk.shape)
tiff.imwrite(
                "D:\\tmp\\WORKINGTIFF_after.tif",
                [msk],
                compression=('zlib', 1))


# print("removed big:", (u<best_th).sum())
# print("removed small:", (v<best_th).sum())

# plt.hist(t[0], bins=20)
# plt.show()