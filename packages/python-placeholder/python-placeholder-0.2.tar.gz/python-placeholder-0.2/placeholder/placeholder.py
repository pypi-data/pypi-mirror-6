#!/usr/bin/python
# -*- coding: utf-8 -*-

# placeholder.py --- short description
#
# Copyright  (C)  2010  Martin Marcher <martin@marcher.name>
#
# Version:
# Keywords:
# Author: Martin Marcher <martin@marcher.name>
# Maintainer: Martin Marcher <martin@marcher.name>
# URL: http://
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
__docformat__ = u'restructuredtext en'


import os
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
from PIL import ImageFont
from PIL import ImageOps


get_color = lambda name: ImageColor.getrgb(name)

class PlaceHolderImage(object):
    """Create an image useable for wireframing websites.
    """

    def __init__(self, width, height, path,
                 fg_color=get_color('black'),
                 bg_color=get_color('grey'),
                 text=None,
                 font=u'Verdana.ttf',
                 fontsize=42,
                 encoding=u'unic',
                 mode='RGBA',
                 fmt=u'PNG'):

        self.path = path
        self.width = width
        self.height = height
        self.size = width, height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.text = text if text else '{0}x{1}'.format(width, height)
        self.font = font
        self.fontsize = fontsize
        self.encoding = encoding
        self.mode = mode
        self.fmt = fmt

    def save_image(self):
        try:
            font = ImageFont.truetype(self.font, size=self.fontsize, encoding=self.encoding)
        except IOError:
            font = ImageFont.load_default()

        result_img = Image.new(self.mode, self.size, self.bg_color)

        text_size = font.getsize(self.text)
        text_img = Image.new("RGBA", self.size, self.bg_color)

        #position for the text:
        left = self.size[0] / 2 - text_size[0] / 2
        top = self.size[1] / 2 - text_size[1] / 2

        drawing = ImageDraw.Draw(text_img)
        drawing.text((left, top),
                     self.text,
                     font=font,
                     fill=self.fg_color)

        txt_img = ImageOps.fit(text_img, self.size, method=Image.BICUBIC, centering=(0.5, 0.5))

        result_img.paste(txt_img)
        txt_img.save(self.path, self.fmt)




