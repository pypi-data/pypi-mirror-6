'''
helpers.py
simple helper functions for PyOracle

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

import cPickle as pickle
import sys
import shelve
import numpy as np
from matplotlib.mlab import find
from math import isnan

try:
    from bregman.suite import *
except:
    print 'bregman suite not imported - hopefully running in max'

features = ['mfcc', 'pitch', 'zerocross', 'brightness', 'centroid', 'rolloff', 'rms']

####################################################################################
# DATA MANGLERS
####################################################################################

def chunks(l, n):
    return [l[i:i+n] for i in xrange(0, len(l), n)]

def normalize(loaded_data):
    """ normalize dictionary of loaded events """
    max_zerocrossings = max([event['zerocrossings'] for event in loaded_data])  
    max_rms = max([event['rms'] for event in loaded_data]) 
    max_centroid = max([event['centroid'] for event in loaded_data]) 
    max_chroma = max(max([event['chroma'] for event in loaded_data]))
    max_mfcc = max(max([event['mfcc'] for event in loaded_data]))
    for event in loaded_data:
        event['rms'] = event['rms'] / (max_rms * 1.0)
        event['centroid'] = event['centroid'] / (max_centroid * 1.0)
        event['chroma'] = [x/max_chroma for x in event['chroma']]
        event['mfcc'] = [x/max_mfcc for x in event['mfcc']]
        event['zerocrossings'] = event['zerocrossings'] / (max_zerocrossings * 1.0) 
    return loaded_data

####################################################################################
# analysis / midi file helper functions
####################################################################################

fft_size = 8192
hop_size = 8192

def set_fft_size(n):
    global fft_size
    fft_size = n

def set_hop_size(n):
    global hop_size
    hop_size = n

def features_to_events(features):
    ''' convert a list of features to a list of events '''
    events = []
    keys = features.keys()

    num_events = len(features[keys[0]])

    # changed back to num_events -1
    for i in range(num_events -1):
        new_event = {}
        for key in keys:
            new_event[key] = features[key][i]
        events.append(new_event)    

    return events

def average_events(events, n):
    ''' average n events, in order to increase oracle frame size '''
    new_events = []
    keys = events[0].keys()
    
    for i in range(0, len(events), n):
        block = events[i:i+n]
        tmp_event = {}
        for key in keys:
            # check if we have a vector or a scalar
            try:
                # vector
                l_vec = len(block[0][key]) # length of vector
                feature = [0] * l_vec
                for i in range(l_vec):
                    feature[i] = float(sum([x[key][i] for x in block])) / n
                tmp_event[key] = feature
            except:    
                # scalar
                tmp_event[key] = float(sum([x[key] for x in block])) / n
        new_events.append(tmp_event)
    return new_events

def zerocrossings(filepath, size, h_size):
    ''' calculate and return zero crossings per size-block '''
    x, sr, fmt = wavread(filepath)    
    output_blocks = []
    # modified from https://gist.github.com/255291
    # for each block
    for n in range(0, len(x), h_size):
        current_samples = x[n:n+size]
        indices = find((current_samples[1:] >= 0) & (current_samples[:-1] < 0)) 
        # crossings = sum([1 for m in range(n, n+size) if x[m+1] > 0 and x[m] <= 0])
        output_blocks.append(len(indices))
    return output_blocks

def extract_audio_features(filepath, todo = ['mfcc', 'rms', 'centroid', 'chroma', 'zerocrossings']):
    ''' 
    extract features from an audio file
    input:
        filepath - path to audio file
        todo - a list of features to be extracted
            can be any combination of ['mfcc', 'rms', 'centroid', 'chroma', 'zerocrossings']
    output:
        a dictionary of extracted features
    '''
    # first do mfccs
    features = {}
    if 'mfcc' in todo:
        print 'extracting mfccs...'
        mfcc = MelFrequencyCepstrum(filepath, ncoef=10, log10=True, nfft=fft_size,
                wfft=fft_size, nhop=hop_size)
        # get number of frames - each array in mfcc is one component
        frames = [[0]] * len(mfcc.X[0])
        num_frames = len(mfcc.X[0])
        for i, frame in enumerate(mfcc.X[0]):
            frames[i] = [component[i] for component in mfcc.X]
        features['mfcc'] = frames
    if 'rms' in todo:
        print 'extracting rms...'
        rms = RMS(filepath, nfft=fft_size, wfft=fft_size, nhop=hop_size)
        features['rms'] = rms.X
    if 'centroid' in todo:
        print 'extracting spectral centroid...'
        mf_spec_centroid = MelFrequencySpectrumCentroid(filepath, nfft=fft_size, wfft=fft_size, nhop=hop_size)
        features['centroid'] = mf_spec_centroid.X
    if 'chroma' in todo:
        print 'extracting chroma...'
        chroma = HighQuefrencyChromagram(filepath, log10=True, intensify=True,
                nfft=fft_size, wfft=fft_size, nhop=hop_size)
        chroma_frames = [[0]] * len(chroma.X[0])
        for i, frame in enumerate(chroma.X[0]):
            chroma_frames[i] = [component[i] for component in chroma.X]
        features['chroma'] = chroma_frames
    if 'zerocrossings' in todo:
        print 'extracting zerocrossing rate...'
        features['zerocrossings'] = zerocrossings(filepath, fft_size, hop_size)
        features = block_nans(features)
    print 'done...'
    return features

def block_nans(feat_dict):
    ''' remove NaNs from feature dictionary '''
    features = feat_dict.keys()
    for feature in features:
        nans_removed = []
        try:
            for d in feat_dict[feature]:
                if isnan(d):
                    nans_removed.append(0)
                else:
                    nans_removed.append(d)
        except TypeError:
            nans_removed = feat_dict[feature]
        feat_dict[feature] = np.array(nans_removed)
    return feat_dict

####################################################################################
# oracle file helpers 
####################################################################################

def save_oracle(oracle, filename):
    file = shelve.open(filename)
    file['oracle'] = oracle
    file.close()

def load_oracle(filename):
    file = shelve.open(filename)
    oracle = file['oracle']
    file.close()
    return oracle

