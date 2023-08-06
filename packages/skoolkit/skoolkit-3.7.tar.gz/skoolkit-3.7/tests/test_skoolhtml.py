# -*- coding: utf-8 -*-
import random
import re
from os.path import join, basename, isfile
import unittest

from skoolkittest import SkoolKitTestCase, StringIO
from skoolkit import VERSION, SkoolKitError, SkoolParsingError
from skoolkit.skoolmacro import MacroParsingError, UnsupportedMacroError
from skoolkit.skoolhtml import HtmlWriter, FileInfo, Udg, Frame
from skoolkit.skoolparser import SkoolParser, Register, BASE_10, BASE_16, CASE_LOWER, CASE_UPPER
from skoolkit.refparser import RefParser

GAMEDIR = 'test'
ASMDIR = 'asm'
MAPS_DIR = 'maps'
GRAPHICS_DIR = 'graphics'
BUFFERS_DIR = 'buffers'
REFERENCE_DIR = 'reference'
UDGDIR = 'images/udgs'
TEMPLATES_DIR = 'templates'

HEADER = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>{name}: {title}</title>
<link rel="stylesheet" type="text/css" href="{path}skoolkit.css" />{script}
</head>
{body}
<table class="header">
<tr>
<td class="headerLogo"><a class="link" href="{path}index.html">{logo}</a></td>
<td class="headerText">{header}</td>
</tr>
</table>"""

INDEX_HEADER = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title>{name}: {title}</title>
<link rel="stylesheet" type="text/css" href="{path}skoolkit.css" />{script}
</head>
{body}
<table class="header">
<tr>
<td class="headerText">{header_prefix}</td>
<td class="headerLogo">{logo}</td>
<td class="headerText">{header_suffix}</td>
</tr>
</table>"""

BARE_FOOTER = """<div class="footer">
<div class="created">Created using <a class="link" href="http://pyskool.ca/?page_id=177">SkoolKit</a> {0}.</div>
</div>
</body>
</html>""".format(VERSION)

PREV_UP_NEXT = """<table class="prevNext">
<tr>
<td class="prev">{prev_link}</td>
<td class="up">{up_link}</td>
<td class="next">{next_link}</td>
</tr>
</table>"""

ERROR_PREFIX = 'Error while parsing #{0} macro'

class TestHtmlWriter(HtmlWriter):
    def write_image(self, img_file, udgs=(), crop_rect=(), scale=2, mask=False):
        frame = Frame(udgs, scale, mask, *crop_rect)
        self.write_animated_image(img_file, [frame])

    def write_animated_image(self, img_file, frames):
        self.image_writer.write_image(img_file, frames)

class MockSkoolParser:
    def __init__(self, snapshot=None, entries=(), memory_map=()):
        self.snapshot = snapshot
        self.entries = entries
        self.memory_map = memory_map
        self.skoolfile = ''
        self.base = None

class MockFileInfo:
    def __init__(self, topdir, game_dir):
        self.odir = join(topdir, game_dir)
        self.path = None
        self.mode = None

    # PY: open_file(self, *names, mode='w') in Python 3
    def open_file(self, *names, **kwargs):
        path = self.odir
        for name in names:
            path = join(path, name)
        self.path = path
        self.mode = kwargs.get('mode', 'w') # PY: Not needed in Python 3
        return StringIO()

    def need_image(self, image_path):
        return True

class MockImageWriter:
    def __init__(self):
        self.build_images = True
        self.default_format = 'png'

    def write_image(self, img_file, frames):
        self.img_file = img_file
        self.frames = frames
        frame1 = frames[0]
        self.udg_array = frame1.udgs
        self.scale = frame1.scale
        self.mask = frame1.mask
        self.x = frame1.x
        self.y = frame1.y
        self.width = frame1.width
        self.height = frame1.height

class MockImageWriter2:
    def __init__(self):
        self.default_format = 'png'

    def write_image(self, frames, img_file, img_format):
        self.frames = frames
        self.img_format = img_format
        if isinstance(frames, list):
            frame1 = frames[0]
            self.udg_array = frame1.udgs
            self.scale = frame1.scale
            self.mask = frame1.mask
            self.x = frame1.x
            self.y = frame1.y
            self.width = frame1.width
            self.height = frame1.height

class HtmlWriterTest(SkoolKitTestCase):
    def read_file(self, fname, lines=False):
        fpath = join(self.odir, GAMEDIR, fname)
        self.assertTrue(isfile(fpath), '{} does not exist'.format(fpath))
        with open(fpath, 'r') as f:
            if lines:
                return [line.rstrip('\n') for line in f]
            return f.read()

    def assert_files_equal(self, d_fname, subs, index=False):
        d_html_lines = self.read_file(d_fname, True)
        body_lines = []
        for line in subs['content'].split('\n'):
            s_line = line.lstrip()
            if s_line:
                body_lines.append(s_line)
        body_class = subs.get('body_class')
        body_class_attr = ' class="{0}"'.format(body_class) if body_class else ''
        subs['body'] = '<body{0}>'.format(body_class_attr)
        js = subs.get('js')
        subs['script'] = '\n<script type="text/javascript" src="{0}"></script>'.format(js) if js else ''
        subs.setdefault('header', subs['title'])
        subs.setdefault('logo', subs['name'])
        footer = subs.get('footer', BARE_FOOTER)
        prev_up_next_lines = []
        if 'up' in subs:
            subs['prev_link'] = ''
            subs['up_link'] = 'Up: <a class="link" href="{path}maps/all.html#{up}">Map</a>'.format(**subs)
            subs['next_link'] = ''
            if 'prev' in subs:
                subs['prev_link'] = 'Prev: <a class="link" href="{0}.html">{0:05d}</a>'.format(subs['prev'])
            if 'next' in subs:
                subs['next_link'] = 'Next: <a class="link" href="{0}.html">{0:05d}</a>'.format(subs['next'])
            prev_up_next = PREV_UP_NEXT.format(**subs)
            prev_up_next_lines = prev_up_next.split('\n')
        header_template = INDEX_HEADER if index else HEADER
        t_html_lines = header_template.format(**subs).split('\n')
        t_html_lines.extend(prev_up_next_lines)
        t_html_lines.extend(body_lines)
        t_html_lines.extend(prev_up_next_lines)
        t_html_lines.extend(footer.split('\n'))
        self.assertEqual(d_html_lines, t_html_lines)

    def assert_html_equal(self, html, exp_html, eol=False):
        exp_lines = []
        for line in exp_html.split('\n'):
            s_line = line.lstrip()
            if s_line:
                exp_lines.append(s_line)
        if eol:
            exp_lines.append('')
        self.assertEqual(html.split('\n'), exp_lines)

    def assert_title_equals(self, fname, title):
        html = self.read_file(fname)
        prefix = self.skoolfile[:-6]
        self.assertTrue('<title>{}: {}</title>'.format(prefix, title) in html)

    def assert_error(self, writer, text, error_msg=None, prefix=None):
        with self.assertRaises(SkoolParsingError) as cm:
            writer.expand(text, ASMDIR)
        if error_msg:
            if prefix:
                error_msg = '{}: {}'.format(prefix, error_msg)
            self.assertEqual(cm.exception.args[0], error_msg)

    def _test_reference_macro(self, macro, def_link_text, page):
        writer = self._get_writer()
        for link_text in ('', '(test)', '(test (nested) parentheses)'):
            for anchor in ('', '#test', '#foo$bar'):
                output = writer.expand('#{}{}{}'.format(macro, anchor, link_text), ASMDIR)
                self.link_equals(output, '../{}/{}.html{}'.format(REFERENCE_DIR, page, anchor), link_text[1:-1] or def_link_text)

        for suffix in ',;:.!)?/"\'':
            output = writer.expand('#{}#name{}'.format(macro, suffix), ASMDIR)
            self.link_equals(output, '../{}/{}.html#name'.format(REFERENCE_DIR, page), def_link_text, suffix)

    def _test_invalid_reference_macro(self, macro):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format(macro)

        # Non-existent item
        self.assert_error(writer, '#{}#nonexistentItem()'.format(macro), "Cannot determine title of item 'nonexistentItem'", prefix)

        # Malformed item name
        self.assert_error(writer, '#{}bad#name()'.format(macro), "Malformed macro: #{}bad#name()".format(macro), prefix)

        # No item name
        self.assert_error(writer, '#{}#(foo)'.format(macro), "No item name: #{}#(foo)".format(macro), prefix)

        # No closing bracket
        self.assert_error(writer, '#{}(foo'.format(macro), "No closing bracket: (foo", prefix)

    def _test_call(self, cwd, arg1, arg2, arg3=None):
        # Method used to test the #CALL macro
        return str((cwd, arg1, arg2, arg3))

    def _test_call_no_retval(self, *args):
        return

    def _unsupported_macro(self, *args):
        raise UnsupportedMacroError()

    def _get_writer(self, ref=None, snapshot=(), case=None, base=None, skool=None, create_labels=False, asm_labels=False):
        self.reffile = None
        self.skoolfile = None
        ref_parser = RefParser()
        if ref is not None:
            self.reffile = self.write_text_file(ref, suffix='.ref')
            ref_parser.parse(self.reffile)
        if skool is None:
            skool_parser = MockSkoolParser(snapshot)
        else:
            self.skoolfile = self.write_text_file(skool, suffix='.skool')
            skool_parser = SkoolParser(self.skoolfile, case=case, base=base, html=True, create_labels=create_labels, asm_labels=asm_labels)
        self.odir = self.make_directory()
        file_info = FileInfo(self.odir, GAMEDIR, False)
        return TestHtmlWriter(skool_parser, ref_parser, file_info, MockImageWriter())

    def _assert_scr_equal(self, game, x0=0, y0=0, w=32, h=24):
        snapshot = game.snapshot[:]
        scr = game.screenshot(x0, y0, w, h)
        self.assertEqual(len(scr),  min((h, 24 - y0)))
        self.assertEqual(len(scr[0]), min((w, 32 - x0)))
        for j, row in enumerate(scr):
            for i, udg in enumerate(row):
                x, y = x0 + i, y0 + j
                df_addr = 16384 + 2048 * (y // 8) + 32 * (y % 8) + x
                af_addr = 22528 + 32 * y + x
                self.assertEqual(udg.data, snapshot[df_addr:df_addr + 2048:256], 'Graphic data for cell at ({0},{1}) is incorrect'.format(x, y))
                self.assertEqual(udg.attr, snapshot[af_addr], 'Attribute byte for cell at ({0},{1}) is incorrect'.format(x, y))

    def link_equals(self, html, href, text, suffix=''):
        self.assertEqual(html, '<a class="link" href="{}">{}</a>{}'.format(href, text, suffix))

    def img_equals(self, html, alt, src):
        self.assertEqual(html, '<img alt="{0}" src="{1}" />'.format(alt, src))

    def _compare_udgs(self, udg_array, exp_udg_array):
        for i, row in enumerate(udg_array):
            exp_row = exp_udg_array[i]
            self.assertEqual(len(row), len(exp_row))
            for j, udg in enumerate(row):
                exp_udg = exp_row[j]
                self.assertEqual(udg.attr, exp_udg.attr)
                self.assertEqual(udg.data, exp_udg.data)
                self.assertEqual(udg.mask, exp_udg.mask)

    def _check_image(self, image_writer, udg_array, scale=2, mask=False, x=0, y=0, width=None, height=None):
        if width is None:
            width = 8 * len(udg_array[0]) * scale
        if height is None:
            height = 8 * len(udg_array) * scale
        self.assertEqual(image_writer.scale, scale)
        self.assertEqual(image_writer.mask, mask)
        self.assertEqual(image_writer.x, x)
        self.assertEqual(image_writer.y, y)
        self.assertEqual(image_writer.width, width)
        self.assertEqual(image_writer.height, height)
        self.assertEqual(len(image_writer.udg_array), len(udg_array))
        self._compare_udgs(image_writer.udg_array, udg_array)

    def _check_animated_image(self, image_writer, frames):
        self.assertEqual(len(image_writer.frames), len(frames))
        for i, frame in enumerate(image_writer.frames):
            exp_frame = frames[i]
            self.assertEqual(frame.scale, exp_frame.scale)
            self.assertEqual(frame.x, exp_frame.x)
            self.assertEqual(frame.y, exp_frame.y)
            self.assertEqual(frame.width, exp_frame.width)
            self.assertEqual(frame.height, exp_frame.height)
            self.assertEqual(frame.mask, exp_frame.mask)
            self.assertEqual(frame.delay, exp_frame.delay)
            self._compare_udgs(frame.udgs, exp_frame.udgs)

    def test_get_screenshot(self):
        snapshot = [0] * 65536
        for a in range(16384, 23296):
            snapshot[a] = random.randint(0, 255)
        writer = self._get_writer(snapshot=snapshot)
        self._assert_scr_equal(writer)
        self._assert_scr_equal(writer, 1, 2, 12, 10)
        self._assert_scr_equal(writer, 10, 10)

    def test_get_font_udg_array(self):
        snapshot = [0] * 65536
        char1 = [1, 2, 3, 4, 5, 6, 7, 8]
        char2 = [8, 7, 6, 5, 4, 3, 2, 1]
        chars = [char1, char2]
        char_data = []
        for char in chars:
            char_data.extend(char)
        address = 32768
        snapshot[address:address + sum(len(c) for c in chars)] = char_data
        writer = self._get_writer(snapshot=snapshot)
        attr = 56
        message = ''.join([chr(n) for n in range(32, 32 + len(chars))])
        font_udg_array = writer.get_font_udg_array(address, attr, message)
        self.assertEqual(len(font_udg_array[0]), len(chars))
        for i, udg in enumerate(font_udg_array[0]):
            self.assertEqual(udg.attr, attr)
            self.assertEqual(udg.data, chars[i])

    def test_ref_parsing(self):
        ref = '\n'.join((
            '[Info]',
            'Release=Test HTML disassembly',
            'Copyright=Me, 2012',
            '',
            '[Links]',
            'Bugs=[Bugs] (program errors)',
            'Pokes=[Pokes [with square brackets in the link text]] (cheats)',
            '',
            '[MemoryMap:TestMap]',
            'EntryTypes=w',
        ))
        writer = self._get_writer(ref=ref)

        # [Info]
        self.assertEqual(writer.info['Release'], 'Test HTML disassembly')
        self.assertEqual(writer.info['Copyright'], 'Me, 2012')

        # [Links]
        self.assertEqual(writer.links['Bugs'], ('Bugs', ' (program errors)'))
        self.assertEqual(writer.links['Pokes'], ('Pokes [with square brackets in the link text]', ' (cheats)'))

        # [MemoryMap:*]
        self.assertTrue('TestMap' in writer.memory_map_names)
        self.assertTrue('TestMap' in writer.memory_maps)
        self.assertEqual(writer.memory_maps['TestMap'], {'EntryTypes': 'w', 'Name': 'TestMap'})

    def test_parse_image_params(self):
        writer = self._get_writer()
        def_crop_rect = (0, 0, None, None)

        text = '1,2,$3'
        end, img_path, crop_rect, p1, p2, p3 = writer.parse_image_params(text, 0, 3)
        self.assertEqual(img_path, None)
        self.assertEqual(crop_rect, def_crop_rect)
        self.assertEqual((p1, p2, p3), (1, 2, 3))
        self.assertEqual(end, len(text))

        text = '4,$a,6{0,1,24,32}'
        end, img_path, crop_rect, p1, p2, p3, p4, p5 = writer.parse_image_params(text, 0, 5, (7, 8))
        self.assertEqual(img_path, None)
        self.assertEqual(crop_rect, (0, 1, 24, 32))
        self.assertEqual((p1, p2, p3, p4, p5), (4, 10, 6, 7, 8))
        self.assertEqual(end, len(text))

        text = '$ff,8,9(img)'
        end, img_path, crop_rect, p1, p2, p3 = writer.parse_image_params(text, 0, 3)
        self.assertEqual(img_path, 'images/udgs/img.png')
        self.assertEqual(crop_rect, def_crop_rect)
        self.assertEqual((p1, p2, p3), (255, 8, 9))
        self.assertEqual(end, len(text))

        text = '0,1{1,2}(scr)'
        end, img_path, crop_rect, p1, p2 = writer.parse_image_params(text, 0, 2, path_id='ScreenshotImagePath')
        self.assertEqual(img_path, 'images/scr/scr.png')
        self.assertEqual(crop_rect, (1, 2, None, None))
        self.assertEqual((p1, p2), (0, 1))
        self.assertEqual(end, len(text))

        text = '0,1,2,3{1,2}(x)'
        with self.assertRaisesRegexp(MacroParsingError, re.escape("Too many parameters (expected 3): '0,1,2,3'")):
            writer.parse_image_params(text, 0, 3)

    def test_image_path(self):
        writer = self._get_writer()
        def_img_format = writer.default_image_format

        img_path = writer.image_path('img')
        self.assertEqual(img_path, '{0}/img.{1}'.format(writer.paths['UDGImagePath'], def_img_format))

        img_path = writer.image_path('/pics/foo.png')
        self.assertEqual(img_path, 'pics/foo.png')

        path_id = 'ScreenshotImagePath'
        img_path = writer.image_path('img.gif', path_id)
        self.assertEqual(img_path, '{0}/img.gif'.format(writer.paths[path_id]))

        path_id = 'UnknownImagePath'
        fname = 'img.png'
        with self.assertRaisesRegexp(SkoolKitError, "Unknown path ID '{}' for image file '{}'".format(path_id, fname)):
            writer.image_path(fname, path_id)

    def test_flip_udgs(self):
        writer = self._get_writer()
        udg1 = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg2 = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [2, 4, 6, 8, 10, 12, 14, 16])
        udg3 = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1])
        udg4 = Udg(0, [8, 7, 6, 5, 4, 3, 2, 1], [255, 254, 253, 252, 251, 250, 249, 248])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.flip_udgs(udgs, 0)
        self.assertEqual(udgs, [[udg1, udg2], [udg3, udg4]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.flip_udgs(udgs, 1)
        udg1_f, udg2_f, udg3_f, udg4_f = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_f.flip(1)
        udg2_f.flip(1)
        udg3_f.flip(1)
        udg4_f.flip(1)
        self.assertEqual(udgs, [[udg2_f, udg1_f], [udg4_f, udg3_f]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.flip_udgs(udgs, 2)
        udg1_f, udg2_f, udg3_f, udg4_f = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_f.flip(2)
        udg2_f.flip(2)
        udg3_f.flip(2)
        udg4_f.flip(2)
        self.assertEqual(udgs, [[udg3_f, udg4_f], [udg1_f, udg2_f]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.flip_udgs(udgs, 3)
        udg1_f, udg2_f, udg3_f, udg4_f = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_f.flip(3)
        udg2_f.flip(3)
        udg3_f.flip(3)
        udg4_f.flip(3)
        self.assertEqual(udgs, [[udg4_f, udg3_f], [udg2_f, udg1_f]])

    def test_rotate_udgs(self):
        writer = self._get_writer()
        udg1 = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg2 = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [2, 4, 6, 8, 10, 12, 14, 16])
        udg3 = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1])
        udg4 = Udg(0, [8, 7, 6, 5, 4, 3, 2, 1], [255, 254, 253, 252, 251, 250, 249, 248])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.rotate_udgs(udgs, 0)
        self.assertEqual(udgs, [[udg1, udg2], [udg3, udg4]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.rotate_udgs(udgs, 1)
        udg1_r, udg2_r, udg3_r, udg4_r = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_r.rotate(1)
        udg2_r.rotate(1)
        udg3_r.rotate(1)
        udg4_r.rotate(1)
        self.assertEqual(udgs, [[udg3_r, udg1_r], [udg4_r, udg2_r]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.rotate_udgs(udgs, 2)
        udg1_r, udg2_r, udg3_r, udg4_r = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_r.rotate(2)
        udg2_r.rotate(2)
        udg3_r.rotate(2)
        udg4_r.rotate(2)
        self.assertEqual(udgs, [[udg4_r, udg3_r], [udg2_r, udg1_r]])

        udgs = [[udg1.copy(), udg2.copy()], [udg3.copy(), udg4.copy()]]
        writer.rotate_udgs(udgs, 3)
        udg1_r, udg2_r, udg3_r, udg4_r = udg1.copy(), udg2.copy(), udg3.copy(), udg4.copy()
        udg1_r.rotate(3)
        udg2_r.rotate(3)
        udg3_r.rotate(3)
        udg4_r.rotate(3)
        self.assertEqual(udgs, [[udg2_r, udg4_r], [udg1_r, udg3_r]])

    def test_macro_bug(self):
        self._test_reference_macro('BUG', 'bug', 'bugs')

        # Anchor with empty link text
        writer = self._get_writer()
        anchor = 'bug1'
        title = 'Bad bug'
        writer.bugs = [(anchor, title, None)]
        output = writer.expand('#BUG#{0}()'.format(anchor), ASMDIR)
        self.link_equals(output, '../reference/bugs.html#{0}'.format(anchor), title)

    def test_macro_bug_invalid(self):
        self._test_invalid_reference_macro('BUG')

    def test_macro_call(self):
        writer = self._get_writer()
        writer.test_call = self._test_call

        # All arguments given
        output = writer.expand('#CALL:test_call(10,test)', ASMDIR)
        self.assertEqual(output, self._test_call(ASMDIR, 10, 'test'))

        # One argument omitted
        output = writer.expand('#CALL:test_call(3,,test2)', ASMDIR)
        self.assertEqual(output, self._test_call(ASMDIR, 3, None, 'test2'))

        # No return value
        writer.test_call_no_retval = self._test_call_no_retval
        output = writer.expand('#CALL:test_call_no_retval(1,2)', ASMDIR)
        self.assertEqual(output, '')

        # Unknown method
        method_name = 'nonexistent_method'
        output = writer.expand('#CALL:{0}(0)'.format(method_name), ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(self.err.getvalue().split('\n')[0], 'WARNING: Unknown method name in #CALL macro: {0}'.format(method_name))

    def test_macro_call_invalid(self):
        writer = self._get_writer()
        writer.test_call = self._test_call
        prefix = ERROR_PREFIX.format('CALL')

        # No parameters
        self.assert_error(writer, '#CALL', 'No parameters', prefix)

        # Malformed #CALL macro
        self.assert_error(writer, '#CALLtest_call(5,s)', 'Malformed macro: #CALLt...', prefix)

        # No method name
        self.assert_error(writer, '#CALL:(0)', 'No method name', prefix)

        # #CALL a non-method
        writer.var = 'x'
        self.assert_error(writer, '#CALL:var(0)', 'Uncallable method name: var', prefix)

        # No argument list
        self.assert_error(writer, '#CALL:test_call', 'No argument list specified: #CALL:test_call', prefix)

        # No closing bracket
        self.assert_error(writer, '#CALL:test_call(1,2', 'No closing bracket: (1,2', prefix)

        # Not enough parameters
        self.assert_error(writer, '#CALL:test_call(1)')

        # Too many parameters
        self.assert_error(writer, '#CALL:test_call(1,2,3,4)')

    def test_macro_chr(self):
        writer = self._get_writer()

        output = writer.expand('#CHR169', ASMDIR)
        self.assertEqual(output, '&#169;')

        output = writer.expand('#CHR(163)1984', ASMDIR)
        self.assertEqual(output, '&#163;1984')

    def test_macro_chr_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('CHR')

        # No parameter
        self.assert_error(writer, '#CHR', 'No parameters (expected 1)', prefix)

        # Blank parameter
        self.assert_error(writer, '#CHR()', "Invalid integer: ''", prefix)

        # Invalid parameter (1)
        self.assert_error(writer, '#CHR2$', "Cannot parse integer '2$' in parameter string: '2$'", prefix)

        # Invalid parameter (2)
        self.assert_error(writer, '#CHR(x)', "Invalid integer: 'x'", prefix)

        # No closing bracket
        self.assert_error(writer, '#CHR(2 ...', 'No closing bracket: (2 ...', prefix)

    def test_macro_d(self):
        skool = '\n'.join((
            '; @start',
            '',
            '; First routine',
            'c32768 RET',
            '',
            '; Second routine',
            'c32769 RET',
            '',
            'c32770 RET',
        ))
        writer = self._get_writer(skool=skool)

        output = writer.expand('#D32768', ASMDIR)
        self.assertEqual(output, 'First routine')

        output = writer.expand('#D$8001', ASMDIR)
        self.assertEqual(output, 'Second routine')

    def test_macro_d_invalid(self):
        skool = '; @start\nc32770 RET'
        writer = self._get_writer(skool=skool)
        prefix = ERROR_PREFIX.format('D')

        # No parameter (1)
        self.assert_error(writer, '#D', 'No parameters (expected 1)', prefix)

        # No parameter (2)
        self.assert_error(writer, '#Dx', 'No parameters (expected 1)', prefix)

        # Invalid parameter
        self.assert_error(writer, '#D234$', "Cannot parse integer '234$' in parameter string: '234$'", prefix)

        # Descriptionless entry
        self.assert_error(writer, '#D32770', 'Entry at 32770 has no description', prefix)

        # Non-existent entry
        self.assert_error(writer, '#D32771', 'Cannot determine description for non-existent entry at 32771', prefix)

    def test_macro_erefs(self):
        # Entry point with one referrer
        skool = '\n'.join((
            '; Referrer',
            'c40000 JP 40004',
            '',
            '; Routine',
            'c40003 LD A,B',
            ' 40004 INC A'
        ))
        writer = self._get_writer(skool=skool)
        output = writer.expand('#EREFS40004', ASMDIR)
        self.assertEqual(output, 'routine at <a class="link" href="40000.html">40000</a>')

        # Entry point with more than one referrer
        skool = '\n'.join((
            '; @start',
            '; First routine',
            'c30000 CALL 30004',
            '',
            '; Second routine',
            'c30003 LD A,B',
            ' 30004 LD B,C',
            '',
            '; Third routine',
            'c30005 JP 30004',
        ))
        writer = self._get_writer(skool=skool)
        output = writer.expand('#EREFS30004', ASMDIR)
        self.assertEqual(output, 'routines at <a class="link" href="30000.html">30000</a> and <a class="link" href="30005.html">30005</a>')

    def test_macro_erefs_invalid(self):
        skool = '; @start\nc30005 JP 30004'
        writer = self._get_writer(skool=skool)
        prefix = ERROR_PREFIX.format('EREFS')

        # No parameter (1)
        self.assert_error(writer, '#EREFS', 'No parameters (expected 1)', prefix)

        # No parameter (2)
        self.assert_error(writer, '#EREFSx', 'No parameters (expected 1)', prefix)

        # Invalid parameter
        self.assert_error(writer, '#EREFS2$2', "Cannot parse integer '2$2' in parameter string: '2$2'", prefix)

        # Entry point with no referrers
        address = 30005
        self.assert_error(writer, '#EREFS30005', 'Entry point at 30005 has no referrers', prefix)

    def test_macro_fact(self):
        self._test_reference_macro('FACT', 'fact', 'facts')

        # Anchor with empty link text
        writer = self._get_writer()
        anchor = 'fact1'
        title = 'Amazing fact'
        writer.facts = [(anchor, title, None)]
        output = writer.expand('#FACT#{0}()'.format(anchor), ASMDIR)
        self.link_equals(output, '../reference/facts.html#{0}'.format(anchor), title)

    def test_macro_fact_invalid(self):
        self._test_invalid_reference_macro('FACT')

    def test_macro_font(self):
        snapshot = [0] * 65536
        writer = self._get_writer(snapshot=snapshot)

        output = writer.expand('#FONT32768,96', ASMDIR)
        self.img_equals(output, 'font', '../images/font/font.png')

        img_fname = 'font2'
        output = writer.expand('#FONT55584,96({0})'.format(img_fname), ASMDIR)
        self.img_equals(output, img_fname, '../images/font/{0}.png'.format(img_fname))

        img_fname = 'font3'
        font_addr = 32768
        char1 = [1, 2, 3, 4, 5, 6, 7, 8]
        char2 = [8, 7, 6, 5, 4, 3, 2, 1]
        char3 = [1, 3, 7, 15, 31, 63, 127, 255]
        chars = (char1, char2, char3)
        for i, char in enumerate(chars):
            snapshot[font_addr + i * 8:font_addr + (i + 1) * 8] = char
        attr = 4
        scale = 2
        x, y, w, h = 1, 2, 3, 4
        macro = '#FONT{0},{1},{2},{3}{{{4},{5},{6},{7}}}({8})'.format(font_addr, len(chars), attr, scale, x, y, w, h, img_fname)
        output = writer.expand(macro, ASMDIR)
        self.img_equals(output, img_fname, '../images/font/{0}.png'.format(img_fname))
        udg_array = [[Udg(4, char) for char in chars]]
        self._check_image(writer.image_writer, udg_array, scale, False, x, y, w, h)

    def test_macro_font_text(self):
        snapshot = [1, 2, 3, 4, 5, 6, 7, 8] # ' '
        snapshot.extend((8, 7, 6, 5, 4, 3, 2, 1)) # '!'
        snapshot.extend((1, 3, 7, 15, 31, 63, 127, 255)) # '"'
        snapshot.extend([0] * 56)
        snapshot.extend((1, 3, 5, 7, 9, 11, 13, 15)) # ')'
        writer = self._get_writer(snapshot=snapshot)

        img_fname = 'message'
        message = ' !"%'
        macro = '#FONT:({})0({})'.format(message, img_fname)
        output = writer.expand(macro, ASMDIR)
        self.img_equals(output, img_fname, '../images/font/{}.png'.format(img_fname))
        udg_array = [[]]
        for c in message:
            c_addr = 8 * (ord(c) - 32)
            udg_array[0].append(Udg(56, snapshot[c_addr:c_addr + 8]))
        self._check_image(writer.image_writer, udg_array)

        message = ')!!!!'
        attr = 43
        scale = 5
        c_addr = 8 * (ord(message[0]) - 32)
        udg_array = [[Udg(attr, snapshot[c_addr:c_addr + 8])]]
        for delim1, delim2 in (('{', '}'), ('[', ']'), ('*', '*'), ('@', '@')):
            macro = '#FONT:{}{}{}0,1,{},{}({})'.format(delim1, message, delim2, attr, scale, img_fname)
            output = writer.expand(macro, ASMDIR)
            self.img_equals(output, img_fname, '../images/font/{}.png'.format(img_fname))
            self._check_image(writer.image_writer, udg_array, scale)

    def test_macro_font_with_custom_font_image_path(self):
        font_path = 'graphics/font'
        ref = '[Paths]\nFontImagePath={}'.format(font_path)
        writer = self._get_writer(ref=ref, snapshot=[0] * 16)
        img_fname = 'text'
        exp_img_path = '{}/{}.png'.format(font_path, img_fname)

        output = writer.expand('#FONT:(!!!)0({})'.format(img_fname), ASMDIR)
        self.img_equals(output, img_fname, '../{}'.format(exp_img_path))
        self.assertEqual(writer.image_writer.img_file, exp_img_path)

    def test_macro_font_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('FONT')

        # No parameters
        self.assert_error(writer, '#FONT', 'No parameters (expected 1)', prefix)

        # No parameters (2)
        self.assert_error(writer, '#FONTx', 'No parameters (expected 1)', prefix)

        # No text parameter
        self.assert_error(writer, '#FONT:', 'No text parameter', prefix)

        # Too many parameters
        self.assert_error(writer, '#FONT0,1,2,3,4,5', "Too many parameters (expected 4): '0,1,2,3,4,5'", prefix)

        # Invalid parameter
        self.assert_error(writer, '#FONT0,1$,2', "Cannot parse integer '1$' in parameter string: '0,1$,2'", prefix)

        # No closing bracket
        self.assert_error(writer, '#FONT(foo', 'No closing bracket: (foo', prefix)

        # Empty message
        self.assert_error(writer, '#FONT:()0', 'Empty message: ()', prefix)

        # No terminating text delimiter
        self.assert_error(writer, '#FONT:[hi)0', 'No terminating delimiter: [hi)0', prefix)

    def test_macro_html(self):
        writer = self._get_writer()

        delimiters = {
            '(': ')',
            '[': ']',
            '{': '}'
        }
        for text in('', 'See <a href="url">this</a>', 'A &gt; B'):
            for delim1 in '([{!@$%^*_-+|':
                delim2 = delimiters.get(delim1, delim1)
                output = writer.expand('#HTML{0}{1}{2}'.format(delim1, text, delim2), ASMDIR)
                self.assertEqual(output, text)

        output = writer.expand('#HTML?#CHR169?', ASMDIR)
        self.assertEqual(output, '&#169;')

    def test_macro_html_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('HTML')

        # No text parameter
        self.assert_error(writer, '#HTML', 'No text parameter', prefix)

        # Unterminated
        self.assert_error(writer, '#HTML:unterminated', 'No terminating delimiter: :unterminated', prefix)

    def test_macro_link(self):
        ref = '\n'.join((
            '[Page:Custom_Page_1]',
            'Title=Custom page',
            'Path=page.html',
            '',
            '[Page:Custom_Page_2]',
            'Path=page2.html',
            'Link=Custom page 2',
        ))
        writer = self._get_writer(ref=ref)

        link_text = 'bugs'
        output = writer.expand('#LINK:Bugs({0})'.format(link_text), ASMDIR)
        self.link_equals(output, '../{0}/bugs.html'.format(REFERENCE_DIR), link_text)

        link_text = 'pokes'
        anchor = '#poke1'
        output = writer.expand('#LINK:Pokes{0}({1})'.format(anchor, link_text), ASMDIR)
        self.link_equals(output, '../{0}/pokes.html{1}'.format(REFERENCE_DIR, anchor), link_text)

        output = writer.expand('#LINK:Custom_Page_1()', ASMDIR)
        self.link_equals(output, '../page.html', 'Custom page')

        output = writer.expand('#LINK:Custom_Page_2#anchor~1()', ASMDIR)
        self.link_equals(output, '../page2.html#anchor~1', 'Custom page 2')

    def test_macro_link_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('LINK')

        # No parameters
        self.assert_error(writer, '#LINK', 'No parameters', prefix)

        # No page ID (1)
        self.assert_error(writer, '#LINK:', 'No page ID: #LINK:', prefix)

        # No page ID (2)
        self.assert_error(writer, '#LINK:(text)', 'No page ID: #LINK:(text)', prefix)

        # No closing bracket
        self.assert_error(writer, '#LINK:(text', 'No closing bracket: (text', prefix)

        # Malformed macro
        self.assert_error(writer, '#LINKpageID(text)', 'Malformed macro: #LINKp...', prefix)

        # Unknown page ID
        self.assert_error(writer, '#LINK:nonexistentPageID(text)', 'Unknown page ID: nonexistentPageID', prefix)

        # No link text
        self.assert_error(writer, '#LINK:Bugs', 'No link text: #LINK:Bugs', prefix)

    def test_macro_list(self):
        writer = self._get_writer()

        # List with a CSS class and an item containing a skool macro
        src = "(default){ Item 1 }{ Item 2 }{ #REGa }"
        html = '\n'.join((
            '<ul class="default">',
            '<li>Item 1</li>',
            '<li>Item 2</li>',
            '<li><span class="register">A</span></li>',
            '</ul>'
        ))
        output = writer.expand('#LIST{0}\nLIST#'.format(src), ASMDIR)
        self.assertEqual(output, html)

        # List with no CSS class
        src = "{ Item 1 }"
        html = '\n'.join((
            '<ul>',
            '<li>Item 1</li>',
            '</ul>'
        ))
        output = writer.expand('#LIST{0}\nLIST#'.format(src), ASMDIR)
        self.assertEqual(output, html)

        # Empty list
        output = writer.expand('#LIST LIST#', ASMDIR)
        self.assertEqual(output, '<ul>\n</ul>')

    def test_macro_list_invalid(self):
        writer = self._get_writer()

        # No end marker
        self.assert_error(writer, '#LIST { Item }', 'No end marker: #LIST { Item }...')

    def test_macro_poke(self):
        self._test_reference_macro('POKE', 'poke', 'pokes')

        # Anchor with empty link text
        writer = self._get_writer()
        anchor = 'poke1'
        title = 'Awesome POKE'
        writer.pokes = [(anchor, title, None)]
        output = writer.expand('#POKE#{0}()'.format(anchor), ASMDIR)
        self.link_equals(output, '../reference/pokes.html#{0}'.format(anchor), title)

    def test_macro_poke_invalid(self):
        self._test_invalid_reference_macro('POKE')

    def test_macro_pokes(self):
        writer = self._get_writer(snapshot=[0] * 65536)
        snapshot = writer.snapshot

        output = writer.expand('#POKES32768,255', ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(snapshot[32768], 255)

        output = writer.expand('#POKES32768,254,10', ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(snapshot[32768:32778], [254] * 10)

        output = writer.expand('#POKES32768,253,20,2', ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(snapshot[32768:32808:2], [253] * 20)

        output = writer.expand('#POKES49152,1;49153,2', ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(snapshot[49152:49154], [1, 2])

    def test_macro_pokes_invalid(self):
        writer = self._get_writer(snapshot=[0])
        prefix = ERROR_PREFIX.format('POKES')

        # No parameters (1)
        self.assert_error(writer, '#POKES', 'No parameters (expected 2)', prefix)

        # No parameters (2)
        self.assert_error(writer, '#POKESx', 'No parameters (expected 2)', prefix)

        # Not enough parameters (1)
        self.assert_error(writer, '#POKES0', "Not enough parameters (expected 2): '0'", prefix)

        # Not enough parameters (2)
        self.assert_error(writer, '#POKES0,1;1', "Not enough parameters (expected 2): '1'", prefix)

        # Invalid parameter
        self.assert_error(writer, '#POKES40000,2$2', "Cannot parse integer '2$2' in parameter string: '40000,2$2'", prefix)

    def test_macro_pops(self):
        writer = self._get_writer(snapshot=[0] * 65536)
        addr, byte = 49152, 128
        writer.snapshot[addr] = byte
        writer.push_snapshot('test')
        writer.snapshot[addr] = (byte + 127) % 256
        output = writer.expand('#POPS', ASMDIR)
        self.assertEqual(output, '')
        self.assertEqual(writer.snapshot[addr], byte)

    def test_macro_pushs(self):
        writer = self._get_writer(snapshot=[0] * 65536)
        addr, byte = 32768, 64
        for name in ('test', '#foo', 'foo$abcd', ''):
            for suffix in ('', '(bar)', ':baz'):
                writer.snapshot[addr] = byte
                output = writer.expand('#PUSHS{}{}'.format(name, suffix), ASMDIR)
                self.assertEqual(output, suffix)
                self.assertEqual(writer.get_snapshot_name(), name)
                self.assertEqual(writer.snapshot[addr], byte)
                writer.snapshot[addr] = (byte + 127) % 256
                writer.pop_snapshot()
                self.assertEqual(writer.snapshot[addr], byte)

    def test_macro_r(self):
        skool = '\n'.join((
            'c00000 LD A,B',
            '',
            'c00007 LD A,C',
            '',
            'c00016 LD A,D',
            '',
            'c00115 LD A,E',
            '',
            'c01114 LD A,H',
            '',
            '; Routine',
            'c24576 LD HL,$6003',
            '',
            '; Data',
            'b$6003 DEFB 123',
            ' $6004 DEFB 246',
            '',
            '; Another routine',
            'c24581 NOP',
            ' 24582 NOP',
            '',
            '; Yet another routine',
            'c24583 CALL 24581',
            '',
            '; Another routine still',
            'c24586 CALL 24581',
            ' 24589 JP 24582',
            '',
            '; The final routine',
            'c24592 CALL 24582'
        ))
        writer = self._get_writer(skool=skool)

        # Reference address is 0
        output = writer.expand('#R0', ASMDIR)
        self.link_equals(output, '0.html', '0')

        # Reference address is 1 digit
        output = writer.expand('#R7', ASMDIR)
        self.link_equals(output, '7.html', '7')

        # Reference address is 2 digits
        output = writer.expand('#R16', ASMDIR)
        self.link_equals(output, '16.html', '16')

        # Reference address is 3 digits
        output = writer.expand('#R115', ASMDIR)
        self.link_equals(output, '115.html', '115')

        # Reference address is 4 digits
        output = writer.expand('#R1114', ASMDIR)
        self.link_equals(output, '1114.html', '1114')

        # Routine reference
        output = writer.expand('#R24576', ASMDIR)
        self.link_equals(output, '24576.html', '24576')

        # Link text
        link_text = 'Testing1'
        output = writer.expand('#R24576({0})'.format(link_text), ASMDIR)
        self.link_equals(output, '24576.html', link_text)

        # Different current working directory
        output = writer.expand('#R24576', 'other')
        self.link_equals(output, '../{0}/24576.html'.format(ASMDIR), '24576')

        # Routine with a hexadecimal address
        output = writer.expand('#R24579', ASMDIR)
        self.link_equals(output, '24579.html', '6003')

        # Entry point reference
        output = writer.expand('#R24580', ASMDIR)
        self.link_equals(output, '24579.html#24580', '6004')

        # Non-existent reference
        prefix = ERROR_PREFIX.format('R')
        self.assert_error(writer, '#R$ABCD', 'Could not find routine file containing $ABCD', prefix)

    def test_macro_r_other_code(self):
        ref = '\n'.join((
            '[OtherCode:other]',
            'Source=other.skool',
            'Path=other',
            'Index=other.html',
            'Title=Other code',
            'Header=Other code'
        ))
        skool = '\n'.join((
            'c49152 LD DE,0',
            ' 49155 RET',
            '',
            'r$C000 other',
            ' $c003'
        ))
        writer = self._get_writer(ref=ref, skool=skool)

        # Reference with the same address as a remote entry
        output = writer.expand('#R49152', ASMDIR)
        self.link_equals(output, '49152.html', '49152')

        # Reference with the same address as a remote entry point
        output = writer.expand('#R49155', ASMDIR)
        self.link_equals(output, '49152.html#49155', '49155')

        # Other code, no remote entry
        output = writer.expand('#R32768@other', ASMDIR)
        self.link_equals(output, '../other/32768.html', '32768')

        # Other code with remote entry
        output = writer.expand('#R49152@other', ASMDIR)
        self.link_equals(output, '../other/49152.html', 'C000')

        # Other code with remote entry point
        output = writer.expand('#R49155@other', ASMDIR)
        self.link_equals(output, '../other/49152.html#49155', 'c003')

        # Other code with anchor and link text
        link_text = 'Testing2'
        anchor = 'testing3'
        output = writer.expand('#R32768@other#{0}({1})'.format(anchor, link_text), ASMDIR)
        self.link_equals(output, '../other/32768.html#{0}'.format(anchor), link_text)

    def test_macro_r_decimal(self):
        ref = '\n'.join((
            '[OtherCode:other]',
            'Source=other.skool',
            'Path=other',
            'Index=other.html',
            'Title=Other code',
            'Header=Other code'
        ))
        skool = '\n'.join((
            'c32768 LD A,B',
            ' 32769 RET',
            '',
            'r$C000 other',
            ' $C003'
        ))
        writer = self._get_writer(ref=ref, skool=skool, base=BASE_10)

        # Routine
        output = writer.expand('#R32768', ASMDIR)
        self.link_equals(output, '32768.html', '32768')

        # Routine entry point
        output = writer.expand('#R32769', ASMDIR)
        self.link_equals(output, '32768.html#32769', '32769')

        # Other code, no remote entry
        output = writer.expand('#R32768@other', ASMDIR)
        self.link_equals(output, '../other/32768.html', '32768')

        # Other code with remote entry
        output = writer.expand('#R49152@other', ASMDIR)
        self.link_equals(output, '../other/49152.html', '49152')

        # Other code with remote entry point
        output = writer.expand('#R49155@other', ASMDIR)
        self.link_equals(output, '../other/49152.html#49155', '49155')

    def test_macro_r_hex(self):
        ref = '\n'.join((
            '[OtherCode:other]',
            'Source=other.skool',
            'Path=other',
            'Index=other.html',
            'Title=Other code',
            'Header=Other code'
        ))
        skool = '\n'.join((
            'c32768 LD A,B',
            ' 32769 RET',
            '',
            'r$C000 other',
            ' $C003'
        ))
        writer = self._get_writer(ref=ref, skool=skool, base=BASE_16)

        # Routine
        output = writer.expand('#R32768', ASMDIR)
        self.link_equals(output, '32768.html', '8000')

        # Routine entry point
        output = writer.expand('#R32769', ASMDIR)
        self.link_equals(output, '32768.html#32769', '8001')

        # Other code, no remote entry
        output = writer.expand('#R32768@other', ASMDIR)
        self.link_equals(output, '../other/32768.html', '8000')

        # Other code with remote entry
        output = writer.expand('#R49152@other', ASMDIR)
        self.link_equals(output, '../other/49152.html', 'C000')

        # Other code with remote entry point
        output = writer.expand('#R49155@other', ASMDIR)
        self.link_equals(output, '../other/49152.html#49155', 'C003')

    def test_macro_r_hex_lower(self):
        ref = '\n'.join((
            '[OtherCode:Other]',
            'Source=other.skool',
            'Path=other',
            'Index=other.html',
            'Title=Other code',
            'Header=Other code'
        ))
        skool = '\n'.join((
            'c40970 LD A,B',
            ' 40971 RET',
            '',
            'r$C000 other',
            ' $C003'
        ))
        writer = self._get_writer(ref=ref, skool=skool, case=CASE_LOWER, base=BASE_16)

        # Routine
        output = writer.expand('#R40970', ASMDIR)
        self.link_equals(output, '40970.html', 'a00a')

        # Routine entry point
        output = writer.expand('#R40971', ASMDIR)
        self.link_equals(output, '40970.html#40971', 'a00b')

        # Other code, no remote entry
        output = writer.expand('#R45066@Other', ASMDIR)
        self.link_equals(output, '../other/45066.html', 'b00a')

        # Other code with remote entry
        output = writer.expand('#R49152@Other', ASMDIR)
        self.link_equals(output, '../other/49152.html', 'c000')

        # Other code with remote entry point
        output = writer.expand('#R49155@Other', ASMDIR)
        self.link_equals(output, '../other/49152.html#49155', 'c003')

    def test_macro_r_hex_upper(self):
        ref = '\n'.join((
            '[OtherCode:other]',
            'Source=other.skool',
            'Path=other',
            'Index=other.html',
            'Title=Other code',
            'Header=Other code'
        ))
        skool = '\n'.join((
            'c$a00a LD A,B',
            ' 40971 RET',
            '',
            'r$c000 other',
            ' $c003'
        ))
        writer = self._get_writer(ref=ref, skool=skool, case=CASE_UPPER, base=BASE_16)

        # Routine
        output = writer.expand('#R40970', ASMDIR)
        self.link_equals(output, '40970.html', 'A00A')

        # Routine entry point
        output = writer.expand('#R40971', ASMDIR)
        self.link_equals(output, '40970.html#40971', 'A00B')

        # Other code, no remote entry
        output = writer.expand('#R45066@other', ASMDIR)
        self.link_equals(output, '../other/45066.html', 'B00A')

        # Other code with remote entry
        output = writer.expand('#R49152@other', ASMDIR)
        self.link_equals(output, '../other/49152.html', 'C000')

        # Other code with remote entry point
        output = writer.expand('#R49155@other', ASMDIR)
        self.link_equals(output, '../other/49152.html#49155', 'C003')

    def test_macro_r_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('R')

        # No address (1)
        self.assert_error(writer, '#R', "No address", prefix)

        # No address (2)
        self.assert_error(writer, '#R@main', "No address", prefix)

        # No address (3)
        self.assert_error(writer, '#R#bar', "No address", prefix)

        # No address (4)
        self.assert_error(writer, '#R(baz)', "No address", prefix)

        # Invalid address
        self.assert_error(writer, '#R20$5', "Invalid address: 20$5", prefix)

        # No closing bracket
        self.assert_error(writer, '#R32768(qux', "No closing bracket: (qux", prefix)

        # Non-existent other code reference
        self.assert_error(writer, '#R24576@nonexistent', "Could not find code path for 'nonexistent' disassembly", prefix)

    def test_macro_refs(self):
        # One referrer
        skool = '\n'.join((
            '; Referrer',
            'c40000 JP 40003',
            '',
            '; Routine',
            'c40003 LD A,B'
        ))
        writer = self._get_writer(skool=skool)
        output = writer.expand('#REFS40003', ASMDIR)
        self.assertEqual(output, 'routine at <a class="link" href="40000.html">40000</a>')

        skool = '\n'.join((
            '; Not used directly by any other routines',
            'c24576 LD HL,$6003',
            '',
            '; Used by the routines at 24581, 24584 and 24590',
            'c24579 LD A,H',
            ' 24580 RET',
            '',
            '; Calls 24579',
            'c24581 CALL 24579',
            '',
            '; Also calls 24579',
            'c24584 CALL 24579',
            ' 24587 JP 24580',
            '',
            '; Calls 24579 too',
            'c24590 CALL 24580',
        ))
        writer = self._get_writer(skool=skool)

        # Some referrers
        for address in ('24579', '$6003'):
            output = writer.expand('#REFS{}'.format(address), ASMDIR)
            self.assertEqual(output, 'routines at <a class="link" href="24581.html">24581</a>, <a class="link" href="24584.html">24584</a> and <a class="link" href="24590.html">24590</a>')

        # No referrers
        output = writer.expand('#REFS24576', ASMDIR)
        self.assertEqual(output, 'Not used directly by any other routines')

    def test_macro_refs_invalid(self):
        writer = self._get_writer(skool='')
        prefix = ERROR_PREFIX.format('REFS')

        # No address
        self.assert_error(writer, '#REFS', "No address", prefix)

        # Invalid address
        self.assert_error(writer, '#REFS3$56', "Invalid address: 3$56", prefix)

        # No closing bracket
        self.assert_error(writer, '#REFS34567(foo', "No closing bracket: (foo", prefix)

        # Non-existent entry
        self.assert_error(writer, '#REFS40000', "No entry at 40000", prefix)

    def test_macro_reg(self):
        # Lower case
        writer = self._get_writer()
        writer.case = CASE_LOWER
        output = writer.expand('#REGhl', ASMDIR)
        self.assertEqual(output, '<span class="register">hl</span>')
        writer.case = None

        # Upper case, all registers
        for reg in ("a", "b", "c", "d", "e", "h", "l", "i", "r", "ixl", "ixh", "iyl", "iyh", "b'", "c'", "d'", "e'", "h'", "l'", "bc", "de", "hl", "sp", "ix", "iy", "bc'", "de'", "hl'"):
            output = writer.expand('#REG{0}'.format(reg), ASMDIR)
            self.assertEqual(output, '<span class="register">{0}</span>'.format(reg.upper()))

    def test_macro_reg_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('REG')

        # Missing register argument (1)
        self.assert_error(writer, '#REG', 'Missing register argument', prefix)

        # Missing register argument (2)
        self.assert_error(writer, '#REGq', 'Missing register argument', prefix)

        # Bad register argument
        self.assert_error(writer, '#REGabcd', 'Bad register: "abcd"', prefix)

    def test_macro_scr(self):
        snapshot = [0] * 65536
        writer = self._get_writer(snapshot=snapshot)

        output = writer.expand('#SCR', ASMDIR)
        self.img_equals(output, 'scr', '../images/scr/scr.png')

        scr_fname = 'scr2'
        output = writer.expand('#SCR2,0,0,10,10({0})'.format(scr_fname), ASMDIR)
        self.img_equals(output, scr_fname, '../images/scr/{0}.png'.format(scr_fname))

        scr_fname = 'scr3'
        data = [128, 64, 32, 16, 8, 4, 2, 1]
        attr = 48
        snapshot[16384:18432:256] = data
        snapshot[22528] = attr
        scale = 2
        x, y, w, h = 1, 2, 5, 6
        macro = '#SCR{0},0,0,1,1{{{1},{2},{3},{4}}}({5})'.format(scale, x, y, w, h, scr_fname)
        output = writer.expand(macro, ASMDIR)
        self.img_equals(output, scr_fname, '../images/scr/{0}.png'.format(scr_fname))
        udg_array = [[Udg(attr, data)]]
        self._check_image(writer.image_writer, udg_array, scale, False, x, y, w, h)

    def test_macro_scr_with_custom_screenshot_path(self):
        scr_path = 'graphics/screenshots'
        ref = '[Paths]\nScreenshotImagePath={}'.format(scr_path)
        writer = self._get_writer(ref=ref, snapshot=[0] * 23296)
        exp_img_path = '{}/scr.png'.format(scr_path)

        output = writer.expand('#SCR', ASMDIR)
        self.img_equals(output, 'scr', '../{}'.format(exp_img_path))
        self.assertEqual(writer.image_writer.img_file, exp_img_path)

    def test_macro_scr_invalid(self):
        writer = self._get_writer(snapshot=[0] * 8)
        prefix = ERROR_PREFIX.format('SCR')

        # Too many parameters
        self.assert_error(writer, '#SCR0,1,2,3,4,5,6,7,8', "Too many parameters (expected 7): '0,1,2,3,4,5,6,7,8'", prefix)

        # No closing bracket
        self.assert_error(writer, '#SCR(foo', 'No closing bracket: (foo', prefix)

        # Invalid parameter
        self.assert_error(writer, '#SCR0,1,2$,3', "Cannot parse integer '2$' in parameter string: '0,1,2$,3'", prefix)

    def test_macro_space(self):
        writer = self._get_writer()

        output = writer.expand('#SPACE', ASMDIR)
        self.assertEqual(output, '&#160;')

        num = 10
        output = writer.expand('#SPACE{0}'.format(num), ASMDIR)
        self.assertEqual(output, '&#160;' * num)

        num = 7
        output = writer.expand('1#SPACE({0})1'.format(num), ASMDIR)
        self.assertEqual(output, '1{0}1'.format('&#160;' * num))

    def test_macro_space_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('SPACE')

        # Invalid integer
        self.assert_error(writer, '#SPACE5$3', "Cannot parse integer '5$3' in parameter string: '5$3'", prefix)

        # Invalid integer in brackets
        self.assert_error(writer, '#SPACE(5$3)', "Invalid integer: '5$3'", prefix)

        # No closing bracket
        self.assert_error(writer, '#SPACE(2', "No closing bracket: (2", prefix)

    def test_macro_table(self):
        src1 = '\n'.join((
            '(data)',
            '{ =h Col1 | =h Col2 | =h,c2 Cols3+4 }',
            '{ =r2 X   | Y       | Za  | Zb }',
            '{           Y2      | Za2 | =t }'
        ))
        html1 = """
            <table class="data">
            <tr>
            <th>Col1</th>
            <th>Col2</th>
            <th colspan="2">Cols3+4</th>
            </tr>
            <tr>
            <td rowspan="2">X</td>
            <td>Y</td>
            <td>Za</td>
            <td>Zb</td>
            </tr>
            <tr>
            <td>Y2</td>
            <td>Za2</td>
            <td class="transparent"></td>
            </tr>
            </table>
        """

        src2 = '\n'.join((
            '(,centre)',
            '{ =h Header }',
            '{ Cell }'
        ))
        html2 = """
            <table>
            <tr>
            <th>Header</th>
            </tr>
            <tr>
            <td class="centre">Cell</td>
            </tr>
            </table>
        """

        writer = self._get_writer()
        for src, html in ((src1, html1), (src2, html2)):
            output = writer.expand('#TABLE{}\nTABLE#'.format(src), ASMDIR)
            self.assert_html_equal(output, html)

        # Empty table
        output = writer.expand('#TABLE TABLE#', ASMDIR)
        self.assertEqual(output, '<table>\n</table>')

    def test_macro_table_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('TABLE')

        # No end marker
        self.assert_error(writer, '#TABLE { A1 }', 'Missing table end marker: #TABLE { A1 }...')

    def test_macro_udg(self):
        snapshot = [0] * 65536
        writer = self._get_writer(snapshot=snapshot)

        udg_fname = 'udg32768_56x4'
        output = writer.expand('#UDG32768', ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))

        udg_fname = 'udg40000_2x3'
        output = writer.expand('#UDG40000,2,3', ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))

        udg_fname = 'test_udg'
        output = writer.expand('#UDG32768,2,6,1,0:49152,2({0})'.format(udg_fname), ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))

        udg_fname = 'test_udg2'
        udg_addr = 32768
        attr = 2
        scale = 1
        step = 1
        inc = 0
        mask_addr = 32776
        x, y, w, h = 2, 1, 3, 4
        udg_data = [136] * 8
        udg_mask = [255] * 8
        snapshot[udg_addr:udg_addr + 8 * step:step] = udg_data
        snapshot[mask_addr:mask_addr + 8 * step:step] = udg_mask
        macro = '#UDG{0},{1},{2},{3},{4}:{5},{6}{{{7},{8},{9},{10}}}({11})'.format(udg_addr, attr, scale, step, inc, mask_addr, step, x, y, w, h, udg_fname)
        output = writer.expand(macro, ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))
        udg_array = [[Udg(attr, udg_data, udg_mask)]]
        self._check_image(writer.image_writer, udg_array, scale, True, x, y, w, h)

    def test_macro_udg_with_custom_udg_image_path(self):
        font_path = 'graphics/udgs'
        ref = '[Paths]\nUDGImagePath={}'.format(font_path)
        writer = self._get_writer(ref=ref, snapshot=[0] * 8)
        img_fname = 'udg0'
        exp_img_path = '{}/{}.png'.format(font_path, img_fname)

        output = writer.expand('#UDG0({})'.format(img_fname), ASMDIR)
        self.img_equals(output, img_fname, '../{}'.format(exp_img_path))
        self.assertEqual(writer.image_writer.img_file, exp_img_path)

    def test_macro_udg_invalid(self):
        writer = self._get_writer(snapshot=[0] * 8)
        prefix = ERROR_PREFIX.format('UDG')

        # No parameters
        self.assert_error(writer, '#UDG', 'No parameters (expected 1)', prefix)

        # Too many parameters
        self.assert_error(writer, '#UDG0,1,2,3,4,5,6,7,8', "Too many parameters (expected 7): '0,1,2,3,4,5,6,7,8'", prefix)

        # Invalid parameter
        self.assert_error(writer, '#UDG0$,1,2', "Cannot parse integer '0$' in parameter string: '0$,1,2'", prefix)

        # No closing bracket
        self.assert_error(writer, '#UDG0(foo', 'No closing bracket: (foo', prefix)

    def test_macro_udgarray(self):
        snapshot = [0] * 65536
        writer = self._get_writer(snapshot=snapshot)

        udg_fname = 'test_udg_array'
        output = writer.expand('#UDGARRAY8;32768-32784-1-8({0})'.format(udg_fname), ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))

        udg_fname = 'test_udg_array2'
        output = writer.expand('#UDGARRAY8,56,2,256,0;32768;32769;32770;32771;32772x12({0})'.format(udg_fname), ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))

        udg_fname = 'test_udg_array3'
        udg_addr = 32768
        mask_addr = 32769
        width = 2
        attr = 5
        scale = 1
        step = 256
        inc = 0
        x, y, w, h = 4, 6, 8, 5
        udg_data = [195] * 8
        udg_mask = [255] * 8
        snapshot[udg_addr:udg_addr + 8 * step:step] = udg_data
        snapshot[mask_addr:mask_addr + 8 * step:step] = udg_mask
        macro = '#UDGARRAY{0},{1},{2},{3},{4};{5}x4:{6}x4{{{7},{8},{9},{10}}}({11})'.format(width, attr, scale, step, inc, udg_addr, mask_addr, x, y, w, h, udg_fname)
        output = writer.expand(macro, ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))
        udg_array = [[Udg(attr, udg_data, udg_mask)] * width] * 2
        self._check_image(writer.image_writer, udg_array, scale, True, x, y, w, h)

        # Flip
        udg_fname = 'test_udg_array4'
        udg = Udg(56, [128, 64, 32, 16, 8, 4, 2, 1])
        udg_addr = 40000
        snapshot[udg_addr:udg_addr + 8] = udg.data
        output = writer.expand('#UDGARRAY1,,,,,1;{0}({1})'.format(udg_addr, udg_fname), ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))
        udg.flip(1)
        self._check_image(writer.image_writer, [[udg]], 2, False, 0, 0, 16, 16)

        # Rotate
        udg_fname = 'test_udg_array5'
        udg = Udg(56, [128, 64, 32, 16, 8, 4, 2, 1])
        udg_addr = 50000
        snapshot[udg_addr:udg_addr + 8] = udg.data
        output = writer.expand('#UDGARRAY1,,,,,,2;{0}({1})'.format(udg_addr, udg_fname), ASMDIR)
        self.img_equals(output, udg_fname, '../{0}/{1}.png'.format(UDGDIR, udg_fname))
        udg.rotate(2)
        self._check_image(writer.image_writer, [[udg]], 2, False, 0, 0, 16, 16)

    def test_macro_udgarray_with_custom_udg_image_path(self):
        font_path = 'udg_images'
        ref = '[Paths]\nUDGImagePath={}'.format(font_path)
        writer = self._get_writer(ref=ref, snapshot=[0] * 8)
        img_fname = 'udgarray0'
        exp_img_path = '{}/{}.png'.format(font_path, img_fname)

        output = writer.expand('#UDGARRAY1;0({})'.format(img_fname), ASMDIR)
        self.img_equals(output, img_fname, '../{}'.format(exp_img_path))
        self.assertEqual(writer.image_writer.img_file, exp_img_path)

    def test_macro_udgarray_invalid(self):
        writer = self._get_writer(snapshot=[0] * 8)
        prefix = ERROR_PREFIX.format('UDGARRAY')

        # No parameters
        self.assert_error(writer, '#UDGARRAY', 'No parameters (expected 1)', prefix)

        # Invalid parameter
        self.assert_error(writer, '#UDGARRAY1,5$,4;0(bar)', "Cannot parse integer '5$' in parameter string: '1,5$,4'", prefix)

        # Invalid UDG address range spec (1)
        self.assert_error(writer, '#UDGARRAY1;0-1$(bar)', 'Invalid address range specification: 0-1$', prefix)

        # Invalid UDG address range spec (2)
        self.assert_error(writer, '#UDGARRAY1;0-1x2x2(bar)', 'Invalid address range specification: 0-1x2x2', prefix)

        # Invalid UDG address range spec (3)
        self.assert_error(writer, '#UDGARRAY1;0-1-2-3-4x5(bar)', 'Invalid address range specification: 0-1-2-3-4x5', prefix)

        # Invalid UDG spec
        self.assert_error(writer, '#UDGARRAY1;0,5-(bar)', "Cannot parse integer '5-' in parameter string: '0,5-'", prefix)

        # Invalid mask address range spec (1)
        self.assert_error(writer, '#UDGARRAY1;0-2:0-2$(bar)', 'Invalid address range specification: 0-2$', prefix)

        # Invalid mask address range spec (2)
        self.assert_error(writer, '#UDGARRAY1;0-1x2:2-3x2x2(bar)', 'Invalid address range specification: 2-3x2x2', prefix)

        # Invalid mask address range spec (3)
        self.assert_error(writer, '#UDGARRAY1;0-1-2-3x9:4-5-6-7-8x9(bar)', 'Invalid address range specification: 4-5-6-7-8x9', prefix)

        # Invalid UDG mask spec
        self.assert_error(writer, '#UDGARRAY1;0,5:8,1x(bar)', "Cannot parse integer '1x' in parameter string: '8,1x'", prefix)

        # Missing filename (1)
        self.assert_error(writer, '#UDGARRAY1;0', 'Missing filename: #UDGARRAY1;0', prefix)

        # Missing filename (2)
        self.assert_error(writer, '#UDGARRAY1;0{0,0}1(foo)', 'Missing filename: #UDGARRAY1;0{0,0}', prefix)

        # No closing bracket
        self.assert_error(writer, '#UDGARRAY1;0(foo', 'No closing bracket: (foo', prefix)

    def test_macro_udgarray_frames(self):
        snapshot = [0] * 65536
        writer = self._get_writer(snapshot=snapshot)

        # Frames
        udg1_addr = 40000
        udg1 = Udg(23, [101] * 8)
        udg2_addr = 40008
        udg2 = Udg(47, [35] * 8)
        udg3_addr = 40016
        udg3 = Udg(56, [19] * 8)
        snapshot[udg1_addr:udg1_addr + 8] = udg1.data
        snapshot[udg2_addr:udg2_addr + 8] = udg2.data
        snapshot[udg3_addr:udg3_addr + 8] = udg3.data
        macro1 = '#UDGARRAY1;{},{}(*foo)'.format(udg1_addr, udg1.attr)
        macro2 = '#UDGARRAY1;{},{}(bar*)'.format(udg2_addr, udg2.attr)
        macro3 = '#UDGARRAY1;{},{}(baz*qux)'.format(udg3_addr, udg3.attr)
        output = writer.expand(macro1, ASMDIR)
        self.assertEqual(output, '')
        output = writer.expand(macro2, ASMDIR)
        self.img_equals(output, 'bar', '../{}/bar.png'.format(UDGDIR))
        output = writer.expand(macro3, ASMDIR)
        self.img_equals(output, 'baz', '../{}/baz.png'.format(UDGDIR))
        delay1 = 93
        delay3 = 47
        fname = 'test_udg_array_frames'
        macro3 = '#UDGARRAY*foo,{};bar;qux,{}({})'.format(delay1, delay3, fname)
        output = writer.expand(macro3, ASMDIR)
        self.img_equals(output, fname, '../{}/{}.png'.format(UDGDIR, fname))
        frame1 = Frame([[udg1]], 2, delay=delay1)
        frame2 = Frame([[udg2]], 2, delay=delay1)
        frame3 = Frame([[udg3]], 2, delay=delay3)
        frames = [frame1, frame2, frame3]
        self._check_animated_image(writer.image_writer, frames)

    def test_macro_udgarray_frames_invalid(self):
        writer = self._get_writer(snapshot=[0] * 8)
        prefix = ERROR_PREFIX.format('UDGARRAY')

        self.assert_error(writer, '#UDGARRAY1;0(*)', 'Missing filename or frame ID: #UDGARRAY1;0(*)', prefix)
        self.assert_error(writer, '#UDGARRAY*,3(foo)', 'Missing frame ID: #UDGARRAY*,3(foo)', prefix)
        self.assert_error(writer, '#UDGARRAY*foo', 'Missing filename: #UDGARRAY*foo', prefix)
        self.assert_error(writer, '#UDGARRAY*foo()', 'Missing filename: #UDGARRAY*foo()', prefix)
        self.assert_error(writer, '#UDGARRAY*foo(bar', 'No closing bracket: (bar', prefix)
        self.assert_error(writer, '#UDGARRAY*foo(bar)', 'No such frame: "foo"', prefix)
        self.assert_error(writer, '#UDGARRAY*foo,qux(bar)', 'Invalid delay parameter: "qux"', prefix)

    def test_macro_udgtable(self):
        src = '\n'.join((
            '(data)',
            '{ =h Col1 | =h Col2 | =h,c2 Cols3+4 }',
            '{ =r2 X   | Y       | Za  | Zb }',
            '{           Y2      | Za2 | =t }'
        ))
        html = """
            <table class="data">
            <tr>
            <th>Col1</th>
            <th>Col2</th>
            <th colspan="2">Cols3+4</th>
            </tr>
            <tr>
            <td rowspan="2">X</td>
            <td>Y</td>
            <td>Za</td>
            <td>Zb</td>
            </tr>
            <tr>
            <td>Y2</td>
            <td>Za2</td>
            <td class="transparent"></td>
            </tr>
            </table>
        """
        writer = self._get_writer()
        output = writer.expand('#UDGTABLE{}\nUDGTABLE#'.format(src), ASMDIR)
        self.assert_html_equal(output, html)

        # Empty table
        output = writer.expand('#UDGTABLE UDGTABLE#', ASMDIR)
        self.assertEqual(output, '<table>\n</table>')

    def test_macro_udgtable_invalid(self):
        writer = self._get_writer()
        prefix = ERROR_PREFIX.format('UDGTABLE')

        # No end marker
        self.assert_error(writer, '#UDGTABLE { A1 }', 'Missing table end marker: #UDGTABLE { A1 }...')

    def test_unsupported_macro(self):
        writer = self._get_writer()
        writer.macros['#BUG'] = self._unsupported_macro
        self.assert_error(writer, '#BUG#bug1', 'Found unsupported macro: #BUG')

    def test_unknown_macro(self):
        writer = self._get_writer()
        for macro, params in (('#FOO', 'xyz'), ('#BAR', '1,2(baz)'), ('#UDGS', '#r1'), ('#LINKS', '')):
            self.assert_error(writer, macro + params, 'Found unknown macro: {}'.format(macro))

    def test_parameter_LinkOperands(self):
        ref = '[Game]\nLinkOperands={}'
        skool = '\n'.join((
            '; Routine at 32768',
            'c32768 RET',
            '',
            '; Routine at 32769',
            'c32769 CALL 32768',
            ' 32772 DEFW 32768',
            ' 32774 DJNZ 32768',
            ' 32776 JP 32768',
            ' 32779 JR 32768',
            ' 32781 LD HL,32768'
        ))
        for param_value in ('CALL,JP,JR', 'CALL,DEFW,djnz,JP,LD'):
            writer = self._get_writer(ref=ref.format(param_value), skool=skool)
            link_operands = tuple(param_value.upper().split(','))
            self.assertEqual(writer.link_operands, link_operands)
            writer.write_asm_entries()
            html = self.read_file(join(ASMDIR, '32769.html'), True)
            link = '<a class="link" href="32768.html">32768</a>'
            line_no = 34
            for prefix in ('CALL ', 'DEFW ', 'DJNZ ', 'JP ', 'JR ', 'LD HL,'):
                inst_type = prefix.split()[0]
                exp_html = prefix + (link if inst_type in link_operands else '32768')
                self.assertEqual(html[line_no], '<td class="instruction">{}</td>'.format(exp_html))
                line_no += 5

    def test_html_escape(self):
        # Check that HTML characters from the skool file are escaped
        skool = 't24576 DEFM "<&>" ; a <= b & b >= c'
        writer = self._get_writer(skool=skool)
        fname = 'test.html'
        writer.write_entry(ASMDIR, writer.entries[24576], fname)
        html = self.read_file(join(ASMDIR, fname))
        self.assertTrue('DEFM "&lt;&amp;&gt;"' in html)
        self.assertTrue('a &lt;= b &amp; b &gt;= c' in html)

    def test_html_no_escape(self):
        # Check that HTML characters from the ref file are not escaped
        ref = '[Bug:test:Test]\n<p>Hello</p>'
        writer = self._get_writer(ref=ref)
        writer.write_bugs()
        html = self.read_file(join(REFERENCE_DIR, 'bugs.html'))
        self.assertTrue('<p>Hello</p>' in html)

    def _test_write_index(self, files, content, ref='', custom_subs=None):
        writer = self._get_writer(ref=ref, skool='')
        for f in files:
            self.write_text_file(path=join(self.odir, GAMEDIR, f))
        writer.write_index()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Index',
            'header_prefix': 'The complete',
            'header_suffix': 'RAM disassembly',
            'path': '',
            'body_class': 'main',
            'content': content
        }
        if custom_subs:
            subs.update(custom_subs)
        self.assert_files_equal('index.html', subs, True)
        self.remove_files()

    def test_write_index_empty(self):
        # Empty index
        files = []
        content = ""
        self._test_write_index(files, content)

    def test_write_index_two_maps(self):
        # Memory map, routines map
        files = [
            join(MAPS_DIR, 'all.html'),
            join(MAPS_DIR, 'routines.html')
        ]
        content = """
            <div class="headerText">Memory maps</div>
            <ul class="indexList">
            <li><a class="link" href="maps/all.html">Everything</a></li>
            <li><a class="link" href="maps/routines.html">Routines</a></li>
            </ul>
        """
        self._test_write_index(files, content)

    def test_write_index_three_maps(self):
        # Memory map, routines map, data map
        files = [
            join(MAPS_DIR, 'all.html'),
            join(MAPS_DIR, 'routines.html'),
            join(MAPS_DIR, 'data.html')
        ]
        content = """
            <div class="headerText">Memory maps</div>
            <ul class="indexList">
            <li><a class="link" href="maps/all.html">Everything</a></li>
            <li><a class="link" href="maps/routines.html">Routines</a></li>
            <li><a class="link" href="maps/data.html">Data</a></li>
            </ul>
        """
        self._test_write_index(files, content)

    def test_write_index_four_maps(self):
        # Memory map, routines map, data map, messages map
        files = [
            join(MAPS_DIR, 'all.html'),
            join(MAPS_DIR, 'routines.html'),
            join(MAPS_DIR, 'data.html'),
            join(MAPS_DIR, 'messages.html')
        ]
        content = """
            <div class="headerText">Memory maps</div>
            <ul class="indexList">
            <li><a class="link" href="maps/all.html">Everything</a></li>
            <li><a class="link" href="maps/routines.html">Routines</a></li>
            <li><a class="link" href="maps/data.html">Data</a></li>
            <li><a class="link" href="maps/messages.html">Messages</a></li>
            </ul>
        """
        self._test_write_index(files, content)

    def test_write_index_other_code(self):
        # Other code
        ref = '\n'.join((
            '[OtherCode:otherCode]',
            'Header=Startup',
            'Index=other/other.html',
            'Path=other',
            'Source=other.skool',
            'Title=Startup code',
            '',
            '[OtherCode:otherCode2]',
            'Header=Loading code',
            'Index=load/index.html',
            'Path=load',
            'Source=load.skool',
            'Title=Load code',
            'Link=Loading code'
        ))
        files = ['other/other.html', 'load/index.html']
        content = """
            <div class="headerText">Other code</div>
            <ul class="indexList">
            <li><a class="link" href="other/other.html">Startup code</a></li>
            <li><a class="link" href="load/index.html">Loading code</a></li>
            </ul>
        """
        self._test_write_index(files, content, ref)

    def test_write_index_custom(self):
        # Defined by [Game], [Index], [Index:*:*], [Links] and [Paths] sections
        title_prefix = 'The woefully incomplete'
        title_suffix = 'disassembly of the RAM'
        ref = '\n'.join((
            '[Game]',
            'TitlePrefix={}'.format(title_prefix),
            'TitleSuffix={}'.format(title_suffix),
            '',
            '[Index]',
            'Reference',
            'MemoryMaps',
            '',
            '[Index:Reference:Reference material]',
            'Bugs',
            'Facts',
            '',
            '[Index:MemoryMaps:RAM maps]',
            'RoutinesMap',
            'MemoryMap',
            '',
            '[Links]',
            'MemoryMap=Entire RAM',
            'Facts=Facts',
            '',
            '[Paths]',
            'MemoryMap=memorymaps/ram.html',
            'RoutinesMap=memorymaps/routines.html',
            'Bugs=ref/bugs.html',
            'Facts=ref/facts.html',
            'Changelog=ref/changelog.html',
        ))
        files = [
            'ref/bugs.html',
            'ref/facts.html',
            'ref/changelog.html',
            'memorymaps/ram.html',
            'memorymaps/routines.html',
            'memorymaps/data.html'
        ]
        content = """
            <div class="headerText">Reference material</div>
            <ul class="indexList">
            <li><a class="link" href="ref/bugs.html">Bugs</a></li>
            <li><a class="link" href="ref/facts.html">Facts</a></li>
            </ul>
            <div class="headerText">RAM maps</div>
            <ul class="indexList">
            <li><a class="link" href="memorymaps/routines.html">Routines</a></li>
            <li><a class="link" href="memorymaps/ram.html">Entire RAM</a></li>
            </ul>
        """
        custom_subs = {
            'header_prefix': title_prefix,
            'header_suffix': title_suffix
        }
        self._test_write_index(files, content, ref, custom_subs)

    def test_write_index_with_custom_link_text(self):
        ref = '\n'.join((
            '[Links]',
            'Bugs=[Bugs] (glitches)',
            'Changelog=Change log',
            'DataMap=Game data',
            'Facts=[Facts] (trivia)',
            'GameStatusBuffer=Workspace',
            'Glossary=List of terms',
            'GraphicGlitches=Graphic bugs',
            'Graphics=UDGs and stuff',
            'MemoryMap=All code and data',
            'MessagesMap=Strings',
            'Pokes=POKEs',
            'RoutinesMap=Game code',
            'UnusedMap=Unused bytes'
        ))
        files = [
            'buffers/gbuffer.html',
            'graphics/glitches.html',
            'graphics/graphics.html',
            'maps/all.html',
            'maps/data.html',
            'maps/messages.html',
            'maps/routines.html',
            'maps/unused.html',
            'reference/bugs.html',
            'reference/changelog.html',
            'reference/facts.html',
            'reference/glossary.html',
            'reference/pokes.html',
        ]
        content = """
            <div class="headerText">Memory maps</div>
            <ul class="indexList">
            <li><a class="link" href="maps/all.html">All code and data</a></li>
            <li><a class="link" href="maps/routines.html">Game code</a></li>
            <li><a class="link" href="maps/data.html">Game data</a></li>
            <li><a class="link" href="maps/messages.html">Strings</a></li>
            <li><a class="link" href="maps/unused.html">Unused bytes</a></li>
            </ul>
            <div class="headerText">Graphics</div>
            <ul class="indexList">
            <li><a class="link" href="graphics/graphics.html">UDGs and stuff</a></li>
            <li><a class="link" href="graphics/glitches.html">Graphic bugs</a></li>
            </ul>
            <div class="headerText">Data tables and buffers</div>
            <ul class="indexList">
            <li><a class="link" href="buffers/gbuffer.html">Workspace</a></li>
            </ul>
            <div class="headerText">Reference</div>
            <ul class="indexList">
            <li><a class="link" href="reference/changelog.html">Change log</a></li>
            <li><a class="link" href="reference/glossary.html">List of terms</a></li>
            <li><a class="link" href="reference/facts.html">Facts</a> (trivia)</li>
            <li><a class="link" href="reference/bugs.html">Bugs</a> (glitches)</li>
            <li><a class="link" href="reference/pokes.html">POKEs</a></li>
            </ul>
        """
        self._test_write_index(files, content, ref)

    def test_write_index_with_custom_footer(self):
        files = []
        content = ""
        release = 'foo'
        c = 'bar'
        created = 'baz'
        ref = '\n'.join((
            '[Info]',
            'Copyright={}',
            'Created={}',
            'Release={}'
        )).format(c, created, release)
        footer = '\n'.join((
            '<div class="footer">',
            '<div class="release">{}</div>',
            '<div class="copyright">{}</div>',
            '<div class="created">{}</div>',
            '</div>',
            '</body>',
            '</html>'
        )).format(release, c, created)
        custom_subs = {'footer': footer}
        self._test_write_index(files, content, ref, custom_subs)

    def test_write_index_empty_with_logo_image(self):
        # Empty index with logo image
        writer = self._get_writer(skool='')
        logo_image_path = 'logo.png'
        writer.game_vars['LogoImage'] = logo_image_path
        self.write_bin_file(path=join(self.odir, GAMEDIR, logo_image_path))
        writer.write_index()
        game = basename(self.skoolfile)[:-6]
        subs = {
            'name': game,
            'title': 'Index',
            'header_prefix': 'The complete',
            'logo': '<img src="{0}" alt="{1}" />'.format(logo_image_path, game),
            'header_suffix': 'RAM disassembly',
            'path': '',
            'body_class': 'main',
            'content': ''
        }
        self.assert_files_equal('index.html', subs, True)

    def test_write_asm_entries(self):
        ref = '\n'.join((
            '[OtherCode:start]',
            'Header=Startup code',
            'Index=start/index.html',
            'Path=start',
            'Source=start.skool',
            'Title=Startup code',
        ))
        skool = '\n'.join((
            '; Routine at 24576',
            ';',
            '; Description of routine at 24576.',
            ';',
            '; A Some value',
            '; B Some other value',
            'c24576 LD A,B  ; Comment for instruction at 24576',
            '; Mid-routine comment above 24577.',
            '*24577 RET',
            '; End comment for routine at 24576.',
            '',
            '; Data block at 24578',
            'b24578 DEFB 0',
            '',
            '; Routine at 24579',
            'c24579 JR 24577',
            '',
            '; GSB entry at 24581',
            'g24581 DEFW 123',
            '',
            '; Unused',
            'u24583 DEFB 0',
            '',
            '; Routine at 24584 (register section but no description)',
            ';',
            '; .',
            ';',
            '; A 0',
            'c24584 CALL 30000  ; {Comment for the instructions at 24584 and 24587',
            ' 24587 JP 30003    ; }',
            '',
            'r30000 start',
            ' 30003',
        ))
        writer = self._get_writer(ref=ref, skool=skool)
        common_subs = {
            'name': basename(self.skoolfile)[:-6],
            'path': '../',
            'body_class': 'disassembly'
        }
        writer.write_asm_entries()

        # Routine at 24576
        content = """
            <div class="description">24576: Routine at 24576</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            <div class="paragraph">
            Description of routine at 24576.
            </div>
            </div>
            <table class="input">
            <tr>
            <td class="register">A</td>
            <td class="registerContents">Some value</td>
            </tr>
            <tr>
            <td class="register">B</td>
            <td class="registerContents">Some other value</td>
            </tr>
            </table>
            </td>
            </tr>
            <tr>
            <td class="label"><a name="24576"></a>24576</td>
            <td class="instruction">LD A,B</td>
            <td class="comment">Comment for instruction at 24576</td>
            </tr>
            <tr>
            <td class="routineComment" colspan="3">
            <a name="24577"></a>
            <div class="comments">
            <div class="paragraph">
            Mid-routine comment above 24577.
            </div>
            </div>
            </td>
            </tr>
            <tr>
            <td class="label">24577</td>
            <td class="instruction">RET</td>
            <td class="comment"></td>
            </tr>
            <tr>
            <td class="routineComment" colspan="3">
            <div class="comments">
            <div class="paragraph">
            End comment for routine at 24576.
            </div>
            </div>
            </td>
            </tr>
            </table>
        """
        subs = {
            'title': 'Routine at 24576',
            'header': 'Routines',
            'up': 24576,
            'next': 24578,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24576.html'), subs)

        # Data at 24578
        content = """
            <div class="description">24578: Data block at 24578</div>
            <table class="dataDisassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="address"><a name="24578"></a>24578</td>
            <td class="instruction">DEFB 0</td>
            <td class="transparentDataComment" />
            </tr>
            </table>
        """
        subs = {
            'title': 'Data at 24578',
            'header': 'Data',
            'prev': 24576,
            'up': 24578,
            'next': 24579,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24578.html'), subs)

        # Routine at 24579
        content = """
            <div class="description">24579: Routine at 24579</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="label"><a name="24579"></a>24579</td>
            <td class="instruction">JR <a class="link" href="24576.html#24577">24577</a></td>
            <td class="transparentComment" />
            </tr>
            </table>
        """
        subs = {
            'title': 'Routine at 24579',
            'header': 'Routines',
            'prev': 24578,
            'up': 24579,
            'next': 24581,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24579.html'), subs)

        # Game status buffer entry at 24581
        content = """
            <div class="description">24581: GSB entry at 24581</div>
            <table class="dataDisassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="address"><a name="24581"></a>24581</td>
            <td class="instruction">DEFW 123</td>
            <td class="transparentDataComment" />
            </tr>
            </table>
        """
        subs = {
            'title': 'Game status buffer entry at 24581',
            'header': 'Game status buffer',
            'prev': 24579,
            'up': 24581,
            'next': 24583,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24581.html'), subs)

        # Unused RAM at 24583
        content = """
            <div class="description">24583: Unused</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="address"><a name="24583"></a>24583</td>
            <td class="instruction">DEFB 0</td>
            <td class="transparentComment" />
            </tr>
            </table>
        """
        subs = {
            'title': 'Unused RAM at 24583',
            'header': 'Unused',
            'prev': 24581,
            'up': 24583,
            'next': 24584,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24583.html'), subs)

        # Routine at 24584
        content = """
            <div class="description">24584: Routine at 24584 (register section but no description)</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            <table class="input">
            <tr>
            <td class="register">A</td>
            <td class="registerContents">0</td>
            </tr>
            </table>
            </td>
            </tr>
            <tr>
            <td class="label"><a name="24584"></a>24584</td>
            <td class="instruction">CALL <a class="link" href="../start/30000.html">30000</a></td>
            <td class="comment" rowspan="2">Comment for the instructions at 24584 and 24587</td>
            </tr>
            <tr>
            <td class="address"><a name="24587"></a>24587</td>
            <td class="instruction">JP <a class="link" href="../start/30000.html#30003">30003</a></td>
            </tr>
            </table>
        """
        subs = {
            'title': 'Routine at 24584',
            'header': 'Routines',
            'prev': 24583,
            'up': 24584,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '24584.html'), subs)

    def test_write_asm_entries_with_decimal_addresses_below_10000(self):
        skool = '\n'.join((
            'c00000 RET',
            '',
            'c00002 RET',
            '',
            'c00044 RET',
            '',
            'c00666 RET',
            '',
            'c08888 RET'
        ))
        entry_template = '\n'.join((
            '<div class="description">{address:05d}: </div>',
            '<table class="disassembly">',
            '<tr>',
            '<td class="routineComment" colspan="3">',
            '<div class="details">',
            '</div>',
            '</td>',
            '</tr>',
            '<tr>',
            '<td class="label"><a name="{address}"></a>{address:05d}</td>',
            '<td class="instruction">RET</td>',
            '<td class="transparentComment" />',
            '</tr>',
            '</table>',
            ''
        ))
        common_subs = {
            'path': '../',
            'body_class': 'disassembly'
        }

        for base in (None, BASE_10):
            writer = self._get_writer(skool=skool, base=BASE_10)
            common_subs['name'] = basename(self.skoolfile)[:-6]
            writer.write_asm_entries()

            # Address 0
            subs = {
                'title': 'Routine at 00000',
                'header': 'Routines',
                'up': 0,
                'next': 2,
                'content': entry_template.format(address=0)
            }
            subs.update(common_subs)
            self.assert_files_equal(join(ASMDIR, '0.html'), subs)

            # Address 2
            subs = {
                'title': 'Routine at 00002',
                'header': 'Routines',
                'prev': 0,
                'up': 2,
                'next': 44,
                'content': entry_template.format(address=2)
            }
            subs.update(common_subs)
            self.assert_files_equal(join(ASMDIR, '2.html'), subs)

            # Address 44
            subs = {
                'title': 'Routine at 00044',
                'header': 'Routines',
                'prev': 2,
                'up': 44,
                'next': 666,
                'content': entry_template.format(address=44)
            }
            subs.update(common_subs)
            self.assert_files_equal(join(ASMDIR, '44.html'), subs)

            # Address 666
            subs = {
                'title': 'Routine at 00666',
                'header': 'Routines',
                'prev': 44,
                'up': 666,
                'next': 8888,
                'content': entry_template.format(address=666)
            }
            subs.update(common_subs)
            self.assert_files_equal(join(ASMDIR, '666.html'), subs)

            # Address 8888
            subs = {
                'title': 'Routine at 08888',
                'header': 'Routines',
                'prev': 666,
                'up': 8888,
                'content': entry_template.format(address=8888)
            }
            subs.update(common_subs)
            self.assert_files_equal(join(ASMDIR, '8888.html'), subs)

    def test_asm_labels(self):
        skool = '\n'.join((
            '; Routine with a label',
            '; @label=START',
            'c50000 LD B,5     ; Loop 5 times',
            ' 50002 DJNZ 50002',
            ' 50004 RET',
            '',
            '; Routine without a label',
            'c50005 JP 50000',
            '',
            '; DEFW statement with a @keep directive',
            '; @keep',
            'b50008 DEFW 50000',
        ))
        writer = self._get_writer(skool=skool, asm_labels=True)
        common_subs = {
            'name': basename(self.skoolfile)[:-6],
            'path': '../',
            'body_class': 'disassembly'
        }
        writer.write_asm_entries()

        # Routine at 50000
        content = """
            <div class="description">START: 50000: Routine with a label</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="4">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="asmLabel">START</td>
            <td class="label"><a name="50000"></a>50000</td>
            <td class="instruction">LD B,5</td>
            <td class="comment">Loop 5 times</td>
            </tr>
            <tr>
            <td class="asmLabel"></td>
            <td class="address"><a name="50002"></a>50002</td>
            <td class="instruction">DJNZ <a class="link" href="50000.html#50002">50002</a></td>
            <td class="comment"></td>
            </tr>
            <tr>
            <td class="asmLabel"></td>
            <td class="address"><a name="50004"></a>50004</td>
            <td class="instruction">RET</td>
            <td class="comment"></td>
            </tr>
            </table>
        """
        subs = {
            'header': 'Routines',
            'title': 'Routine at 50000 (START)',
            'up': 50000,
            'next': 50005,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '50000.html'), subs)

        # Routine at 50005
        content = """
            <div class="description">50005: Routine without a label</div>
            <table class="disassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="label"><a name="50005"></a>50005</td>
            <td class="instruction">JP <a class="link" href="50000.html">START</a></td>
            <td class="transparentComment" />
            </tr>
            </table>
        """
        subs = {
            'header': 'Routines',
            'title': 'Routine at 50005',
            'prev': 50000,
            'up': 50005,
            'next': 50008,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '50005.html'), subs)

        # DEFW statement at 50008
        content = """
            <div class="description">50008: DEFW statement with a @keep directive</div>
            <table class="dataDisassembly">
            <tr>
            <td class="routineComment" colspan="3">
            <div class="details">
            </div>
            </td>
            </tr>
            <tr>
            <td class="address"><a name="50008"></a>50008</td>
            <td class="instruction">DEFW 50000</td>
            <td class="transparentDataComment" />
            </tr>
            </table>
        """
        subs = {
            'header': 'Data',
            'title': 'Data at 50008',
            'prev': 50005,
            'up': 50008,
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(ASMDIR, '50008.html'), subs)

    def test_write_map(self):
        skool = '\n'.join((
            '; Routine',
            'c30000 RET',
            '',
            '; Bytes',
            'b30001 DEFB 1,2',
            '',
            '; Words',
            'b30003 DEFW 257,65534',
            '',
            '; GSB entry',
            'g30007 DEFB 0',
            '',
            '; Unused',
            'u30008 DEFB 0',
            '',
            '; Zeroes',
            's30009 DEFS 6',
            '',
            '; More zeroes',
            'z30015 DEFS 3',
            '',
            '; Text',
            't30018 DEFM "Hi"'
        ))
        writer = self._get_writer(skool=skool)
        common_subs = {
            'name': basename(self.skoolfile)[:-6],
            'path': '../',
            'body_class': 'map'
        }

        # Memory map
        content = """
            <table class="map">
            <tr>
            <th>Page</th>
            <th>Byte</th>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">48</td>
            <td class="routine"><a class="link" name="30000" href="../asm/30000.html">30000</a></td>
            <td class="routineDesc">Routine</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">49</td>
            <td class="data"><a class="link" name="30001" href="../asm/30001.html">30001</a></td>
            <td class="dataDesc">Bytes</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">51</td>
            <td class="data"><a class="link" name="30003" href="../asm/30003.html">30003</a></td>
            <td class="dataDesc">Words</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">55</td>
            <td class="gbuffer"><a class="link" name="30007" href="../asm/30007.html">30007</a></td>
            <td class="gbufferDesc">GSB entry</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">56</td>
            <td class="unused"><a class="link" name="30008" href="../asm/30008.html">30008</a></td>
            <td class="unusedDesc">Unused (1 byte)</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">57</td>
            <td class="unused"><a class="link" name="30009" href="../asm/30009.html">30009</a></td>
            <td class="unusedDesc">Unused (6 bytes)</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">63</td>
            <td class="unused"><a class="link" name="30015" href="../asm/30015.html">30015</a></td>
            <td class="unusedDesc">Unused (3 bytes)</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">66</td>
            <td class="message"><a class="link" name="30018" href="../asm/30018.html">30018</a></td>
            <td class="messageDesc">Text</td>
            </tr>
            </table>
        """
        writer.write_map(writer.memory_maps['MemoryMap'])
        subs = {
            'title': 'Memory map',
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(MAPS_DIR, 'all.html'), subs)

        # Routines map
        content = """
            <table class="map">
            <tr>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="routine"><a class="link" name="30000" href="../asm/30000.html">30000</a></td>
            <td class="routineDesc">Routine</td>
            </tr>
            </table>
        """
        writer.write_map(writer.memory_maps['RoutinesMap'])
        subs = {
            'title': 'Routines',
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(MAPS_DIR, 'routines.html'), subs)

        # Data map
        content = """
            <table class="map">
            <tr>
            <th>Page</th>
            <th>Byte</th>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">49</td>
            <td class="data"><a class="link" name="30001" href="../asm/30001.html">30001</a></td>
            <td class="dataDesc">Bytes</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">51</td>
            <td class="data"><a class="link" name="30003" href="../asm/30003.html">30003</a></td>
            <td class="dataDesc">Words</td>
            </tr>
            </table>
        """
        writer.write_map(writer.memory_maps['DataMap'])
        subs = {
            'title': 'Data',
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(MAPS_DIR, 'data.html'), subs)

        # Messages map
        content = """
            <table class="map">
            <tr>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="message"><a class="link" name="30018" href="../asm/30018.html">30018</a></td>
            <td class="messageDesc">Text</td>
            </tr>
            </table>
        """
        writer.write_map(writer.memory_maps['MessagesMap'])
        subs = {
            'title': 'Messages',
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(MAPS_DIR, 'messages.html'), subs)

        # Unused map
        content = """
            <table class="map">
            <tr>
            <th>Page</th>
            <th>Byte</th>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">56</td>
            <td class="unused"><a class="link" name="30008" href="../asm/30008.html">30008</a></td>
            <td class="unusedDesc">Unused (1 byte)</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">57</td>
            <td class="unused"><a class="link" name="30009" href="../asm/30009.html">30009</a></td>
            <td class="unusedDesc">Unused (6 bytes)</td>
            </tr>
            <tr>
            <td class="mapPage">117</td>
            <td class="mapByte">63</td>
            <td class="unused"><a class="link" name="30015" href="../asm/30015.html">30015</a></td>
            <td class="unusedDesc">Unused (3 bytes)</td>
            </tr>
            </table>
        """
        writer.write_map(writer.memory_maps['UnusedMap'])
        subs = {
            'title': 'Unused addresses',
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(join(MAPS_DIR, 'unused.html'), subs)

        # Custom map
        content = """
            <div class="mapIntro">Introduction.</div>
            <table class="map">
            <tr>
            <th>Address</th>
            <th>Description</th>
            </tr>
            <tr>
            <td class="routine"><a class="link" name="30000" href="../asm/30000.html">30000</a></td>
            <td class="routineDesc">Routine</td>
            </tr>
            <tr>
            <td class="gbuffer"><a class="link" name="30007" href="../asm/30007.html">30007</a></td>
            <td class="gbufferDesc">GSB entry</td>
            </tr>
            </table>
        """
        map_details = {
            'Path': join(MAPS_DIR, 'custom.html'),
            'Title': 'Custom map',
            'Intro': 'Introduction.',
            'EntryTypes': 'cg'
        }
        writer.write_map(map_details)
        subs = {
            'title': map_details['Title'],
            'content': content
        }
        subs.update(common_subs)
        self.assert_files_equal(map_details['Path'], subs)

    def test_write_memory_map_with_intro(self):
        intro = 'This map is empty.'
        ref = '[MemoryMap:MemoryMap]\nIntro={}'.format(intro)
        writer = self._get_writer(ref=ref, skool='')
        content = """
            <div class="mapIntro">{}</div>
            <table class="map">
            <tr>
            <th>Page</th>
            <th>Byte</th>
            <th>Address</th>
            <th>Description</th>
            </tr>
            </table>
        """.format(intro)
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'path': '../',
            'title': 'Memory map',
            'body_class': 'map',
            'content': content
        }

        writer.write_map(writer.memory_maps['MemoryMap'])
        self.assert_files_equal(join(MAPS_DIR, 'all.html'), subs)

    def test_write_map_with_decimal_addresses_below_10000(self):
        skool = '\n'.join((
            'c00000 RET',
            '',
            'c00002 RET',
            '',
            'c00044 RET',
            '',
            'c00666 RET',
            '',
            'c08888 RET'
        ))
        exp_content = '\n'.join((
            '<table class="map">',
            '<tr>',
            '<th>Page</th>',
            '<th>Byte</th>',
            '<th>Address</th>',
            '<th>Description</th>',
            '</tr>\n'
        ))
        for address in (0, 2, 44, 666, 8888):
            exp_content += '\n'.join((
                '<tr>',
                '<td class="mapPage">{}</td>'.format(address // 256),
                '<td class="mapByte">{}</td>'.format(address % 256),
                '<td class="routine"><a class="link" name="{0}" href="../asm/{0}.html">{0:05d}</a></td>'.format(address),
                '<td class="routineDesc"></td>',
                '</tr>\n'
            ))
        exp_content += '</table>\n'

        # Memory map
        for base in (None, BASE_10):
            writer = self._get_writer(skool=skool, base=base)
            writer.write_map(writer.memory_maps['MemoryMap'])
            subs = {
                'name': basename(self.skoolfile)[:-6],
                'path': '../',
                'title': 'Memory map',
                'body_class': 'map',
                'content': exp_content
            }
            self.assert_files_equal(join(MAPS_DIR, 'all.html'), subs)

    def test_write_data_map_with_custom_title_and_path(self):
        title = 'Data blocks'
        path = 'foo/bar/data.html'
        ref = '\n'.join((
            '[Titles]',
            'DataMap={}',
            '[Paths]',
            'DataMap={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_map(writer.memory_maps['DataMap'])
        self.assert_title_equals(path, title)

    def test_write_memory_map_with_custom_title_and_path(self):
        title = 'All the RAM'
        path = 'memory_map.html'
        ref = '\n'.join((
            '[Titles]',
            'MemoryMap={}',
            '[Paths]',
            'MemoryMap={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_map(writer.memory_maps['MemoryMap'])
        self.assert_title_equals(path, title)

    def test_write_messages_map_with_custom_title_and_path(self):
        title = 'Strings'
        path = 'text/strings.html'
        ref = '\n'.join((
            '[Titles]',
            'MessagesMap={}',
            '[Paths]',
            'MessagesMap={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_map(writer.memory_maps['MessagesMap'])
        self.assert_title_equals(path, title)

    def test_write_routines_map_with_custom_title_and_path(self):
        title = 'All the code'
        path = 'mappage/code.html'
        ref = '\n'.join((
            '[Titles]',
            'RoutinesMap={}',
            '[Paths]',
            'RoutinesMap={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_map(writer.memory_maps['RoutinesMap'])
        self.assert_title_equals(path, title)

    def test_write_unused_map_with_custom_title_and_path(self):
        title = 'Bytes of no use'
        path = 'unused_bytes.html'
        ref = '\n'.join((
            '[Titles]',
            'UnusedMap={}',
            '[Paths]',
            'UnusedMap={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_map(writer.memory_maps['UnusedMap'])
        self.assert_title_equals(path, title)

    def test_write_changelog(self):
        ref = '\n'.join((
            '[Changelog:20120704]',
            'Intro.',
            '',
            '1',
            '  2',
            '    3',
            '    4',
            '  5',
            '',
            '[Changelog:20120703]',
            '-',
            '',
            '1',
            '  2',
            '    3',
        ))
        content = """
            <ul class="linkList">
            <li><a class="link" href="#20120704">20120704</a></li>
            <li><a class="link" href="#20120703">20120703</a></li>
            </ul>
            <div><a name="20120704"></a></div>
            <div class="changelog changelog1">
            <div class="changelogTitle">20120704</div>
            <div class="changelogDesc">Intro.</div>
            <ul class="changelog">
            <li>1
            <ul class="changelog1">
            <li>2
            <ul class="changelog2">
            <li>3</li>
            <li>4</li>
            </ul>
            </li>
            <li>5</li>
            </ul>
            </li>
            </ul>
            </div>
            <div><a name="20120703"></a></div>
            <div class="changelog changelog2">
            <div class="changelogTitle">20120703</div>
            <ul class="changelog">
            <li>1
            <ul class="changelog1">
            <li>2
            <ul class="changelog2">
            <li>3</li>
            </ul>
            </li>
            </ul>
            </li>
            </ul>
            </div>
        """
        writer = self._get_writer(ref=ref, skool='')
        writer.write_changelog()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Changelog',
            'path': '../',
            'body_class': 'changelog',
            'content': content
        }
        self.assert_files_equal(join(REFERENCE_DIR, 'changelog.html'), subs)

    def test_write_changelog_with_custom_title_and_path(self):
        title = 'Log of changes'
        path = 'changes/log.html'
        ref = '\n'.join((
            '[Titles]',
            'Changelog={}',
            '[Paths]',
            'Changelog={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_changelog()
        self.assert_title_equals(path, title)

    def test_write_glossary(self):
        ref = '\n'.join((
            '[Glossary:Term1]',
            'Definition 1.',
            '',
            '[Glossary:Term2]',
            'Definition 2. Paragraph 1.',
            '',
            'Definition 2. Paragraph 2.',
        ))
        content = """
            <ul class="linkList">
            <li><a class="link" href="#term1">Term1</a></li>
            <li><a class="link" href="#term2">Term2</a></li>
            </ul>
            <div><a name="term1"></a></div>
            <div class="box box1">
            <div class="boxTitle">Term1</div>
            <div class="paragraph">
            Definition 1.
            </div>
            </div>
            <div><a name="term2"></a></div>
            <div class="box box2">
            <div class="boxTitle">Term2</div>
            <div class="paragraph">
            Definition 2. Paragraph 1.
            </div>
            <div class="paragraph">
            Definition 2. Paragraph 2.
            </div>
            </div>
        """
        writer = self._get_writer(ref=ref, skool='')
        writer.write_glossary()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Glossary',
            'path': '../',
            'body_class': 'glossary',
            'content': content
        }
        self.assert_files_equal(join(REFERENCE_DIR, 'glossary.html'), subs)

    def test_write_glossary_with_custom_title_and_path(self):
        title = 'Terminology'
        path = 'terminology.html'
        ref = '\n'.join((
            '[Titles]',
            'Glossary={}',
            '[Paths]',
            'Glossary={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_glossary()
        self.assert_title_equals(path, title)

    def test_write_graphics(self):
        ref = '[Graphics]\n<em>This is the graphics page.</em>'
        writer = self._get_writer(ref=ref, skool='')
        writer.write_graphics()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Graphics',
            'path': '../',
            'body_class': 'graphics',
            'content': '<em>This is the graphics page.</em>\n'
        }
        self.assert_files_equal(join(GRAPHICS_DIR, 'graphics.html'), subs)

    def test_write_graphics_with_custom_title_and_path(self):
        title = 'Sprites and stuff'
        path = 'sprites_and_stuff.html'
        ref = '\n'.join((
            '[Titles]',
            'Graphics={}',
            '[Paths]',
            'Graphics={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_graphics()
        self.assert_title_equals(path, title)

    def test_write_page(self):
        ref = '\n'.join((
            '[Page:CustomPage]',
            'Title=Custom page',
            'Path=page.html',
            'JavaScript=test-html.js',
            '',
            '[PageContent:CustomPage]',
            '<b>This is the content of the custom page.</b>',
        ))
        writer = self._get_writer(ref=ref, skool='')
        writer.write_page('CustomPage')
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Custom page',
            'path': '',
            'js': 'test-html.js',
            'content': '<b>This is the content of the custom page.</b>\n'
        }
        self.assert_files_equal('page.html', subs)

    def test_write_page_with_body_class(self):
        path = 'custom/page.html'
        body_class = 'custom'
        content = '<i>This is the content of the custom page.</i>'
        ref = '\n'.join((
            '[Page:Custom]',
            'Path={}',
            'BodyClass={}',
            'PageContent={}'
        )).format(path, body_class, content)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_page('Custom')
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Custom',
            'path': '../',
            'body_class': body_class,
            'content': content
        }
        self.assert_files_equal(path, subs)

    def test_write_bugs(self):
        ref = '\n'.join((
            '[Bug:b1:Showstopper]',
            'This bug is bad.',
            '',
            'Really bad.',
        ))
        content = """
            <ul class="linkList">
            <li><a class="link" href="#b1">Showstopper</a></li>
            </ul>
            <div><a name="b1"></a></div>
            <div class="box box1">
            <div class="boxTitle">Showstopper</div>
            <div class="paragraph">
            This bug is bad.
            </div>
            <div class="paragraph">
            Really bad.
            </div>
            </div>
        """
        writer = self._get_writer(ref=ref, skool='')
        writer.write_bugs()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Bugs',
            'path': '../',
            'body_class': 'bugs',
            'content': content
        }
        self.assert_files_equal(join(REFERENCE_DIR, 'bugs.html'), subs)

    def test_write_bugs_with_custom_title_and_path(self):
        title = 'Things that go wrong'
        path = 'ref/wrongness.html'
        ref = '\n'.join((
            '[Titles]',
            'Bugs={}',
            '[Paths]',
            'Bugs={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_bugs()
        self.assert_title_equals(path, title)

    def test_write_facts(self):
        ref = '\n'.join((
            '[Fact:f1:Interesting fact]',
            'Hello.',
            '',
            'Goodbye.',
            '',
            '[Fact:f2:Another interesting fact]',
            'Yes.',
        ))
        content = """
            <ul class="linkList">
            <li><a class="link" href="#f1">Interesting fact</a></li>
            <li><a class="link" href="#f2">Another interesting fact</a></li>
            </ul>
            <div><a name="f1"></a></div>
            <div class="box box1">
            <div class="boxTitle">Interesting fact</div>
            <div class="paragraph">
            Hello.
            </div>
            <div class="paragraph">
            Goodbye.
            </div>
            </div>
            <div><a name="f2"></a></div>
            <div class="box box2">
            <div class="boxTitle">Another interesting fact</div>
            <div class="paragraph">
            Yes.
            </div>
            </div>
        """
        writer = self._get_writer(ref=ref, skool='')
        writer.write_facts()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Trivia',
            'path': '../',
            'body_class': 'facts',
            'content': content
        }
        self.assert_files_equal(join(REFERENCE_DIR, 'facts.html'), subs)

    def test_write_facts_with_custom_title_and_path(self):
        title = 'Things that are true'
        path = 'true_stuff.html'
        ref = '\n'.join((
            '[Titles]',
            'Facts={}',
            '[Paths]',
            'Facts={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_facts()
        self.assert_title_equals(path, title)

    def test_write_pokes(self):
        html = """
            <ul class="linkList">
            <li><a class="link" href="#p1">Infinite everything</a></li>
            </ul>
            <div><a name="p1"></a></div>
            <div class="box box1">
            <div class="boxTitle">Infinite everything</div>
            <div class="paragraph">
            POKE 12345,0
            </div>
            </div>
        """
        ref = '[Poke:p1:Infinite everything]\nPOKE 12345,0'
        writer = self._get_writer(ref=ref, skool='')
        writer.write_pokes()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Pokes',
            'path': '../',
            'body_class': 'pokes',
            'content': html
        }
        self.assert_files_equal(join(REFERENCE_DIR, 'pokes.html'), subs)

    def test_write_pokes_with_custom_title_and_path(self):
        title = 'Hacking the game'
        path = 'qux/xyzzy/hacks.html'
        ref = '\n'.join((
            '[Titles]',
            'Pokes={}',
            '[Paths]',
            'Pokes={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_pokes()
        self.assert_title_equals(path, title)

    def test_write_graphic_glitches(self):
        ref = '[GraphicGlitch:g0:Wrong arms]\nHello.'
        content = """
            <ul class="linkList">
            <li><a class="link" href="#g0">Wrong arms</a></li>
            </ul>
            <div><a name="g0"></a></div>
            <div class="box box1">
            <div class="boxTitle">Wrong arms</div>
            <div class="paragraph">
            Hello.
            </div>
            </div>
        """
        writer = self._get_writer(ref=ref, skool='')
        writer.write_graphic_glitches()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Graphic glitches',
            'path': '../',
            'body_class': 'graphics',
            'content': content
        }
        self.assert_files_equal(join(GRAPHICS_DIR, 'glitches.html'), subs)

    def test_write_graphic_glitches_with_custom_title_and_path(self):
        title = 'Bugs with the graphics'
        path = 'cgi/graphic_bugs.html'
        ref = '\n'.join((
            '[Titles]',
            'GraphicGlitches={}',
            '[Paths]',
            'GraphicGlitches={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_graphic_glitches()
        self.assert_title_equals(path, title)

    def test_write_gbuffer(self):
        ref = '[Game]\nGameStatusBufferIncludes=30003,30004'
        skool = '\n'.join((
            '; GSB entry 1',
            ';',
            '; Number of lives.',
            'g30000 DEFB 4',
            '',
            '; GSB entry 2',
            'g30001 DEFW 78',
            '',
            '; Message ID',
            't30003 DEFB 0',
            '',
            '; Another message ID',
            't30004 DEFB 0',
            '',
            '; Not a game status buffer entry',
            'c30005 RET',
            '',
            'i30006',
        ))
        content = """
            <table class="gbuffer">
            <tr>
            <th>Address</th>
            <th>Length</th>
            <th>Purpose</th>
            </tr>
            <tr>
            <td class="gbufAddress"><a name="30000" class="link" href="../asm/30000.html">30000</a></td>
            <td class="gbufLength">1</td>
            <td class="gbufDesc">
            <div class="gbufDesc">GSB entry 1</div>
            <div class="gbufDetails">
            <div class="paragraph">
            Number of lives.
            </div>
            </div>
            </td>
            </tr>
            <tr>
            <td class="gbufAddress"><a name="30001" class="link" href="../asm/30001.html">30001</a></td>
            <td class="gbufLength">2</td>
            <td class="gbufDesc">
            <div class="gbufDesc">GSB entry 2</div>
            </td>
            </tr>
            <tr>
            <td class="gbufAddress"><a name="30003" class="link" href="../asm/30003.html">30003</a></td>
            <td class="gbufLength">1</td>
            <td class="gbufDesc">
            <div class="gbufDesc">Message ID</div>
            </td>
            </tr>
            <tr>
            <td class="gbufAddress"><a name="30004" class="link" href="../asm/30004.html">30004</a></td>
            <td class="gbufLength">1</td>
            <td class="gbufDesc">
            <div class="gbufDesc">Another message ID</div>
            </td>
            </tr>
            </table>
        """
        writer = self._get_writer(ref=ref, skool=skool)
        writer.write_gbuffer()
        subs = {
            'name': basename(self.skoolfile)[:-6],
            'title': 'Game status buffer',
            'path': '../',
            'body_class': 'gbuffer',
            'content': content
        }
        self.assert_files_equal(join(BUFFERS_DIR, 'gbuffer.html'), subs)

    def test_write_gbuffer_with_custom_title_and_path(self):
        title = 'Workspace'
        path = 'game/status_buffer.html'
        ref = '\n'.join((
            '[Titles]',
            'GameStatusBuffer={}',
            '[Paths]',
            'GameStatusBuffer={}'
        )).format(title, path)
        writer = self._get_writer(ref=ref, skool='')
        writer.write_gbuffer()
        self.assert_title_equals(path, title)

    def test_index_page_id(self):
        ref = '\n'.join((
            '[OtherCode:secondary]',
            'Source=secondary.skool',
            'Path=secondary',
            'Index=secondary/secondary.html',
            'Title=Secondary code',
            'Header=Secondary code',
            'IndexPageId=SecondaryCode',
        ))
        writer = self._get_writer(ref=ref)
        self.assertTrue('SecondaryCode' in writer.paths)
        self.assertEqual(writer.paths['SecondaryCode'], 'secondary/secondary.html')

    def test_page_content(self):
        ref = '[Page:ExistingPage]\nContent=asm/32768.html'
        writer = self._get_writer(ref=ref)
        self.assertFalse('ExistingPage' in writer.page_ids)
        self.assertTrue('ExistingPage' in writer.paths)
        self.assertTrue(writer.paths['ExistingPage'], 'asm/32768.html')

    def test_get_udg_addresses(self):
        writer = self._get_writer(snapshot=())
        addr_specs = [
            (0, 1, [0]),
            ('1', 1, [1]),
            ('2x3', 1, [2] * 3),
            ('0-3', 1, [0, 1, 2, 3]),
            ('0-2x3', 1, [0, 1, 2] * 3),
            ('0-6-2', 1, [0, 2, 4, 6]),
            ('0-6-3x2', 1, [0, 3, 6] * 2),
            ('0-49-1-16', 2, [0, 1, 16, 17, 32, 33, 48, 49]),
            ('0-528-8-256x4', 3, [0, 8, 16, 256, 264, 272, 512, 520, 528] * 4)
        ]
        for addr_spec, width, exp_addresses in addr_specs:
            self.assertEqual(writer._get_udg_addresses(addr_spec, width), exp_addresses)

    def test_get_snapshot_name(self):
        writer = self._get_writer()
        names = ['snapshot1', 'next', 'final']
        for name in names:
            writer.push_snapshot(name)
        while names:
            self.assertEqual(writer.get_snapshot_name(), names.pop())
            writer.pop_snapshot()

    def test_should_write_map(self):
        ref = '[MemoryMap:UnusedMap]\nWrite=0'
        skool = '\n'.join((
            '; Routine',
            'c40000 RET',
            '',
            '; Data',
            'b40001 DEFB 0',
            '',
            '; Unused',
            'u40002 DEFB 0',
        ))
        writer = self._get_writer(ref=ref, skool=skool)
        self.assertTrue(writer.should_write_map(writer.memory_maps['MemoryMap']))
        self.assertTrue(writer.should_write_map(writer.memory_maps['RoutinesMap']))
        self.assertTrue(writer.should_write_map(writer.memory_maps['DataMap']))
        self.assertFalse(writer.should_write_map(writer.memory_maps['MessagesMap']))
        self.assertFalse(writer.should_write_map(writer.memory_maps['UnusedMap']))

    def test_write_registers(self):
        writer = self._get_writer(snapshot=())

        # Traditional
        html = """
            <table class="input">
            <tr>
            <td class="register">A</td>
            <td class="registerContents">Some value</td>
            </tr>
            <tr>
            <td class="register">B</td>
            <td class="registerContents">Some other value</td>
            </tr>
            </table>
        """
        registers = []
        registers.append(Register('', 'A', 'Some value'))
        registers.append(Register('', 'B', 'Some other value'))
        stream = StringIO()
        writer.write_registers(stream, registers, ASMDIR)
        self.assert_html_equal(stream.getvalue(), html, True)

        # With prefixes
        html = """
            <table class="input">
            <tr>
            <th colspan="2">Input</th>
            </tr>
            <tr>
            <td class="register">A</td>
            <td class="registerContents">Some value</td>
            </tr>
            <tr>
            <td class="register">B</td>
            <td class="registerContents">Some other value</td>
            </tr>
            </table>
            <table class="output">
            <tr>
            <th colspan="2">Output</th>
            </tr>
            <tr>
            <td class="register">D</td>
            <td class="registerContents">The result</td>
            </tr>
            <tr>
            <td class="register">E</td>
            <td class="registerContents">Result flags</td>
            </tr>
            </table>
        """
        writer.game_vars['InputRegisterTableHeader'] = 'Input'
        writer.game_vars['OutputRegisterTableHeader'] = 'Output'
        registers = []
        registers.append(Register('Input', 'A', 'Some value'))
        registers.append(Register('', 'B', 'Some other value'))
        registers.append(Register('Output', 'D', 'The result'))
        registers.append(Register('', 'E', 'Result flags'))
        stream = StringIO()
        writer.write_registers(stream, registers, ASMDIR)
        self.assert_html_equal(stream.getvalue(), html, True)

    def test_write_image(self):
        file_info = MockFileInfo('html', 'test_write_image')
        image_writer = MockImageWriter2()
        writer = HtmlWriter(MockSkoolParser(), RefParser(), file_info, image_writer)

        # PNG
        image_path = 'images/test.png'
        udgs = [[Udg(0, (0,) * 8)]]
        writer.write_image(image_path, udgs)
        self.assertEqual(file_info.path, join(file_info.odir, image_path))
        self.assertEqual(file_info.mode, 'wb')
        self.assertEqual(image_writer.udg_array, udgs)
        self.assertEqual(image_writer.img_format, 'png')
        self.assertEqual(image_writer.scale, 2)
        self.assertFalse(image_writer.mask)
        self.assertEqual(image_writer.x, 0)
        self.assertEqual(image_writer.y, 0)
        self.assertEqual(image_writer.width, 16)
        self.assertEqual(image_writer.height, 16)

        # GIF
        image_path = 'images/test.gif'
        writer.write_image(image_path, udgs)
        self.assertEqual(file_info.path, join(file_info.odir, image_path))
        self.assertEqual(image_writer.img_format, 'gif')

        # Unsupported format
        image_path = 'images/test.jpg'
        with self.assertRaisesRegexp(SkoolKitError, 'Unsupported image file format: {}'.format(image_path)):
            writer.write_image(image_path, udgs)

    def test_write_animated_image_png(self):
        file_info = MockFileInfo('html', 'test_write_animated_png')
        image_writer = MockImageWriter2()
        writer = HtmlWriter(MockSkoolParser(), RefParser(), file_info, image_writer)

        image_path = 'images/test_animated.png'
        frames = object()
        writer.write_animated_image(image_path, frames)
        self.assertEqual(file_info.path, join(file_info.odir, image_path))
        self.assertEqual(file_info.mode, 'wb')
        self.assertEqual(image_writer.frames, frames)
        self.assertEqual(image_writer.img_format, 'png')

    def test_write_animated_image_gif(self):
        file_info = MockFileInfo('html', 'test_write_animated_gif')
        image_writer = MockImageWriter2()
        writer = HtmlWriter(MockSkoolParser(), RefParser(), file_info, image_writer)

        image_path = 'images/test_animated.gif'
        frames = object()
        writer.write_animated_image(image_path, frames)
        self.assertEqual(file_info.path, join(file_info.odir, image_path))
        self.assertEqual(file_info.mode, 'wb')
        self.assertEqual(image_writer.frames, frames)
        self.assertEqual(image_writer.img_format, 'gif')

    def test_write_animated_image_unsupported_format(self):
        file_info = MockFileInfo('html', 'test_write_animated_jpg')
        image_writer = MockImageWriter2()
        writer = HtmlWriter(MockSkoolParser(), RefParser(), file_info, image_writer)

        image_path = 'images/test_animated.jpg'
        with self.assertRaisesRegexp(SkoolKitError, 'Unsupported image file format: {}'.format(image_path)):
            writer.write_animated_image(image_path, None)

    def test_write_header_with_title(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        title = 'Main page'
        cwd = ''
        writer.write_header(ofile, title, cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        game_name = self.skoolfile[:-6]
        self.assertEqual(header[7], '<title>{}: {}</title>'.format(game_name, title))
        self.assertEqual(header[14], '<td class="headerText">{}</td>'.format(title))

    def test_write_header_with_body_class(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        cwd = 'subdir'
        body_class = 'default'
        writer.write_header(ofile, title='', cwd=cwd, body_class=body_class, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        self.assertEqual(header[10], '<body class="{}">'.format(body_class))

    def test_write_header_with_body_title(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        cwd = 'subdir'
        body_title = 'ABCD'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=body_title, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        game_name = self.skoolfile[:-6]
        self.assertEqual(header[14], '<td class="headerText">{}</td>'.format(body_title))

    def test_write_header_with_single_global_js(self):
        global_js = 'js/global.js'
        ref = '[Game]\nJavaScript={}'.format(global_js)
        writer = self._get_writer(ref=ref, skool='')
        ofile = StringIO()
        cwd = 'subdir/subdir2'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None)
        header = ofile.getvalue().split('\n')
        js_path = FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['JavaScriptPath'], basename(global_js)))
        self.assertEqual(header[9], '<script type="text/javascript" src="{}"></script>'.format(js_path))

    def test_write_header_with_multiple_global_js(self):
        js_files = ['js/global1.js', 'js.global2.js']
        global_js = ';'.join(js_files)
        ref = '[Game]\nJavaScript={}'.format(global_js)
        writer = self._get_writer(ref=ref, skool='')
        ofile = StringIO()
        cwd = 'subdir/subdir2'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None)
        header = ofile.getvalue().split('\n')
        js_paths = [FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['JavaScriptPath'], basename(js))) for js in js_files]
        self.assertEqual(header[9], '<script type="text/javascript" src="{}"></script>'.format(js_paths[0]))
        self.assertEqual(header[10], '<script type="text/javascript" src="{}"></script>'.format(js_paths[1]))

    def test_write_header_with_single_local_js(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        cwd = 'subdir/subdir2'
        js = 'js/script.js'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=js)
        header = ofile.getvalue().split('\n')
        js_path = FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['JavaScriptPath'], basename(js)))
        self.assertEqual(header[9], '<script type="text/javascript" src="{}"></script>'.format(js_path))

    def test_write_header_with_multiple_local_js(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        cwd = 'subdir'
        js_files = ['js/script1.js', 'js/script2.js']
        js = ';'.join(js_files)
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=js)
        header = ofile.getvalue().split('\n')
        js_paths = [FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['JavaScriptPath'], basename(js))) for js in js_files]
        self.assertEqual(header[9], '<script type="text/javascript" src="{}"></script>'.format(js_paths[0]))
        self.assertEqual(header[10], '<script type="text/javascript" src="{}"></script>'.format(js_paths[1]))

    def test_write_header_with_local_and_global_js(self):
        global_js_files = ['js/global1.js', 'js.global2.js']
        global_js = ';'.join(global_js_files)
        local_js_files = ['js/local1.js', 'js/local2.js']
        local_js = ';'.join(local_js_files)
        ref = '[Game]\nJavaScript={}'.format(global_js)
        writer = self._get_writer(ref=ref, skool='')
        ofile = StringIO()
        cwd = 'subdir/subdir2'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=local_js)
        header = ofile.getvalue().split('\n')
        for i, js in enumerate(global_js_files + local_js_files, 9):
            js_path = FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['JavaScriptPath'], basename(js)))
            self.assertEqual(header[i], '<script type="text/javascript" src="{}"></script>'.format(js_path))

    def test_write_header_with_single_css(self):
        css = 'css/game.css'
        ref = '[Game]\nStyleSheet={}'.format(css)
        writer = self._get_writer(ref=ref, skool='')
        ofile = StringIO()
        cwd = ''
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        css_path = FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['StyleSheetPath'], basename(css)))
        self.assertEqual(header[8], '<link rel="stylesheet" type="text/css" href="{}" />'.format(css_path))

    def test_write_header_with_multiple_css(self):
        css_files = ['css/game.css', 'css/foo.css']
        ref = '[Game]\nStyleSheet={}'.format(';'.join(css_files))
        writer = self._get_writer(ref=ref, skool='')
        ofile = StringIO()
        cwd = ''
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        css_paths = [FileInfo.relpath(cwd, '{}/{}'.format(writer.paths['StyleSheetPath'], basename(css))) for css in css_files]
        self.assertEqual(header[8], '<link rel="stylesheet" type="text/css" href="{}" />'.format(css_paths[0]))
        self.assertEqual(header[9], '<link rel="stylesheet" type="text/css" href="{}" />'.format(css_paths[1]))

    def test_write_header_no_game_name(self):
        writer = self._get_writer(skool='')
        ofile = StringIO()
        cwd = ''
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        game_name = self.skoolfile[:-6]
        self.assertEqual(header[10], '<body>')
        self.assertEqual(header[13], '<td class="headerLogo"><a class="link" href="{}">{}</a></td>'.format(index, game_name))

    def test_write_header_with_game_name(self):
        game_name = 'Some game'
        writer = self._get_writer(ref='[Game]\nGame={}'.format(game_name), skool='')
        ofile = StringIO()
        cwd = 'subdir'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        self.assertEqual(header[13], '<td class="headerLogo"><a class="link" href="{}">{}</a></td>'.format(index, game_name))

    def test_write_header_with_nonexistent_logo_image(self):
        writer = self._get_writer(ref='[Game]\nLogoImage=images/nonexistent.png', skool='')
        ofile = StringIO()
        cwd = 'subdir'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        game_name = self.skoolfile[:-6]
        self.assertEqual(header[13], '<td class="headerLogo"><a class="link" href="{}">{}</a></td>'.format(index, game_name))

    def test_write_header_with_logo_image(self):
        logo_image_fname = 'logo.png'
        ref = '[Game]\nLogoImage={}'.format(logo_image_fname)
        writer = self._get_writer(ref=ref, skool='')
        logo_image = self.write_bin_file(path=join(writer.file_info.odir, logo_image_fname))
        ofile = StringIO()
        cwd = 'subdir/subdir2'
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        logo = FileInfo.relpath(cwd, logo_image_fname)
        game_name = self.skoolfile[:-6]
        self.assertEqual(header[13], '<td class="headerLogo"><a class="link" href="{}"><img src="{}" alt="{}" /></a></td>'.format(index, logo, game_name))

    def test_write_header_with_logo(self):
        logo = 'ABC #UDG30000 123'
        writer = self._get_writer(ref='[Game]\nLogo={}'.format(logo), skool='')
        ofile = StringIO()
        cwd = ''
        writer.write_header(ofile, title='', cwd=cwd, body_class=None, body_title=None, js=None)
        header = ofile.getvalue().split('\n')
        index = FileInfo.relpath(cwd, writer.paths['GameIndex'])
        logo_value = writer.expand(logo, cwd)
        self.assertEqual(header[13], '<td class="headerLogo"><a class="link" href="{}">{}</a></td>'.format(index, logo_value))

class UdgTest(SkoolKitTestCase):
    def test_flip(self):
        udg = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg.flip(0)
        self.assertEqual(udg.data, [1, 2, 4, 8, 16, 32, 64, 128])
        self.assertEqual(udg.mask, [1, 2, 4, 8, 16, 32, 64, 128])

        udg = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg.flip(1)
        self.assertEqual(udg.data, [128, 64, 32, 16, 8, 4, 2, 1])
        self.assertEqual(udg.mask, [128, 64, 32, 16, 8, 4, 2, 1])

        udg = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [2, 4, 6, 8, 10, 12, 14, 16])
        udg.flip(2)
        self.assertEqual(udg.data, [8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual(udg.mask, [16, 14, 12, 10, 8, 6, 4, 2])

        udg = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1])
        udg.flip(3)
        self.assertEqual(udg.data, [16, 224, 96, 160, 32, 192, 64, 128])
        self.assertEqual(udg.mask, [128, 64, 192, 32, 160, 96, 224, 16])

    def test_rotate(self):
        udg = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg.rotate(0)
        self.assertEqual(udg.data, [1, 2, 4, 8, 16, 32, 64, 128])
        self.assertEqual(udg.mask, [1, 2, 4, 8, 16, 32, 64, 128])

        udg = Udg(0, [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 4, 8, 16, 32, 64, 128])
        udg.rotate(1)
        self.assertEqual(udg.data, [128, 64, 32, 16, 8, 4, 2, 1])
        self.assertEqual(udg.mask, [128, 64, 32, 16, 8, 4, 2, 1])

        udg = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1])
        udg.rotate(2)
        self.assertEqual(udg.data, [16, 224, 96, 160, 32, 192, 64, 128])
        self.assertEqual(udg.mask, [128, 64, 192, 32, 160, 96, 224, 16])

        udg = Udg(0, [1, 2, 3, 4, 5, 6, 7, 8], [255, 254, 253, 252, 251, 250, 249, 248])
        udg.rotate(3)
        self.assertEqual(udg.data, [170, 102, 30, 1, 0, 0, 0, 0])
        self.assertEqual(udg.mask, [170, 204, 240, 255, 255, 255, 255, 255])

    def test_copy(self):
        udg = Udg(23, [1] * 8)
        replica = udg.copy()
        self.assertEqual(udg.attr, replica.attr)
        self.assertEqual(udg.data, replica.data)
        self.assertEqual(udg.mask, replica.mask)
        self.assertFalse(udg.data is replica.data)

        udg = Udg(47, [2] * 8, [3] * 8)
        replica = udg.copy()
        self.assertEqual(udg.attr, replica.attr)
        self.assertEqual(udg.data, replica.data)
        self.assertEqual(udg.mask, replica.mask)
        self.assertFalse(udg.data is replica.data)
        self.assertFalse(udg.mask is replica.mask)

    def test_eq(self):
        udg1 = Udg(1, [7] * 8)
        udg2 = Udg(1, [7] * 8)
        udg3 = Udg(2, [7] * 8)
        self.assertTrue(udg1 == udg2)
        self.assertFalse(udg1 == udg3)
        self.assertFalse(udg1 == 1)

    def test_repr(self):
        udg1 = Udg(1, [2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(repr(udg1), 'Udg(1, [2, 3, 4, 5, 6, 7, 8, 9])')

        udg2 = Udg(1, [2] * 8, [3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(repr(udg2), 'Udg(1, [2, 2, 2, 2, 2, 2, 2, 2], [3, 4, 5, 6, 7, 8, 9, 10])')

if __name__ == '__main__':
    unittest.main()
