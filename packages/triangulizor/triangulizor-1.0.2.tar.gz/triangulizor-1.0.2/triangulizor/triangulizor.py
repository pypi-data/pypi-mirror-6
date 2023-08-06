#!/usr/bin/env python2.7

import itertools
import logging
import sys

try:
    import Image
    import ImageDraw
except ImportError:
    try:
        import PIL.Image as Image
        import PIL.ImageDraw as ImageDraw
    except ImportError:
        if __name__ == '__main__':
            print >> sys.stderr, 'Could not import Python Imaging Library'
            sys.exit(1)
        else:
            raise


def triangulize(image, tile_size):
    """Processes the given image by breaking it down into tiles of the given
    size and applying a triangular effect to each tile. Returns the processed
    image as a PIL Image object.

    The image can be given as anything suitable for passing to `Image.open`
    (ie, the path to an image or as a file-like object containing image data).

    If tile_size is 0, the tile size will be guessed based on the image
    size. It will also be adjusted to be divisible by 2 if it is not already.
    """
    if isinstance(image, basestring) or hasattr(image, 'read'):
        image = Image.open(image)
    assert isinstance(tile_size, int)

    # Make sure we have a usable tile size, by guessing based on image size
    # and making sure it's a multiple of two.
    if tile_size == 0:
        tile_size = guess_tile_size(image)
    if tile_size % 2 != 0:
        tile_size = (tile_size / 2) * 2

    logging.info('Input image size: %r', image.size)
    logging.info('Tile size: %r', tile_size)

    # Preprocess image to make sure it's at a size we can handle
    image = prep_image(image, tile_size)
    logging.info('Prepped image size: %r', image.size)

    # Get pixmap (for direct pixel access) and draw objects for the image.
    pix = image.load()
    draw = ImageDraw.Draw(image)

    # Process the image, tile by tile
    for x, y in iter_tiles(image, tile_size):
        process_tile(x, y, tile_size, pix, draw, image)
    return image


def process_tile(tile_x, tile_y, tile_size, pix, draw, image):
    """Process a tile whose top left corner is at the given x and y
    coordinates.
    """
    logging.debug('Processing tile (%d, %d)', tile_x, tile_y)

    # Calculate average color for each "triangle" in the given tile
    n, e, s, w = triangle_colors(tile_x, tile_y, tile_size, pix)

    # Calculate distance between triangle pairs
    d_ne = get_color_dist(n, e)
    d_nw = get_color_dist(n, w)
    d_se = get_color_dist(s, e)
    d_sw = get_color_dist(s, w)

    # Figure out which pair is the closest, which will determine the direction
    # we'll split this tile into triangles. A 'right' split runs from top left
    # to bottom right. A 'left' split runs bottom left to top right.
    closest = sorted([d_ne, d_nw, d_se, d_sw])[0]
    if closest in (d_ne, d_sw):
        split = 'right'
    elif closest in (d_nw, d_se):
        split = 'left'

    # Figure out the average color for each side of the "split"
    if split == 'right':
        top_color = get_average_color([n, e])
        bottom_color = get_average_color([s, w])
    else:
        top_color = get_average_color([n, w])
        bottom_color = get_average_color([s, e])

    draw_triangles(tile_x, tile_y, tile_size, split, top_color, bottom_color,
                   draw)


def triangle_colors(tile_x, tile_y, tile_size, pix):
    """Extracts the average color for each triangle in the given tile. Returns
    a 4-tuple of colors for the triangles in this order: North, East, South,
    West (clockwise).
    """
    quad_size = tile_size / 2

    north = []
    for y in xrange(tile_y, tile_y + quad_size):
        x_off = y - tile_y
        for x in xrange(tile_x + x_off, tile_x + tile_size - x_off):
            north.append(pix[x, y])

    south = []
    for y in xrange(tile_y + quad_size, tile_y + tile_size):
        x_off = tile_y + tile_size - y
        for x in xrange(tile_x + x_off, tile_x + tile_size - x_off):
            south.append(pix[x, y])

    east = []
    for x in xrange(tile_x, tile_x + quad_size):
        y_off = x - tile_x
        for y in xrange(tile_y + y_off, tile_y + tile_size - y_off):
            east.append(pix[x, y])

    west = []
    for x in xrange(tile_x + quad_size, tile_x + tile_size):
        y_off = tile_x + tile_size - x
        for y in xrange(tile_y + y_off, tile_y + tile_size - y_off):
            west.append(pix[x, y])

    return map(get_average_color, [north, east, south, west])


def draw_triangles(tile_x, tile_y, tile_size, split, top_color, bottom_color,
                   draw):
    """Draws a triangle on each half of the tile with the given coordinates
    and size.
    """
    assert split in ('right', 'left')

    # The four corners of this tile
    nw = (tile_x, tile_y)
    ne = (tile_x + tile_size - 1, tile_y)
    se = (tile_x + tile_size - 1, tile_y + tile_size)
    sw = (tile_x, tile_y + tile_size)

    if split == 'left':
        # top right triangle
        draw_triangle(nw, ne, se, top_color, draw)
        # bottom left triangle
        draw_triangle(nw, sw, se, bottom_color, draw)
    else:
        # top left triangle
        draw_triangle(sw, nw, ne, top_color, draw)
        # bottom right triangle
        draw_triangle(sw, se, ne, bottom_color, draw)


def draw_triangle(a, b, c, color, draw):
    """Draws a triangle with the given vertices in the given color."""
    draw.polygon([a, b, c], fill=color)


def get_average_color(colors):
    """Calculate the average color from the list of colors, where each color
    is a 3-tuple of (r, g, b) values.
    """
    c = reduce(color_reducer, colors)
    total = len(colors)
    return tuple(v / total for v in c)


def color_reducer(c1, c2):
    """Helper function used to add two colors together when averaging."""
    return tuple(v1 + v2 for v1, v2 in itertools.izip(c1, c2))


def get_color_dist(c1, c2):
    """Calculates the "distance" between two colors, where the distance is
    another color whose components are the absolute values of the difference
    between each component of the input colors.
    """
    return tuple(abs(v1 - v2) for v1, v2 in itertools.izip(c1, c2))


def prep_image(image, tile_size):
    """Takes an image and a tile size and returns a possibly cropped version
    of the image that is evenly divisible in both dimensions by the tile size.
    """
    w, h = image.size
    x_tiles = w / tile_size  # floor division
    y_tiles = h / tile_size
    new_w = x_tiles * tile_size
    new_h = y_tiles * tile_size
    if new_w == w and new_h == h:
        return image
    else:
        crop_bounds = (0, 0, new_w, new_h)
        return image.crop(crop_bounds)


def iter_tiles(image, tile_size):
    """Yields (x, y) coordinate pairs for the top left corner of each tile in
    the given image, based on the given tile size.
    """
    w, h = image.size
    for y in xrange(0, h, tile_size):
        for x in xrange(0, w, tile_size):
            yield x, y


def guess_tile_size(image):
    """Try to pick an appropriate tile size based on the image's size."""
    # Formula: 5% of the largest dimension of the image
    return int(max(image.size) * 0.05)
