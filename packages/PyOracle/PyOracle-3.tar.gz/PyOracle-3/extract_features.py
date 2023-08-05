'''
extract_features.py
feature extraction for PyOracle

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

import pyoracle
import shelve

# file to analyze
filename = 'mmp_proj/audio/LM_COMP_no_silence-157rep.wav'
fftsize = 8192
hopsize = 8192

features = pyoracle.make_features(filename, fftsize, hopsize, todo=['mfcc', 'chroma', 'rms'])

# make new shelve db
s = shelve.open('LM_features_8192.txt')
s['features_dict'] = features
s.close()
