'''
FactOracle.py
audio oracle and factor oracle analysis in python

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

from numpy import *
from PyOracle import *

class data(object):
    """A helper class for construct data object for symbolic comparison
    
    By default, the fist entry of the list or tuple is used as the feature to 
    test for equality between different data object. 
    
    Attributes:
        content: a list or tuple
        idx: the index of the list or tuple to be tested for equality 
    """
    def __init__(self, data_item, index = 0):
        self.content = data_item
        self.idx = index
        
    def __repr__(self):
        return str(self.content)
        
    def __eq__(self, other):
        if type(other) == data:
            if self.content[self.idx] == other.content[self.idx]:
                return True
            else:
                return False
        else:
            return False
    
    def __ne__(self, other):
        if type(other) == data:
            if self.content[self.idx] == other.content[self.idx]:
                return False
            else:
                return True
        else:
            return True

class FactorOracle(object):
    """ The base class for the RO(repeat oracle) and AO(audio oracle)
    
    Attributes:
        sfx: a list containing the suffix link of each state.
        trn: a list containing the forward links of each state as a list.
        rsfx: a list containing the reverse suffix links of each state 
            as a list.
        lrs: the value of longest repeated suffix of each state.
        data: the object/value associated with the direct link 
            connected to each state.
        compror: a list of tuples (i, i-j), i is the current coded position,
            i-j is the length of the corresponding coded words.
        code: a list of tuples (len, pos), len is the length of the 
            corresponding coded words, pos is the position where the coded
            words starts.
        seg: same as code but non-overlapping.
        kind: 
            'a': audio oracle
            'f': repeat oracle
        n_states: number of total states, also is length of the input 
            sequence plus 1.
        max_lrs: the longest lrs so far.
        params: a python dictionary for different feature and distance settings.
            keys:
                'thresholds': the minimum value for separating two values as 
                    different symbols.
                'weights': a dictionary containing different weights for features
                    used.
                'dfunc': the distance function.
    """
    def __init__(self, **kwargs):
        self.sfx = []
        self.trn = []
        self.rsfx= []
        self.lrs = []
        self.data= [] 
        
        self.compror = []
        self.code = []    
        self.seg = []   
        
        self.kind= 'f'
        
        self.n_states = 1
        self.max_lrs = 0
        self.params = {
                       'threshold':0,
                       'weights': {},
                       'dfunc': 'euclidean'
                       }
        self.update_params(**kwargs)
        
        # Adding zero state
        self.sfx.append(None)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(0)

    def update_params(self, **kwargs):
        """Subclass this"""
        self.params.update(kwargs)

    def add_state(self, new_data):
        """Subclass this"""
        pass

    def encode(self): #Referenced from IR module
        
        if self.compror == []:
            j = 0
        else:
            j = self.compror[-1][0]
            
        i = j
        while j < self.n_states-1:
            while i < self.n_states - 1 and self.lrs[i + 1] >= i - j + 1:
                i = i + 1
            if i == j:
                i = i + 1
                self.code.append((0,i))
                self.compror.append((i,0))
            else:
                self.code.append((i - j, self.sfx[i] - i + j + 1))
                self.compror.append((i,i-j)) 
            j = i
        return self.code, self.compror
    
    def get_code(self):
        if self.code == []:
            print "Generating codes with encode()."
            self.encode()
        return [(i, self.data[j]) if i == 0 else (i, j) for i, j in self.code]    
    
    def segment(self):
        """An non-overlap version Compror"""
        if self.seg == []:
            j = 0
        else:
            j = self.seg[-1][0]

        i = j
        while j < self.n_states-1:
            while i < self.n_states - 1 and self.lrs[i + 1] >= i - j + 1:
                i = i + 1
            if i == j:
                i = i + 1
                self.seg.append((0, i))
            else:
                if (self.sfx[i] + self.lrs[i]) <= i:
                    self.seg.append((i - j, self.sfx[i] - i + j + 1))

                else:
                    _i = j + i - self.sfx[i]
                    self.seg.append((_i-j ,self.sfx[i] - i + j + 1))
                    _j = _i
                    while _i < i and self.lrs[_i + 1] - self.lrs[_j]  >= _i - _j + 1:
                        _i = _i +1
                    if _i == _j:
                        _i = _i + 1
                        self.seg.append((0, _i))
                    else:
                        self.seg.append((_i-_j, self.sfx[_i]-_i+_j+1))
            j = i
        return self.seg
    
    def get_seg(self):
        if self.code == []:
            print "Generating codes with segment()."
            self.segment()
        return [(i, self.data[j]) if i == 0 else (i, j) for i, j in self.seg]    
    
    def get_IR(self, alpha = 1.0):
        """Referenced from IR.py
        """
        if self.code == []:
            raise ValueError("encode first then get IR!!")
        else:
            cw = zeros(len(self.code))
            for i, c in enumerate(self.code):
                cw[i] = c[0]+1
        
            c0 = [1 if x[0] == 0 else 0 for x in self.code]
            h0 = array([math.log(x, 2) for x in cumsum(c0)])
        
            dti = [1 if x[0] == 0 else x[0] for x in self.code]
            ti = cumsum(dti)
        
            h = zeros(len(cw))
        
            for i in range(1, len(cw)):
                h[i] = _entropy(cw[0:i+1])
        
            h = array(h)
            h0 = array(h0)
            IR = ti, alpha*h0-h
        
            return IR, self.code, self.compror
    
    def get_threshold(self):
        if self.params.get('threshold'):
            return int(self.params.get('threshold'))
        else:
            raise ValueError("Threshold is not set!")
        
    def get_weights(self):
        if self.params.get('weights'):
            return self.params.get('weights')
        else:
            raise ValueError("Weights are not set!")
        
    def get_dfunc(self):
        if self.params.get('dfunc'):
            return self.params.get('dfunc')
        else:
            raise ValueError("dfunc is not set!")
        
    
class RO(FactorOracle):
    """ An implementation of the RepeatOracle
    """
    
    def __init__(self, **kwargs):
        super(RO, self).__init__(**kwargs)
        self.kind = 'r'
        
    def add_state(self, new_symbol):
        self.sfx.append(0)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(new_symbol)
        
        self.n_states += 1
        
        i = self.n_states - 1
        
        self.trn[i-1].append(i)
        k = self.sfx[i-1]
        pi_1 = i-1
        
        # Adding forward links
        while k != None:
            _symbols = [self.data[state] for state in self.trn[k]]
            
            if self.data[i] not in _symbols:
                self.trn[k].append(i)
                pi_1 = k
                k = self.sfx[k]
            else:
                break
        
        if k == None:
            self.sfx[i] = 0
            self.lrs[i] = 0
        else:
            _query = [[self.data[state], state] for state in self.trn[k] if self.data[state] == self.data[i]]
            _query = sorted(_query, key=lambda _query: _query[1])
            _state = _query[0][1]  
            self.sfx[i] = _state
            self.lrs[i] = self._len_common_suffix(pi_1, self.sfx[i]-1) + 1
        
        k = self._find_better(i, self.data[i-self.lrs[i]])
        if k != None:
            self.lrs[i] += 1
            self.sfx[i] = k
        self.rsfx[self.sfx[i]].append(i)
        
        if self.lrs[i] > self.max_lrs:
            self.max_lrs = self.lrs[i]
            
    def _len_common_suffix(self, p1, p2):
        if p2 == self.sfx[p1]:
            return self.lrs[p1]
        else:
            while self.sfx[p1] != self.sfx[p2]:
                p2 = self.sfx[p2]
        return min(self.lrs[p1], self.lrs[p2])
    
    def _find_better(self, i, symbol):
        self.rsfx[i].sort()
        for j in self.rsfx[i]:
            if self.lrs[j] == self.lrs[i] and self.data[j-self.lrs[i]] == symbol:
                return j
        return None

    
class AO(FactorOracle):
    
    def __init__(self, **kwargs):
        super(AO, self).__init__(**kwargs)
        self.kind = 'a'
    
    def add_state(self, new_data):
        """Create new state and update related links and compressed state"""
        self.sfx.append(0)
        self.rsfx.append([])
        self.trn.append([])
        self.lrs.append(0)
        self.data.append(new_data)

        self.n_states += 1 
        i = self.n_states - 1
    
        # assign new transition from state i-1 to i
        self.trn[i - 1].append(i)
        k = self.sfx[i - 1] 
        pi_1 = i - 1
    
        # iteratively backtrack suffixes from state i-1
        dvec = []
        while k != None:
            dvec = [get_distance(new_data, self.data[s-1], self.params['weights'], self.params['dfunc']) for s in self.trn[k] if s-1 != 0]
            dvec = array(dvec)
            # if no transition from suffix
            '''
            if True not in dvec:
                self.trn[k].append(i)
                pi_1 = k
                k = self.sfx[k]
            else:
                break
            '''
            I = find(dvec < self.params['threshold'])
            if len(I) == 0:
                self.trn[k].append(i)
                pi_1 = k
                k = self.sfx[k]
            else:
                break
        # if backtrack ended before 0
        if k == None:
            self.sfx[i] = 0
        else:
            ival = argmin(dvec[I])
            self.sfx[i] = self.trn[k][I[ival]]
            S_i = self.sfx[i]
            # add rev suffix
            if type(self.rsfx[S_i]) == list:
                self.rsfx[S_i].append(i)
            else:
                self.rsfx[S_i] = [i]
            '''
            # filter out all above distance thresh
            filtered_transitions = filter(lambda x: get_distance(self.data[x], new_data, self.params['weights'], self.params['dfunc']) <= self.params['threshold'], self.trn[k])
            # sort possible suffixes by LRS
            sorted_list = sorted(filtered_transitions, key = lambda x: self.lrs[x])
            for t in sorted_list:
                if get_distance(self.data[t], new_data, self.params['weights'], self.params['dfunc']) <= self.params['threshold']:
                    # add suffix
                    S_i = t
                    self.sfx[i] = S_i
                    
                    # add rev suffix
                    if type(self.rsfx[S_i]) == list:
                        self.rsfx[S_i].append(i)
                    else:
                        self.rsfx[S_i] = [i]
                    break
            '''
        # LRS 
        ss = self.sfx[-1]
        if ss == 0 or ss == 1:
            self.lrs[-1] = 0
        else:
            pi_2 = ss - 1
            if pi_2 == self.sfx[pi_1]:
                self.lrs[-1] = self.lrs[pi_1] + 1
            else:
                while self.sfx[pi_2] != self.sfx[pi_1]:
                    pi_2 = self.sfx[pi_2]
                self.lrs[-1] = min(self.lrs[pi_1], self.lrs[pi_2]) + 1
                
def _entropy(x):
    x = divide(x, sum(x), dtype = float)
    return sum(multiply(-log2(x),x))

def _create_oracle(t, **kwargs):
    """A routine for creating a factor oracle."""
    if t == 'f':
        return RO(**kwargs)
    elif t == 'a':
        return AO(**kwargs)
    else:
        return AO(**kwargs)

def _build_factor_oracle(oracle,input_data):    
    for i, event in enumerate(input_data):
        oracle.add_state(event)
    return oracle
 
def build_oracle(input_data, flag, threshold = 0, feature = None, weights = None, dfunc = 'euclidian'):
    
    # initialize weights if needed 
    if weights == None:
        weights = {'mfcc': 0.0,            
                   'centroid': 0.0,
                   'rms': 0.0,
                   'chroma': 0.0,
                   'zerocrossings': 0.0}

        # weight the feature we want
        weights[feature] = 1.0

    if flag == 'a' or flag == 'f':
        oracle = _create_oracle(flag, threshold = threshold, weights = weights, dfunc = dfunc)
    else:
        oracle = _create_oracle('a', threshold = threshold, weights = weights, dfunc = dfunc)
             
    oracle = _build_factor_oracle(oracle, input_data)
    return oracle 

def build_weighted_oracle(input_data, flag, threshold, weights):

    if flag == 'a' or flag == 'f':
        oracle = _create_oracle(flag, threshold = threshold, weights = weights)
    else:
        oracle = _create_oracle('a', threshold = threshold, weights = weights)
             
    oracle = _build_factor_oracle(oracle, input_data)

    return oracle 

def build_dynamic_oracle(input_data, flag, threshold, weights):
    # features should be determined by the analysis code
    # need to embed timing info into the oracle 
    if flag == 'a' or flag == 'f':
        oracle = _create_oracle(flag, threshold = threshold, weights = weights)
    else:
        oracle = _create_oracle('a', threshold = threshold, weights = weights)
             
    for i, event in enumerate(input_data):
        oracle.update_params(weights = weights[i])
        oracle.add_state(event)
    return oracle 


                
