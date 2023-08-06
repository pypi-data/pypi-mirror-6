# -*- coding: utf-8 -*-

# Copyright 2012-2013 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of SkoolKit.
#
# SkoolKit is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# SkoolKit is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# SkoolKit. If not, see <http://www.gnu.org/licenses/>.

"""
Defines the :class:`ImageWriter` class.
"""

from .pngwriter import PngWriter
from .gifwriter import GifWriter

#: Colour name for the transparent colour used in masked images.
TRANSPARENT = 'TRANSPARENT'
#: Colour name for black.
BLACK = 'BLACK'
#: Colour name for blue.
BLUE = 'BLUE'
#: Colour name for red.
RED = 'RED'
#: Colour name for magenta.
MAGENTA = 'MAGENTA'
#: Colour name for green.
GREEN = 'GREEN'
#: Colour name for cyan.
CYAN = 'CYAN'
#: Colour name for yellow.
YELLOW = 'YELLOW'
#: Colour name for white.
WHITE = 'WHITE'
#: Colour name for bright blue.
BRIGHT_BLUE = 'BRIGHT_BLUE'
#: Colour name for bright red.
BRIGHT_RED = 'BRIGHT_RED'
#: Colour name for bright magenta.
BRIGHT_MAGENTA = 'BRIGHT_MAGENTA'
#: Colour name for bright green.
BRIGHT_GREEN = 'BRIGHT_GREEN'
#: Colour name for bright cyan.
BRIGHT_CYAN = 'BRIGHT_CYAN'
#: Colour name for bright yellow.
BRIGHT_YELLOW = 'BRIGHT_YELLOW'
#: Colour name for bright white.
BRIGHT_WHITE = 'BRIGHT_WHITE'

#: Option name that specifies the default image format.
DEFAULT_FORMAT = 'DefaultFormat'
#: Option name that specifies the PNG compression level.
PNG_COMPRESSION_LEVEL = 'PNGCompressionLevel'
#: Option name that specifies the PNG alpha value.
PNG_ALPHA = 'PNGAlpha'
#: Option name that specifies whether to create animated PNGs in APNG format
#: for images that contain flashing cells.
PNG_ENABLE_ANIMATION = 'PNGEnableAnimation'
#: Option name that specifies whether to create animated GIFs for images that
#: contain flashing cells.
GIF_ENABLE_ANIMATION = 'GIFEnableAnimation'
#: Option name that specifies whether to create transparent GIFs for masked
#: images.
GIF_TRANSPARENCY = 'GIFTransparency'
#: Option name that specifies whether GIFs should be compressed.
GIF_COMPRESSION = 'GIFCompression'

PNG_FORMAT = 'png'
GIF_FORMAT = 'gif'

class ImageWriter:
    """Writes PNG and GIF images.

    :type palette: dict
    :param palette: Colour palette replacements to use.
    :type options: dict
    :param options: Options.
    """
    def __init__(self, palette=None, options=None):
        self.options = self._get_default_options()
        if options:
            for k, v in options.items():
                if k == DEFAULT_FORMAT:
                    self.options[k] = v
                else:
                    try:
                        self.options[k] = int(v)
                    except ValueError:
                        pass
        full_palette = self._get_default_palette()
        if palette:
            full_palette.update(palette)
        self._create_colours(full_palette)
        self._create_attr_index()
        self.default_format = self.options[DEFAULT_FORMAT]
        self.animation = {
            PNG_FORMAT: self.options[PNG_ENABLE_ANIMATION],
            GIF_FORMAT: self.options[GIF_ENABLE_ANIMATION]
        }
        self.writers = {
            PNG_FORMAT: PngWriter(self.options[PNG_ALPHA] & 255, self.options[PNG_COMPRESSION_LEVEL]),
            GIF_FORMAT: GifWriter(self.options[GIF_TRANSPARENCY], self.options[GIF_COMPRESSION])
        }

    def write_image(self, frames, img_file, img_format):
        use_flash = len(frames) == 1 and self.animation.get(img_format)
        attrs = set()
        colours = set()
        trans = 0
        for frame in frames:
            f_colours, f_attrs, flash_rect = self._get_colours(frame, use_flash)
            colours.update(f_colours)
            attrs.update(f_attrs)
            trans = trans or frame.trans
        palette, attr_map = self._get_palette(colours, attrs, trans)
        self.writers[img_format].write_image(frames, img_file, palette, attr_map, trans, flash_rect)

    def _get_default_palette(self):
        return  {
            TRANSPARENT: (0, 254, 0),
            BLACK: (0, 0, 0),
            BLUE: (0, 0, 197),
            RED: (197, 0, 0),
            MAGENTA: (197, 0, 197),
            GREEN: (0, 198, 0),
            CYAN: (0, 198, 197),
            YELLOW: (197, 198, 0),
            WHITE: (205, 198, 205),
            BRIGHT_BLUE: (0, 0, 255),
            BRIGHT_RED: (255, 0, 0),
            BRIGHT_MAGENTA: (255, 0, 255),
            BRIGHT_GREEN: (0, 255, 0),
            BRIGHT_CYAN: (0, 255, 255),
            BRIGHT_YELLOW: (255, 255, 0),
            BRIGHT_WHITE: (255, 255, 255)
        }

    def _get_default_options(self):
        return {
            DEFAULT_FORMAT: PNG_FORMAT,
            PNG_COMPRESSION_LEVEL: 9,
            PNG_ENABLE_ANIMATION: 1,
            PNG_ALPHA: 255,
            GIF_ENABLE_ANIMATION: 1,
            GIF_TRANSPARENCY: 0,
            GIF_COMPRESSION: 1
        }

    def _create_colours(self, palette):
        colours = []
        colours.append(palette[TRANSPARENT])
        colours.append(palette[BLACK])
        colours.append(palette[BLUE])
        colours.append(palette[RED])
        colours.append(palette[MAGENTA])
        colours.append(palette[GREEN])
        colours.append(palette[CYAN])
        colours.append(palette[YELLOW])
        colours.append(palette[WHITE])
        colours.append(palette[BRIGHT_BLUE])
        colours.append(palette[BRIGHT_RED])
        colours.append(palette[BRIGHT_MAGENTA])
        colours.append(palette[BRIGHT_GREEN])
        colours.append(palette[BRIGHT_CYAN])
        colours.append(palette[BRIGHT_YELLOW])
        colours.append(palette[BRIGHT_WHITE])
        self.colours = colours

    def _create_attr_index(self):
        self.attr_index = {}
        for attr in range(128):
            if attr & 64:
                ink = 8 + (attr & 7)
                paper = 8 + (attr & 56) // 8
                if ink == 8:
                    ink = 1
                if paper == 8:
                    paper = 1
            else:
                ink = 1 + (attr & 7)
                paper = 1 + (attr & 56) // 8
            self.attr_index[attr] = (paper, ink)

    def _get_colours(self, frame, use_flash=False):
        if not frame.cropped:
            return self._get_all_colours(frame, use_flash)

        udg_array = frame.udgs
        scale = frame.scale
        mask = frame.mask
        x, y, width, height = frame.x, frame.y, frame.width, frame.height
        attrs = set()
        colours = set()
        has_trans = 0
        all_masked = 1
        flashing = False
        y_count = 0
        inc = 8 * scale
        min_x = width
        min_y = height
        max_x = max_y = 0
        rows = 0
        for row in udg_array:
            if y_count >= y + height:
                break
            if y_count + inc - 1 < y:
                y_count += inc
                continue
            for j in range(8):
                if y_count + scale - 1 < y:
                    y_count += scale
                    continue
                if y_count >= y:
                    num_lines = min(y + height - y_count, scale)
                else:
                    num_lines = y_count - y + scale
                x_count = 0
                cols = 0
                for udg in row:
                    if x_count >= x + width:
                        break
                    if x_count + inc - 1 < x:
                        x_count += inc
                        continue
                    attr = udg.attr & 127
                    attrs.add(attr)
                    paper, ink = self.attr_index[attr]
                    byte = udg.data[j]
                    if mask and udg.mask:
                        mask_byte = udg.mask[j]
                        byte &= mask_byte
                    else:
                        all_masked = 0
                        mask_byte = 0
                    if use_flash and udg.attr & 128:
                        colours.add(ink)
                        if ink != paper:
                            colours.add(paper)
                            flashing = True
                    for k in range(8):
                        if x_count >= x + width:
                            break
                        if x_count + scale - 1 < x:
                            x_count += scale
                            byte *= 2
                            mask_byte *= 2
                            continue
                        if x_count >= x:
                            num_bits = min(x + width - x_count, scale)
                        else:
                            num_bits = x_count - x + scale
                        if use_flash and udg.attr & 128 and ink != paper:
                            min_x = min((cols, min_x))
                            max_x = max((cols + num_bits, max_x))
                            min_y = min((rows, min_y))
                            max_y = max((rows + num_lines, max_y))
                        if byte & 128:
                            colours.add(ink)
                        elif mask_byte & 128:
                            has_trans = 1
                        else:
                            colours.add(paper)
                        byte *= 2
                        mask_byte *= 2
                        x_count += scale
                        cols += num_bits
                y_count += scale
                rows += num_lines

        if flashing:
            flash_rect = (min_x, min_y, max_x - min_x, max_y - min_y)
        else:
            flash_rect = None
        if has_trans:
            frame.trans = 1 + all_masked
        else:
            frame.trans = 0
        return colours, attrs, flash_rect

    def _get_all_colours(self, frame, use_flash=False):
        # Find all the colours in an uncropped image
        udg_array = frame.udgs
        mask = frame.mask
        attrs = set()
        colours = set()
        has_trans = 0
        all_masked = 1
        flashing = False
        min_x = len(udg_array[0])
        min_y = len(udg_array)
        max_x = max_y = 0

        y = 0
        for row in udg_array:
            x = 0
            for udg in row:
                attr = udg.attr
                attrs.add(attr & 127)
                paper, ink = self.attr_index[attr & 127]
                if mask and udg.mask:
                    data = [udg.data[i] & udg.mask[i] for i in range(8)]
                    has_non_trans = False
                    if any(data):
                        colours.add(ink)
                        has_non_trans = True
                    if any([b < 255 for b in udg.mask]):
                        colours.add(paper)
                        has_non_trans = True
                    if use_flash and attr & 128 and has_non_trans:
                        colours.add(ink)
                        if ink != paper:
                            min_x = min((x, min_x))
                            min_y = min((y, min_y))
                            max_x = max((x, max_x))
                            max_y = max((y, max_y))
                            colours.add(paper)
                            flashing = True
                    if any([data[i] | udg.mask[i] > data[i] for i in range(8)]):
                        has_trans = 1
                elif use_flash and attr & 128:
                    colours.add(ink)
                    if ink != paper:
                        min_x = min((x, min_x))
                        min_y = min((y, min_y))
                        max_x = max((x, max_x))
                        max_y = max((y, max_y))
                        colours.add(paper)
                        flashing = True
                    all_masked = 0
                else:
                    if any(udg.data):
                        colours.add(ink)
                    if any([b < 255 for b in udg.data]):
                        colours.add(paper)
                    all_masked = 0
                x += 1
            y += 1

        if flashing:
            flash_rect = (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        else:
            flash_rect = None
        if has_trans:
            frame.trans = 1 + all_masked
        else:
            frame.trans = 0
        return colours, attrs, flash_rect

    def _get_palette(self, colours, attrs, trans):
        colour_map = {}
        palette = []
        i = 0
        if trans:
            palette.extend(self.colours[0])
            i += 1
        for colour in colours:
            palette.extend(self.colours[colour])
            colour_map[colour] = i
            i += 1

        attr_map = {}
        for attr in attrs:
            paper, ink = self.attr_index[attr]
            attr_map[attr] = (colour_map.get(paper, 0), colour_map.get(ink, 0))

        return palette, attr_map
