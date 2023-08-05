'''
pyoracle_demo.py
example of pyoracle.py usage and audio generation

Copyright (C) 12.03.2013 Greg Surges

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

# import the pyoracle high-level functions
from pyoracle import *
import os

# modify this to point to a .WAV file on your system
filepath = os.path.abspath('') + '/prokofiev.wav' 

# specify which features to extract
# can be any or all of the below
todo = ['mfcc', 'chroma', 'rms', 'centroid']

fft_size = 8192
hop_size = fft_size / 2

# call the feature extractors
features = make_features(filepath, fft_size, hop_size, todo)

# calculate ideal distance threshold for chroma feature
thresholds = (0.001, 2.0, 0.01) # specify a range of possible thresholds
ideal_t = calculate_ideal_threshold(thresholds, features, 'chroma')

# ideal threshold is stored in ideal_t[0][1]
print 'ideal distance threshold:', ideal_t[0][1]

# after determining the ideal threshold, we build an oracle using that threshold
thresh = ideal_t[0][1]
oracle = make_oracle(thresh, features, 'chroma')
# then write an image of the oracle to disk
draw_oracle(oracle, 'pyoracle_demo.png', size=(800,300))

# since feature extraction and threshold determination can be time-consuming,
# we can save and load AO structures to disk
save_oracle(oracle, "prokofiev.dat")
loaded_oracle = load_oracle("prokofiev.dat")

# finally, we can use the AO to generate new audio based on the analysis
# for this to work properly, hop_size MUST be fft_size/2
from Resources.generate import generate_audio
fs = 44100 # this is an assumption... 
duration = 60 * fs / hop_size # 60 second duration
generate_audio(filepath, # input filename
               'demo_gen.wav', # output filename
               fft_size, 
               hop_size, 
               oracle, 
               duration,
               0.8, # continuity (0.0 - 1.0) - smaller number means more jumps
               0, # starting frame 
               15) # LRS (shared context between jump points)
