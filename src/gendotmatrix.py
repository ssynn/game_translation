#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import bitarray
from bitarray import bitarray
import getopt
import sys
import re

def get_pix(image):
    pixel = image.load()
    width, height = image.size
    bitmap = bitarray()
    for h in range(height):
        for w in range(width):
            # if int(sum(pixel[w, h])) > (255 * 3 / 2):
            if pixel[w, h] > 0:
                bitmap.append(False)
            else:
                bitmap.append(True)
    return bitmap

def get_gb2312_pix(gb2312_code, w, h, usr_font):
    # image = Image.new("RGB", (w, h), (255, 255, 255))
    image = Image.new("1", (w, h), (1))
    d_usr = ImageDraw.Draw(image)
    try:
        unicode_code = gb2312_code.decode('gb2312')
        # d_usr.text((0, 0), unicode_code, (0,0,0), font=usr_font)
        d_usr.text((0, 0), unicode_code, (0), font=usr_font)
    except:
        # d_usr.text((0, 0), u" ", (0,0,0), font=usr_font)
        d_usr.text((0, 0), u" ", (0), font=usr_font)
    return get_pix(image)

def make_fontset(font_width=24, font_height=24, outfilename, truetypefile):

    usr_font = ImageFont.truetype(truetypefile, font_height)
    with open(outfilename, 'wb') as outfile:
        for i in range(0xA1, 0xF8):
            for j in range(0xA1, 0xFF):
                data = get_gb2312_pix(chr(i) + chr(j), font_width, font_height, usr_font)
                data.tofile(outfile)

if __name__ == '__main__':
    main()
