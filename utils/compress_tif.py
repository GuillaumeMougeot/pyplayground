import os
import tifffile as tiff

def compress_tif_images(input_folder):
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.tif') or file.endswith('.tiff'):
                file_path = os.path.join(root, file)
                with tiff.TiffFile(file_path) as tif:
                    image = tif.asarray()

                tiff.imwrite(file_path, image, compression='zlib')
                print(f"Compressed and saved: {file_path}")

if __name__ == "__main__":
    input_folder = "/gpfswork/rech/ere/uro28rs/codes/biom3d/data/preds"  # Change this to your folder path
    compress_tif_images(input_folder)
