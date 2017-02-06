import skimage
import skimage.io
import skimage.transform


def load_image(path, height=None, width=None):
    img = skimage.io.imread(path)
    if len(img.shape) == 2:
        img = skimage.color.gray2rgb(img)
    img = img / 255.0
    if height is not None and width is not None:
        ny = height
        nx = width
    elif height is not None:
        ny = height
        nx = img.shape[1] * ny / img.shape[0]
    elif width is not None:
        nx = width
        ny = img.shape[0] * nx / img.shape[1]
    else:
        ny = img.shape[0]
        nx = img.shape[1]
    return skimage.transform.resize(img, (ny, nx))
