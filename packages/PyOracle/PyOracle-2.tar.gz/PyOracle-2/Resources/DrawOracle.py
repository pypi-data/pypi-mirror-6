'''
DrawOracle.py
drawing routines for PyOracle

Copyright (C) 12.02.2013 Greg Surges

This file is part of PyOracle.

PyOracle is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyOracle is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOracle.  If not, see <http://www.gnu.org/licenses/>.
'''

from random import randint

try:
    from PIL import Image, ImageDraw, ImageFilter #@UnresolvedImport @UnusedImport
except:
    print 'pil not loaded - hopefully running in max'

width = 900 * 4 
height = 400 * 4
oracle = []
image = []

lrs_threshold = 0

def start_draw(_oracle, size=(900*4, 400*4)):
    global oracle
    global image
    global width, height
    width = size[0]
    height = size[1]
    current_state = 0
    image = Image.new('RGB', (size[0], size[1]))
    oracle = _oracle 
    return draw(current_state)

def draw(current_state):
    # handle to Draw object - PIL
    N_states = len(oracle['sfx'])
    draw = ImageDraw.Draw(image)
    
    """Adding compror visualization"""
#     _c = None
#     if N_states > 1:
#         k = N_states - 1
#         _c = oracle['comp'][k]
#         if (_c != None) and (_c[0] != 0):
#             rsl_pos = _c[0]
#             rsl_len = _c[1]
    
    for i in range(N_states):
        # draw circle for each state
        x_pos = (float(i) / N_states * width) + 0.5 * 1.0 / N_states * width
        # iterate over forward transitions
        for tran in oracle['trn'][i]:
            # if forward transition to next state
            if tran == i + 1:
                # draw forward transitions
                next_x = (float(i + 1) / N_states * width) + 0.5 * 1.0 / N_states * width
                current_x = x_pos + (0.25 / N_states * width)
                draw.line((current_x, height/2, next_x, height/2), width=1,fill='white')
            else:
                if oracle['lrs'][tran] >= lrs_threshold:
                    # forward transition to another state
                    current_x = x_pos
                    next_x = (float(tran) / N_states * width) + (0.5 / N_states * width)
                    arc_height = (height / 2) + (tran - i) * 0.125
                    draw.arc((int(current_x), int(height/2 - arc_height/2),
                        int(next_x), int(height/2 + arc_height / 2)), 180, 0,
                        fill='White')
        if oracle['sfx'][i] is not None and oracle['sfx'][i] != 0 and oracle['lrs'][oracle['sfx'][i]] >= lrs_threshold:
            current_x = x_pos
            next_x = (float(oracle['sfx'][i]) / N_states * width) + (0.5 / N_states * width)
            # draw arc
            arc_height = (height / 2) - (oracle['sfx'][i] - i) * 0.125
            draw.arc((int(next_x), 
                      int(height/2 - arc_height/2), 
                      int(current_x), 
                      int(height/2 + arc_height/2)),
                    0,
                    180,
                    fill='White')
    # draw circles on top 
#     for i in range(N_states):
#         color = 'white'
#         if i == current_state:
#             color = 'red'  
#         """ Compror added here"""
#         if _c != None and _c[0] != 0:
#             if (i >= rsl_pos) and (i <= (rsl_pos+rsl_len)):
#                 color = 'blue'
#                 
#         x_pos = (float(i) / N_states * width) + 0.5 * 1.0 / N_states * width
#         circle_width = (0.5 / N_states * width) / 2 
#         draw.ellipse([x_pos - circle_width, height/2 - circle_width,
#             x_pos+circle_width, height/2 + circle_width], outline= color, fill= color)
        
    image.resize((900, 400), (Image.BILINEAR))
    return image
