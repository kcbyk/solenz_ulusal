#!/usr/bin/env python3
"""Generate Android TV launcher banner (320x180) and icon (160x160). Requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

base = Path(__file__).resolve().parent.parent / 'android-tv/app/src/main/res/drawable-xhdpi'
base.mkdir(parents=True, exist_ok=True)
font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def image(size, banner=False):
    w, h = size
    im = Image.new('RGB', size, '#071324')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, w-4, h-4), radius=24, outline='#2ac7ee', width=3)
    if banner:
        d.rounded_rectangle((20, 37, 110, 127), radius=22, fill='#102b3c', outline='#44d8f3', width=3)
        d.polygon([(53, 54), (53, 110), (92, 82)], fill='#b5f5ff')
        d.text((126, 55), 'SOLENZ', font=ImageFont.truetype(font, 26), fill='#f6faff')
        d.text((127, 90), 'CANLI TV', font=ImageFont.truetype(font, 17), fill='#3ee0ff')
    else:
        d.rounded_rectangle((26, 26, 134, 134), radius=28, fill='#102b3c', outline='#44d8f3', width=4)
        d.polygon([(61, 48), (61, 114), (109, 81)], fill='#b5f5ff')
        d.text((55, 135), 'TV', font=ImageFont.truetype(font, 14), fill='#e5faff')
    return im

image((320, 180), True).save(base / 'tv_banner.png')
image((160, 160)).save(base / 'ic_launcher.png')
print('Launcher assets:', base)
