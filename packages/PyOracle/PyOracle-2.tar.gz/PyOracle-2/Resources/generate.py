'''
generate.py
offline audio oracle / factor oracle generation routines for PyOracle

Copyright (C) 12.02.2013 Greg Surges, Cheng-i Wang

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

import random
import numpy as np
from matplotlib.mlab import find
from scipy.io import wavfile

import PyOracle.IR

def generate_symbolic(oracle, seq_len, p, k, LRS = 0, weight = None):
    """ Generate a sequence based on both sfx and rsfx
    """
    if type(oracle) == dict:
        trn = oracle['trn']
        sfx = oracle['sfx']
        lrs = oracle['lrs']
        rsfx = oracle['rsfx']
    else:
        trn = oracle.trn
        sfx = oracle.sfx
        lrs = oracle.lrs
        rsfx = oracle.rsfx

    s = []
    ktrace = [1]

    for i in range(seq_len):
        # generate each state
        if sfx[k] != 0 and sfx[k] is not None:
            if (random.random() < p):
                #copy forward according to transitions
                I = trn[k]
                if len(I) == 0:
                    # if last state, choose a suffix
                    k = sfx[k]
                    ktrace.append(k)
                    I = trn[k]
                sym = I[int(np.floor(random.random()*len(I)))]
                s.append(sym) #Why (sym-1) before?
                k = sym
                ktrace.append(k)
            else:
                # copy any of the next symbols
                ktrace.append(k)
                _k = k
                k_vec = [] 
                _find_links(k_vec, sfx, rsfx, _k)
                k_vec = [_i for _i in k_vec if lrs[_i] >= LRS] 
                lrs_vec = [lrs[_i] for _i in k_vec]
                if len(k_vec) > 0: # if a possibility found, len(I)
                    if weight == 'weight':
                        max_lrs = np.amax(lrs_vec)
                        query_lrs = max_lrs - np.floor(random.expovariate(1)) 
                        
                        if query_lrs in lrs_vec:
                            _tmp = np.where(lrs_vec == query_lrs)[0]
                            _tmp = _tmp[int(np.floor(random.random()*len(_tmp)))]
                            sym = k_vec[_tmp]
                        else:
                            _tmp = np.argmin(abs(np.subtract(lrs_vec, query_lrs)))
                            sym = k_vec[_tmp]
                    elif weight == 'max':
                        sym = k_vec[np.argmax([lrs[_i] for _i in k_vec])]
                    else:
                        sym = k_vec[int(np.floor(random.random()*len(k_vec)))]
                    s.append(sym+1)
                    k = sym+1
                    ktrace.append(k+1)
                else: # otherwise continue
                    sym = k+1
                    s.append(sym)
                    k = sym
                    ktrace.append(k)                    
        else:
            if k < len(sfx) - 1:
                s.append(k+1)
                k = k+1
                ktrace.append(k)
            else:
                k = int(random.random()*(len(sfx) - 1))
                s.append(k)
                ktrace.append(k)
    kend = k
    return s, kend, ktrace

def _find_links(k_vec ,sfx, rsfx, k):
    k_vec.sort()
    if 0 in k_vec:
        return 
    else:
        if sfx[k] not in k_vec:
            k_vec.append(sfx[k])
        for i in range(len(rsfx[k])):
            if rsfx[k][i] not in k_vec:
                k_vec.append(rsfx[k][i])
        for i in range(len(k_vec)):
            _find_links(k_vec, sfx, rsfx, k_vec[i])
            if 0 in k_vec:
                break


def generate(oracle, seq_len, p, k, LRS = 0):
    '''
    generate output state vector from audio oracle
    inputs:
    oracle - audio oracle to use
    seq_len - length of output sequence in states
    p - probability of jump
    k - starting state
    outputs:
    s - new_sequence
    kend - end point
    ktrace
    '''

    if type(oracle) == dict:
        trn = oracle['trn']
        sfx = oracle['sfx']
        lrs = oracle['lrs']
    else:
        trn = oracle.trn
        sfx = oracle.sfx
        lrs = oracle.lrs

    s = []
    ktrace = [1]

    for i in range(seq_len):
        # generate each state
        if sfx[k] != 0:
            if (random.random() < p):
                #copy forward according to transitions
                I = trn[k]
                if len(I) == 0:
                    # if last state, choose a suffix
                    k = sfx[k]
                    ktrace.append(k)
                    I = trn[k]
                sym = I[int(np.floor(random.random()*len(I)))]
                s.append(sym-1)
                k = sym
                ktrace.append(k)
            else:
                # copy any of the next symbols
                k = sfx[k]
                ktrace.append(k)
                I = trn[k]
                I = [_i for _i in I if lrs[_i] >= LRS]
                if len(I) > 0: # if a possibility found
                    sym = I[int(np.floor(random.random()*len(I)))]
                    s.append(sym-1)
                    k = sym
                    ktrace.append(k)
                else: # otherwise continue
                    sym = k+1
                    s.append(sym-1)
                    k = sym
                    ktrace.append(k)
        else:
            if k < len(sfx) - 1:
                next_k = k+1
                # next_k = find([o.transition.pointer.number for o in oracle] == k+1)
                s.append(next_k)
                k = k+1
                ktrace.append(k)
            else:
                nextk = int(random.random()*(len(sfx) - 1))
                # s.append(find(oracle['trn'][0] == nextk))
                s.append(nextk)
                k = nextk
                ktrace.append(k)
    kend = k
    return s, kend, ktrace

def make_win(n, mono=False):
    if mono:
        win = np.hanning(n) + 0.00001
    else:
        win = np.array([np.hanning(n) + 0.00001, np.hanning(n) + 0.00001])
    win = np.transpose(win)
    return win

def generate_audio(ifilename, ofilename, buffer_size, hop, oracle, seq_len, p, k, lrs = 0):
    '''
    make audio output using audio oracle for generation
    input:
        ifilename - input audio file path
        ofilename - output audio file path
        buffer_size - should match fft/frame size of oracle analysis
        hop - hop size, should be 1/2 buffer_size
        oracle - oracle built on ifilename
        seq_len - length of sequence to be generated, in frames
        p - continuity parameter
        k - start frame
        lrs - lrs constraint
    output:
        x - generated sequence
        wsum - generated sequence with compensation for windowing
    '''

    fs, x = wavfile.read(ifilename)
    xmat = []
    for i in range(0, len(x), hop):
        new_mat = np.array(x[i:i+buffer_size]) # try changing array type?
        xmat.append(new_mat)
    if buffer_size == 1 and hop == 1:
        xmat = x
    xmat = np.array(xmat)

    s, kend, ktrace = generate(oracle, seq_len, p, k, lrs) 
    xnewmat = xmat[:, s]

    if buffer_size == 1 and hop == 1:
        framelen = 1
    else:
        framelen = len(xnewmat[0])
    nframes = len(xnewmat)

    wsum = np.zeros(((nframes-1) * hop + framelen, 2)) 

    win = make_win(framelen)

    x = np.zeros(((nframes-1) * hop + framelen, 2)) 
    win_pos = range(0, len(x), hop)
    for i in range(0, nframes):
        # this is the overlap add sec

        if buffer_size == 1 and hop == 1:
            len_xnewmat = 1
        else:
            len_xnewmat = len(xnewmat[i])
        win = make_win(len_xnewmat)
        x[win_pos[i]:win_pos[i]+len_xnewmat] = x[win_pos[i]:win_pos[i]+len_xnewmat] + xnewmat[i] * win
        wsum[win_pos[i]:win_pos[i]+len_xnewmat] = wsum[win_pos[i]:win_pos[i]+len_xnewmat] + win 
    # x[hop:-hop] = x[hop:-hop] / wsum[hop:-hop]
    x = np.array(x/x.max()*32000, dtype=np.int16)
    wavfile.write(ofilename, fs, x)
    return x, wsum

def follow_code(oracle):
    ir, code, compror = PyOracle.IR.get_IR(oracle)
    len_thresh = 8
    
    sorted_code = sorted(code, key= lambda x: x[0], reverse=True)
    sorted_code = filter(lambda x: x[0] >= len_thresh, sorted_code)
    s = []
    kend = 0
    ktrace = []

    for i,cur in enumerate(sorted_code[:-2]):
        if cur[0] > 0:
            s.extend(range(cur[1], cur[1]+cur[0]))
            dest = sorted_code[i+1][1]
            tran = follow_path(oracle, dest, s[-1]) 
            s.extend(tran[-2:1:-1])
    
    return s, kend, ktrace

def follow_path(oracle, dest, current):
    # TODO: Need to clarify the len(oracle) 
    if dest == current:
        return [dest]
    # print 'dest:', dest, 'current:', current
    # COLLECT TRN AND SFX VECTORS
    trn = [0] * len(oracle)
    for i in range(len(oracle)):
        trn[i] = [t.pointer.number for t in oracle[i].transition]
    sfx = [0] * len(oracle)
    for i in range(len(oracle)):
        try:
            sfx[i] = oracle[i].suffix.number 
        except:
            sfx[i] = oracle[i].suffix
    rsfx = [[]] * len(oracle)
    for i in range(len(oracle)): 
        rsfx[i] = [r.number for r in oracle[i].reverse_suffix]

    visited_states = [dest]
    # collect all unvisited possible next states
    possibilities = trn[dest]
    possibilities.append(sfx[dest])
    for rs in rsfx[dest]:
        possibilities.append(rs)
    possibilities = filter(lambda x: x not in visited_states, possibilities)
    # add to list of visited  
    visited_states.extend(possibilities) 

    paths = [tuple([dest])] * len(possibilities)    

    for i, pos in enumerate(possibilities):
        new_list = list(paths[i])
        new_list.append(pos)
        paths[i] = tuple(new_list)
    
    # check for success
    for path in paths:
        if path[-1] == current:
            return path
        else:
            # continue search
            found = False

    while not found:
        new_paths = []
        for p in paths:
            c = p[-1]
            possibilities = trn[c]
            possibilities.append(sfx[c])
            for rs in rsfx[dest]:
                possibilities.append(rs)
            possibilities = filter(lambda x: x not in visited_states, possibilities)
            # add to list of visited 
            visited_states.extend(possibilities) 
            for pos in possibilities:
                new_list = list(p)
                new_list.append(pos)
                new_paths.append(tuple(new_list))
                if pos == current:
                    found = True
                    path = new_list
                    return path
                    break
        paths = new_paths 

    # because we dont want to actually navigate TO state 0
    for e in path:
        # TODO: Added path.remove, make sure it`s right.
        if e is 0: path.remove(e)

    return path
    
