import numpy as np

def save_jpeg(image_name, y_rle, cb_rle, cr_rle, shape):
    np.savez_compressed(image_name+".npz", y_rle=y_rle, cb_rle=cb_rle, cr_rle=cr_rle, shape=shape)

def load_jpeg(image_name: str):
    data = np.load(image_name + '.npz', allow_pickle=True)
    y_rle = data["y_rle"]
    cb_rle = data["cb_rle"]
    cr_rle = data["cr_rle"]
    shape = int(data["shape"][0]), int(data["shape"][1])
    return y_rle, cb_rle, cr_rle, shape