#!/opt/anaconda/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 09 11:31:36 2014

@author: Christoph
"""


import PIL
from PIL import ImageDraw
import numpy as np
from traits.api import HasTraits, Int, Color, List
# Select the QT4 backend, since the wx backend is not
# up to date and crashes for a list of colors.
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'
from traitsui.api import View, Item, Group, CancelButton, OKButton
import pickle
import os

def calc_dh(d):
    r"""
    Calculates the height distance of two rows from the inner row distance
    of two points.
    """
    return np.sqrt(3./4.) * float(d)

def calc_h(nh, r, d):
    r"""
    Calculates the image height.
    
    Parameters
    ==========    
    
    :param nh: int, how many dot rows.
    :param r: int, dot radius.
    :param d: int, half dot distance.
    """
    dh = calc_dh(d)
    return int(nh * 2 * r + nh * 2 * dh)

def calc_w(nw, r, d):
    r"""
    Calculates the image width.
    
    Parameters
    ==========    
    
    :param nh: int, how many dot rows.
    :param r: int, dot radius.
    :param d: int, half dot distance.
    """
    return int(nw * 2 * r + nw * 2 * d)

class DotConfig(HasTraits):
    r"""
    Traits object for one polka dot configuration.
    
    Configuration elements
    ======================
    
    :nh: int, how many dot rows.
    :r: int, dot radius.
    :d: int, half dot distance.
    :nw: int, number of dots per row.
    :bg: color, background color.
    :dotfill: list(color), list of dot colors.
    :im_height: int, 'virtual' property with image height.
    :im_width: int, 'virtual' property with image width.
    """
    r = Int(default_value=5)
    d = Int(default_value=15)
    nw = Int(default_value=65)
    nh = Int(default_value=45)
    im_height = Int(0)
    im_width = Int(0)
    bg = Color
    dotfill = List(trait=Color)
    
    def __init__(self):
        self.on_trait_change(self.update_im_params, ['r','d', 'nw', 'nh'])
        self.update_im_params()
    
    def update_im_params(self):
        self.im_height = calc_h(self.nh, self.r, self.d)
        self.im_width = calc_w(self.nw, self.r, self.d)

# Configure TraitsUI view.
prog_view = View(Group(
                     Group(Item(name='bg', label='Background color'),
                           Item(name='im_height', label='Image height',
                                enabled_when='False'),
                           Item(name='im_width', label='Image widht',
                                enabled_when='False'),
                           label='Image properties',
                           show_border=True),
                     Group(Item(name='r', label='Dot radius'),
                           Item(name='d', label='Dot distance'),
                           Item(name='nw', label='Dots per row'),
                           Item(name='nh', label='Rows'),
                           Item(name='dotfill', label='Colors'),
                           label='Dots',
                           show_border=True),
                     orientation='vertical'),
                 buttons=[CancelButton, OKButton],
                 title='Polka dot generator')

def polka_img(r, d, nw, nh, bg, dotfill):
    r"""
    Generates the polka image for the given parameters.
    
    Params
    ======
    :nh: int, how many dot rows.
    :r: int, dot radius.
    :d: int, half dot distance.
    :nw: int, number of dots per row.
    :bg: color, background color.
    :dotfill: list(color), list of dot colors.    
    """
    dh = calc_dh(d)
    tmp = np.zeros((calc_h(nh, r, d),
                    calc_w(nw, r, d),
                    3),
                   dtype='uint8')
    # Background
    tmp[:, :, :] = bg
    im = PIL.Image.fromarray(tmp)
    draw = ImageDraw.Draw(im)
    # Dots
    for doty in xrange(nh):
        for dotx in xrange(nw+1):
            bbox = (d - (doty % 2) * (r+d) + dotx * 2 * r + dotx * 2 * d,
                    d + doty * 2 * r + doty * 2 * dh,
                    d - (doty % 2) * (r+d) + dotx * 2 * r + dotx * 2 * d + 2 * r,
                    d + doty * 2 * r + doty * 2 * dh + 2 * r)
            if isinstance(dotfill, (list, tuple)):
                if len(dotfill) == 0:
                    raise Exception("At least one color must be specified!")
                realdotfill = dotfill[(dotx + doty * max(len(dotfill) - 2, 1))\
                                        % len(dotfill)]
            else:
                realdotfill = dotfill
            draw.ellipse(bbox, fill=realdotfill)
    return im

# Try to load the dotconfig.
persistence_fn = os.path.join(os.path.expanduser('~'),
                              '.polkadots')
try:
    with open(persistence_fn, 'r') as f:
        dc = pickle.load(f)
except Exception as e:
    print 'Could not load polka-dot config: ' + str(e)
    dc = DotConfig()
# Program loop.
config_change_accepted = True
while(config_change_accepted):
    config_change_accepted = dc.configure_traits(view=prog_view)
    if config_change_accepted:
        im = polka_img(dc.r,
                       dc.d,
                       dc.nw,
                       dc.nh,
                       dc.bg.getRgb()[:3],
                       [color.getRgb()[:3] for color in dc.dotfill])
        im.show()
# Store result.
try:
    with open(persistence_fn, 'w') as f:
        pickle.dump(dc, f)
except Exception as e:
    print 'Could not save polka-dot config: ' + str(e)
