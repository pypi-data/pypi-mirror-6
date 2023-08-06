"""
Utilities for image manipulation.
"""
import copy
import png

# Python 2 / 3 compatibility
import sys
from applitools.errors import EyesError

if sys.version < '3':
    range = xrange


def png_image_from_file(f):
    """
    Reads the PNG data from the given file stream and returns a new PngImage instance.
    """
    width, height, pixels_iterable, meta_info = png.Reader(file=f).asDirect()
    return PngImage(width, height, list(pixels_iterable), meta_info)


def png_image_from_bytes(png_bytes):
    """
    Reads the PNG data from the given file stream and returns a new PngImage instance.
    """
    width, height, pixels_iterable, meta_info = png.Reader(bytes=png_bytes).asDirect()
    return PngImage(width, height, list(pixels_iterable), meta_info)


class PngImage(object):
    """
    Encapsulates an image.
    """
    def __init__(self, width, height, pixels, meta_info):
        """
        Initializes a PngImage object.
        The "pixels" argument should be a sequence of rows, where each row is a sequence of
        values representing pixels (no separation between pixels inside the raw).
        """
        self.width = width
        self.height = height
        self.pixels = pixels
        self.meta_info = meta_info
        # Images are either RGB or Greyscale
        if not meta_info["greyscale"]:
            self.pixel_size = 3
        else:
            self.pixel_size = 1
        # If there's also an alpha channel
        if meta_info["alpha"]:
            self.pixel_size += 1

    def get_subimage(self, region):
        """
        Returns a PNG binary.
        """
        if region.is_empty():
            raise EyesError('region is empty!')
        result_pixels = []
        x_start = region.left * self.pixel_size
        x_end = x_start + (region.width * self.pixel_size)
        y_start = region.top
        for y_offset in range(region.height):
            pixels_row = self.pixels[y_start + y_offset][x_start:x_end]
            result_pixels.append(pixels_row)
        meta_info = copy.copy(self.meta_info)
        meta_info['size'] = (region.width, region.height)
        return PngImage(region.width, region.height, result_pixels, meta_info)

    def write(self, output):
        """
        Writes the png to the output stream.
        """
        png.Writer(**self.meta_info).write(output, self.pixels)