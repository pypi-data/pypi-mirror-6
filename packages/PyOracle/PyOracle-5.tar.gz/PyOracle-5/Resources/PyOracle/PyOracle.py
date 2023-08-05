'''
pyoracle.py
build an audio oracle from an input string of audio features

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

import time

from random import randint
from itertools import izip
from numpy import array, size, zeros, shape, log, exp, max, argmin
from matplotlib.mlab import find
from math import isnan, sqrt

def create_oracle():
    """Returns an oracle with empty entry."""
    _oracle = {'sfx': [],    # suffix links
               'trn': [],    # forward links 
               'rsfx': [],   # reverse suffix links 
               'lrs': [],    # longest repeat  
               'data': [],
               }
    return _oracle

oracle = create_oracle()

def get_distance(event1, event2, weights = None, dfunc = 'euclidian'):
    '''Get distance between frames.'''
    features = event1.keys()
    if 'time' in features:
        features.remove('time')
    if 'duration' in features:
        features.remove('duration')

    distance = 0

    # if no weight, initialize by weighting all features equally
    if weights == None:
        weights = {}
        for feature in features:
            weights[feature] = 1.0

    # remove features which are not considered
    features = [f for f in features if weights[f] != 0.0]

    for feature in features:
        # get length of feature vec 
        try:
            n = len(event1[feature])
        except:
            n = 1
        if dfunc == 'euclidian':
            if n > 1:
                # is a vector
                data = izip(event1[feature], event2[feature])
                data = sqrt(sum((a - b) * (a - b) for a, b in data) / n)
                data *= weights[feature]
                distance += data
            else:
                # is a scaler
                data = sqrt(((event1[feature] - event2[feature]) * (event1[feature] - event2[feature])))
                distance += data * weights[feature]
        elif dfunc == 'bregman':
            # multinomial bregman
            sevent1 = event1[feature]
            sevent2 = event2[feature]
            data = multinomial_bregman_div(sevent1, sevent2) 
            if isnan(data):
                data = 0
            distance += data * weights[feature]
        # print feature, distance
    return distance

def add_initial_state(oracle):
    """Add state zero"""
    oracle['sfx'].append(None)
    oracle['rsfx'].append([])
    oracle['trn'].append([])
    oracle['lrs'].append(0)
    oracle['data'].append({})


def dts(fwd, symbol, s):
    ''' vector of distances between new symbol and all states
    pointed to by forward transiions links
    distance normalized by dim of feature vector '''
    D = len(symbol)
    dist = []
    s = array(s)
    symbol = array(symbol)
    for i in range(len(fwd)):
        dist.append(s[fwd[i]-1] - symbol)
    dist = array(dist)/D
    return dist

def add_state(oracle, new_data, threshold = 0, weights = None, dfunc = 'euclidian'):
    """Create new state and update related links and compressed state"""
    oracle['sfx'].append(0)
    oracle['rsfx'].append([])
    oracle['trn'].append([])
    oracle['lrs'].append(0)
    oracle['data'].append(new_data)

    n_states = len(oracle['lrs']) 
    i = n_states - 1 

    # assign new transition from state i-1 to i
    oracle['trn'][i - 1].append(i)

    k = oracle['sfx'][i - 1] 
    pi_1 = i - 1

    # iteratively backtrack suffixes from state i-1
    dvec = []
    while k != None:
        dvec = [get_distance(new_data, oracle['data'][s-1], weights, dfunc) for s in oracle['trn'][k] if s-1 != 0]
        dvec=array(dvec)
        I = find(dvec < threshold)
        # if no transition from suffix
        if len(I) == 0:
            oracle['trn'][k].append(i)
            pi_1 = k
            k = oracle['sfx'][k]
        else:
            break
    # if backtrack ended before 0
    if k == None:
        oracle['sfx'][i] = 0
    else:
        ival = argmin(dvec[I])
        oracle['sfx'][i] = oracle['trn'][k][I[ival]]
        S_i = oracle['sfx'][i]
        # add rev suffix
        if type(oracle['rsfx'][S_i]) == list:
            oracle['rsfx'][S_i].append(i)
        else:
            oracle['rsfx'][S_i] = [i]
    # LRS 
    ss = oracle['sfx'][-1]
    if ss == 0 or ss == 1:
        oracle['lrs'][-1] = 0
    else:
        pi_2 = ss - 1
        if pi_2 == oracle['sfx'][pi_1]:
            oracle['lrs'][-1] = oracle['lrs'][pi_1] + 1
        else:
            while oracle['sfx'][pi_2] != oracle['sfx'][pi_1]:
                pi_2 = oracle['sfx'][pi_2]
            oracle['lrs'][-1] = min(oracle['lrs'][pi_1], oracle['lrs'][pi_2]) + 1            

def build_oracle(input_data, threshold, feature = None, weights = None, dfunc = 'euclidian'):
    '''
    build an oracle from input data and a distance threshold
    returns dict oracle
    '''
    global oracle

    oracle = create_oracle() 

    # initialize weights if needed 
    if weights == None:
        weights = {'mfcc': 0.0,            
                   'centroid': 0.0,
                   'rms': 0.0,
                   'chroma': 0.0,
                   'zerocrossings': 0.0}

        # weight the feature we want
        weights[feature] = 1.0

    add_initial_state(oracle)
    for i, event in enumerate(input_data):
        # print 'progress:', float(i) / len(input_data)
        add_state(oracle, event, threshold, weights, dfunc)
    return oracle 

def build_weighted_oracle(input_data, threshold, weights):
    oracle = []

    add_initial_state(oracle)

    for event in input_data:
        add_state(oracle, event, threshold, weights)
    return oracle 

def build_dynamic_oracle(input_data, threshold, weights):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    oracle = []

    add_initial_state(oracle)
    for i, event in enumerate(input_data):
        add_state(oracle, event, threshold, weights[i])
        # progress output
    return oracle 

def dist_to_multinomial(q):
    '''
    convert raw distributions to multinomial natural parameters
    see : http://cosmal.ucsd.edu/~arshia/musant/?n=InformationGeometry.ExponentialFamilies
    '''

    q = array(q)
    d = size(q, 0)

    q = abs(q / sum(q))

    theta = log(q[:d-1] / q[d-1] + 0.0000001)
    
    return theta

def multinomial_grad_f(theta):
    # f is the cumulant function of the multinomial exponential canonical form
    s = 0.0
    
    try:
        s = sum(exp(theta))
    except TypeError:
        s = exp(theta)
    result = exp(theta) / (1+s)
    
    return result

def F(p):
    # print p
    try:
        return log(1 + sum(exp(p)))
    except TypeError:
        return log(1+exp(p))

def multinomial_bregman_div(p, q):
    p = dist_to_multinomial(p)
    q = dist_to_multinomial(q)
    # print 'after', p, q
    pq = p - q
    try:
        result = F(p) - F(q) - sum(pq * multinomial_grad_f(q))
    except TypeError:
        result = F(p) - F(q) - (pq * multinomial_grad_f(q))
    return result
