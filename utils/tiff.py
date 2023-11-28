
import tifffile as tiff 

def tif_read_imagej(img_path):
    """Read tif file metadata stored in a ImageJ format.
    adapted from: https://forum.image.sc/t/python-copy-all-metadata-from-one-multipage-tif-to-another/26597/8

    Parameters
    ----------
    img_path : str
        Path to the input image.

    Returns
    -------
    img : numpy.ndarray
        Image.
    img_meta : dict
        Image metadata. 
    """

    with tiff.TiffFile(img_path) as tif:
        assert tif.is_imagej

        # store img_meta
        img_meta = {}

        # get image resolution from TIFF tags
        tags = tif.pages[0].tags
        x_resolution = tags['XResolution'].value
        y_resolution = tags['YResolution'].value
        resolution_unit = tags['ResolutionUnit'].value
        
        img_meta["resolution"] = (x_resolution, y_resolution, resolution_unit)

        # parse ImageJ metadata from the ImageDescription tag
        ij_description = tags['ImageDescription'].value
        ij_description_metadata = tiff.tifffile.imagej_description_metadata(ij_description)
        # remove conflicting entries from the ImageJ metadata
        ij_description_metadata = {k: v for k, v in ij_description_metadata.items()
                                   if k not in 'ImageJ images channels slices frames'}

        img_meta["description"] = ij_description_metadata
        
        # compute spacing
        xres = (x_resolution[1]/x_resolution[0])
        yres = (y_resolution[1]/y_resolution[0])
        zres = float(ij_description_metadata["spacing"])
        
        img_meta["spacing"] = (xres, yres, zres)

        # read the whole image stack and get the axes order
        series = tif.series[0]
        img = series.asarray()
        
        img_meta["axes"] = series.axes
    
    return img, img_meta

def tif_write_imagej(img_path, img, img_meta):
    """Write tif file using metadata in ImageJ format.
    adapted from: https://forum.image.sc/t/python-copy-all-metadata-from-one-multipage-tif-to-another/26597/8
    """
    # saving ImageJ hyperstack requires a 6 dimensional array in axes order TZCYXS
    img = tiff.tifffile.transpose_axes(img, img_meta["axes"], 'TZCYXS')

    # write image and metadata to an ImageJ hyperstack compatible file
    tiff.imwrite(img_path, img,
            resolution=img_meta["resolution"],
            imagej=True, 
            metadata=img_meta["description"],
            compression=('zlib', 1)
            )

