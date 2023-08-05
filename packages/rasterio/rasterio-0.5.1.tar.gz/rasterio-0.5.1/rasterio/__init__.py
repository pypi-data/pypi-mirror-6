# rasterio

import logging
import os

from rasterio.five import string_types
from rasterio._copy import RasterCopier
from rasterio._io import RasterReader, RasterUpdater
from rasterio._io import eval_window, window_index, window_shape
from rasterio._drivers import DriverManager, DummyManager, driver_count
import rasterio.dtypes
from rasterio.dtypes import (
    bool_, ubyte, uint8, uint16, int16, uint32, int32, float32, float64)


__all__ = ['open', 'drivers', 'copy', 'check_dtype']
__version__ = "0.5.1"

log = logging.getLogger('rasterio')
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log.addHandler(NullHandler())


def open(
        path, mode='r', 
        driver=None,
        width=None, height=None,
        count=None,
        dtype=None,
        nodata=None,
        crs=None, transform=None,
        **kwargs):
    """Open file at ``path`` in ``mode`` "r" (read), "r+" (read/write),
    or "w" (write) and return a ``Reader`` or ``Updater`` object.
    
    In write mode, a driver name such as "GTiff" or "JPEG" (see GDAL
    docs or ``gdal_translate --help`` on the command line), ``width``
    (number of pixels per line) and ``height`` (number of lines), the
    ``count`` number of bands in the new file must be specified.
    Additionally, the data type for bands such as ``rasterio.ubyte`` for
    8-bit bands or ``rasterio.uint16`` for 16-bit bands must be
    specified using the ``dtype`` argument.

    A coordinate reference system for raster datasets in write mode can
    be defined by the ``crs`` argument. It takes Proj4 style mappings
    like
    
      {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84',
       'no_defs': True}

    An affine transformation that maps pixel row/column coordinates to
    coordinates in the specified reference system can be specified using
    the ``transform`` argument. The affine transformation is represented
    by a six-element sequence where th:wqe items are ordered like

    Item 0: X coordinate of the top left corner of the top left pixel 
    Item 1: rate of change of X with respect to increasing column, i.e.
            pixel width
    Item 2: rotation, 0 if the raster is oriented "north up" 
    Item 3: Y coordinate of the top left corner of the top left pixel 
    Item 4: rotation, 0 if the raster is oriented "north up"
    Item 5: rate of change of Y with respect to increasing row, usually
            a negative number i.e. -1 * pixel height

    Reference system oordinates can be calculated by the formula

      X = Item 0 + Column * Item 1 + Row * Item 2
      Y = Item 3 + Column * Item 4 + Row * Item 5

    Finally, additional kwargs are passed to GDAL as driver-specific
    dataset creation parameters.
    """
    if not isinstance(path, string_types):
        raise TypeError("invalid path: %r" % path)
    if mode and not isinstance(mode, string_types):
        raise TypeError("invalid mode: %r" % mode)
    if driver and not isinstance(driver, string_types):
        raise TypeError("invalid driver: %r" % driver)
    if mode in ('r', 'r+'):
        if not os.path.exists(path):
            raise IOError("no such file or directory: %r" % path)
    
    if mode == 'r':
        s = RasterReader(path)
    elif mode == 'r+':
        raise NotImplemented("r+ mode not implemented")
        # s = RasterUpdater(path, mode, driver=None)
    elif mode == 'w':
        s = RasterUpdater(
                path, mode, driver,
                width, height, count, 
                crs, transform, dtype,
                nodata,
                **kwargs)
    else:
        raise ValueError(
            "mode string must be one of 'r', 'r+', or 'w', not %s" % mode)

    s.start()
    return s

def check_dtype(dt):
    tp = getattr(dt, 'type', dt)
    return tp in rasterio.dtypes.dtype_rev

def copy(src, dst, **kw):
    """Copy a source dataset to a new destination with driver specific
    creation options.

    ``src`` must be an existing file and ``dst`` a valid output file.

    A ``driver`` keyword argument with value like 'GTiff' or 'JPEG' is
    used to control the output format.
    
    This is the one way to create write-once files like JPEGs.
    """
    with drivers():
        return RasterCopier()(src, dst, **kw)

def drivers(*args):
    """Returns a context manager with registered drivers."""
    if driver_count() == 0:
        log.debug("Creating a DriverManager in drivers()")
        return DriverManager()
    else:
        log.debug("Creating a DummyManager in drivers()")
        return DummyManager()

