'''
factoracle.py

Audio Oracle (AO) and Factor Oracle (FO) analysis in Python.

This file provides a set of useful, high-level functions for
working with the AO and FO structures.
It also provides methods of calculating the Information Rate (IR)
of a signal compressed via AO.
Finally, helper functions for saving, loading, and visualizing 
AO structures are provided.

Copyright (C) 12.02.2013 Cheng-i Wang, Greg Surges

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

import numpy as np

import Resources.helpers
import Resources.PyOracle.FactOracle
import Resources.PyOracle.IR
import Resources.DrawOracle
import Resources.generate

def make_features(filename, fft_size = 4096, hop_size = 4096, todo = ['mfcc', 'rms', 'centroid', 'chroma', 'zerocrossings']):
    '''
    extract list of features from audio file
    intput:
        filename - path to audio file which will be analyzed
        fft_size - size of each fft frame (in samples)
        hop_size - hop between each fft frame
        todo - a list of features to be extracted
            can contain 'mfcc', 'rms', 'centroid', 'chroma', and/or 'zerocrossings'
    output:
        dictionary containing requested features
            keys are feature names, values are lists of feature vectors
    '''
    Resources.helpers.set_fft_size(fft_size)
    Resources.helpers.set_hop_size(hop_size)
    features = Resources.helpers.extract_audio_features(filename, todo)
    return features

def make_oracle(threshold, flag, features_list, feature, frames_per_state = 1, dfunc = 'euclidian'):
    '''
    the basic AO construction routine
    inputs:
        threshold - distance function theshold
        flag - 'a' or 'f' to select Audio Oracle or Factor Oracle
        features_list - feature vector (from pyoracle.make_features)
        feature - string indicating which feature the oracle should be built on
        frames_per_state - average n analysis frames together to make one oracle state
        dfunc - distance function to use for AO construction. can be 'euclidian' or 'bregman'
    output:
        oracle object
    '''
    events = Resources.helpers.features_to_events(features_list)
    events = Resources.helpers.average_events(events, frames_per_state)
    oracle = Resources.PyOracle.FactOracle.build_oracle(events, flag, threshold, feature, dfunc = dfunc)
    return oracle

def make_weighted_oracle(threshold, flag, features_list, weights):
    '''
    build an oracle with a weighted combination of multiple features
    inputs:
        threshold - distance function theshold
        flag - 'a' or 'f' to select AO or FO 
        features_list - feature vector (from pyoracle.make_features)
        weights - dict() with a weight for each feature in features_list, used
            in computing distance function
    output:
        oracle object
    '''
    events = Resources.helpers.features_to_events(features_list)
    oracle = Resources.PyOracle.FactOracle.build_weighted_oracle(events, flag, threshold, weights)
    return oracle

def calculate_ir(oracle, alpha=1, ir_type='cum'):
    '''
    calculate information rate (IR) for a given oracle
    inputs:
        oracle - an AO or FO object
        alpha - used to maintain positive IR (leave at 1)
        ir_type - select IR estimation method - 'cum', 'old', or 'None'
            'cum' is cumulative alphabet growth, and the default 
    output:
        tuple containing (IR, code, compror)
            IR is the actual IR function.
            code and compror are results of the compression algorithm
            used in IR estimation.
    '''
    if ir_type=='old':
        IR, code, compror = Resources.PyOracle.IR.get_IR_old(oracle)
    elif ir_type=='cum':
        IR, code, compror = Resources.PyOracle.IR.get_IR_cum(oracle,alpha)
    else:
        IR, code, compror = Resources.PyOracle.IR.get_IR(oracle, alpha)
        IR = IR[1]
    return IR, code, compror

def calculate_ideal_threshold(range=(0.0, 1.0, 0.1), features = None, feature =
        None, flag='a', frames_per_state = 1, alpha = 1,  ir_type='cum', dfunc ='euclidian'):
    ''' 
    given a feature vector representing an audio signal, determine the
    best distance threshold - i.e. the one which will create an AO which
    best represents the signal
    inputs:
        range - a tuple of (lowval, highval, stepsize) representing
            a range of possible thresholds
        features - a feature vector from pyoracle.make_features
        feature - string indicating which feature the oracle should be built on
        flag - 'a' or 'f' to select AO or FO
        frames_per_state - average n frames together to make each state
        alpha - used to maintain positive IR (leave at 1)
        ir_type - select IR estimation method - 'cum', 'old', or 'None'
            'cum' is cumulative alphabet growth, and the default 
        dfunc - distance function to use for AO construction. can be 'euclidian' or 'bregman'
    outputs:
        tuple ((total_ir, ideal_t), list_of_ir_thresh_pairs)
            the first value in the tuple is another tuple, containing the ideal
            threshold and the sum of the IR measured from an AO built on that 
            threshold.
            the second value is a list of the other IR/threshold pairs, and
            is useful for plotting
    '''
    thresholds = np.arange(range[0], range[1], range[2])
    # oracles = []
    irs = []

    for threshold in thresholds:
        print 'testing threshold:', threshold
        tmp_oracle = make_oracle(threshold, flag, features, feature, frames_per_state, dfunc = dfunc)
        # oracles.append(tmp_oracle)
        tmp_ir, code, compror = calculate_ir(tmp_oracle, alpha, ir_type)
        # is it a sum?
        if ir_type=='old' or ir_type=='cum':
            irs.append(sum(tmp_ir))
        else:
            irs.append(sum(tmp_ir[1]))
    # now pair irs and thresholds in a vector, and sort by ir
    ir_thresh_pairs = [(a,b) for a, b in zip(irs, thresholds)]
    pairs_return = ir_thresh_pairs
    ir_thresh_pairs = sorted(ir_thresh_pairs, key= lambda x: x[0], reverse = True)
    return ir_thresh_pairs[0], pairs_return 

def calculate_ideal_threshold_and_window(trange=(0.0, 1.0, 0.1), features = None, feature =
        None, flag = 'a', frames_per_state = (1, 1, 1), alpha = 1,  ir_type='cum', dfunc ='euclidian'):
    ''' 
    given a feature vector representing an audio signal, determine the
    best distance threshold - i.e. the one which will create an AO which
    best represents the signal - in combination with the ideal number
    of frames to average together.
    inputs:
        range - a tuple of (lowval, highval, stepsize) representing
            a range of possible thresholds
        features - a feature vector from pyoracle.make_features
        feature - string indicating which feature the oracle should be built on
        flag - 'a' or 'f' to select AO or FO
        frames_per_state - tuple representing a range of frame sizes
        alpha - used to maintain positive IR (leave at 1)
        ir_type - select IR estimation method - 'cum', 'old', or 'None'
            'cum' is cumulative alphabet growth, and the default 
        dfunc - distance function to use for AO construction. can be 'euclidian' or 'bregman'
    outputs:
        tuple ((total_ir, ideal_t, fsize), list_of_ir_thresh_pairs)
            the first value in the tuple is another tuple, containing the ideal
            threshold and frame size, and the sum of the IR measured from
            an AO built on that threshold using that frame size.
            the second value is a list of the other IR/threshold/fsize tuples, and
            is useful for plotting
    '''
    ''' 
    using IR, return optimum distance threshold for a given oracle
    '''
    thresholds = np.arange(trange[0], trange[1], trange[2])
    frame_sizes = np.arange(frames_per_state[0], frames_per_state[1], frames_per_state[2])
    irs = []
    ir_thresh_tups = []

    print 'beginning calculations...'
    for fsize in frame_sizes:
        for threshold in thresholds:
            print 'testing threshold:', threshold, 'with', fsize, 'frames averaged'
            tmp_oracle = make_oracle(threshold, flag, features, feature, fsize, dfunc = dfunc)
            # oracles.append(tmp_oracle)
            tmp_ir, code, compror = calculate_ir(tmp_oracle, alpha, ir_type)
            # is it a sum?
            if ir_type=='old' or ir_type=='cum':
                ir_thresh_tups.append((sum(tmp_ir) * fsize, threshold, fsize))
            else:
                ir_thresh_tups.append((sum(tmp_ir[1]), threshold, fsize))
    # now pair irs and thresholds in a vector, and sort by ir
    pairs_return = ir_thresh_tups
    ir_thresh_tups = sorted(ir_thresh_tups, key= lambda x: x[0], reverse = True)
    return ir_thresh_tups[0], pairs_return 

# def make_transition_matrix(oracle):
#     '''
#     return transition matrix as 2d numpy array
#     '''
#     matrix = np.zeros((len(oracle), len(oracle)), dtype = np.int8) 
#     for i, state in enumerate(oracle):
#         for t in state.transition:
#             matrix[i][t.pointer.number] = 1
#     return matrix
# 
# def make_suffix_vector(oracle):
#     '''
#     return suffix vector as 1d numpy array
#     '''
#     suffix_vector = np.zeros((len(oracle)), np.int16) 
#     for i, state in enumerate(oracle):
#         try:
#             suffix_vector[i] = state.suffix.number
#         except:
#             suffix_vector[i] = 0
#     return suffix_vector
# 
# def save_oracle(oracle, filename):
#     print 'saving to ', filename
#     Resources.helpers.save_oracle(oracle, filename)
#     print 'done!'
# 
# def load_oracle(filename):
#     print 'loading "', filename, '"'
#     oracle = Resources.helpers.load_oracle(filename)
#     print 'done!'
#     return oracle
# 
def draw_oracle(oracle, filename, size=(900*4, 400*4)):
    image = Resources.DrawOracle.start_draw(oracle, size) 
    image.save(filename)
