'''
IR.py
Music Information Rate (IR) Analysis for PyOracle

Copyright (C) 12.02.2013 Greg Surges, Cheng-i Wang, Shlomo Dubnov

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

import math
import numpy as np

def encode(oracle):
    ''' 
    return code and compror for a given Oracle representation
    '''
    if type(oracle) == dict:
        lrs = oracle['lrs']
        sfx = oracle['sfx']
    else:
        lrs = oracle.lrs
        sfx = oracle.sfx

    compror = []
    code = []
    
    j = 0
    i = j
    cnt = 1
    while j < len(lrs) - 1:
        while i < len(lrs) - 1 and lrs[i + 1] >= i - j + 1:
            i = i + 1
        if i == j:
            i = i + 1
            code.append((0,i))
        else:
            #Shlomo: code.append((i - j, sfx[i] - i + j + 1))
            code.append((i - j, sfx[i] - i + j + 1))
            compror.append((i,i-j)) #Shlomo: changed from compror.append(i) 
        cnt = cnt + 1
        j = i
    return code, compror

def encode_old(oracle):
    ''' 
    return code and compror for a given Oracle representation
    '''
    compror = []
    if type(oracle) == dict:
        lrs = oracle['lrs']
        sfx = oracle['sfx']
    else:
        lrs = oracle.lrs
        sfx = oracle.sfx

    code = []
    
    j = 0
    i = j
    cnt = 1
    while j < len(lrs):
        while i < len(lrs) - 1 and lrs[i + 1] >= i - j + 1:
            i = i + 1
        if i == j:
            i = i + 1
            code.append((0,i))
        else:
            code.append((i - j, sfx[i] - i + j + 1))
            compror.append(i) 
        cnt = cnt + 1
        j = i
    return code, compror

def ent(x):
    n = sum(x)
    h = 0
    for i in range(len(x)):
        p = float(x[i])/n
        h = h-p*math.log(p,2)
    return h

def get_IR(oracle ,alpha = 1.0):
    '''
    compress PyOracle and get IR
    new, time-evolving measure
    returns IR, code, compror
    '''
    code, compror = encode(oracle)
    
    # cw = [0] * len(code)
    cw = np.zeros(len(code))
    for i, c in enumerate(code):
        cw[i] = c[0]+1

    c0 = [1 if x[0] == 0 else 0 for x in code]
    h0 = np.array([math.log(x, 2) for x in np.cumsum(c0)])

    dti = [1 if x[0] == 0 else x[0] for x in code]
    ti = np.cumsum(dti)

    # h = [0]*len(cw)
    h = np.zeros(len(cw))

    for i in range(1, len(cw)):
        h[i] = ent(cw[0:i+1])

    h = np.array(h)
    h0 = np.array(h0)
    IR = ti, alpha*h0-h

    return IR, code, compror

    
def get_IR_old(oracle):
    '''
    compress PyOracle and get IR
    returns IR, code, compror
    '''
    code, compror = encode_old(oracle)
    
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

    # proposed modification - 10.23.2012
    # takes into account that all transitions are not equally probably (occuring
    # with equal frequency over the length of the sequence
    P = [0] * len(trn[0])
    # rename
    N = []
    for t in trn[0]: # for each new state
        N_i = len(rsfx[t])
        N.append(N_i) 
    for i in range(len(P)):
        P[i] = float(N[i]) / sum(N)
    C0 = -1 * sum([p * math.log(p + 0.000000000000000000000001, 2) for p in P]) 

    # calculate IR from Compror
    IR = [0] * len(lrs)
    # C0 = math.log(len(trn[0]), 2)
    N = len(lrs)
    M = max(lrs)
    try:
        C1 = math.log(N, 2) + math.log(M, 2)
    except ValueError: # if log(0)
        C1 = math.log(0.0000000000000001 + N, 2) + math.log(0.0000000000000001 + M, 2)
    for i in range(1, len(compror)):
        L = compror[i] - compror[i - 1]
        IR[compror[i - 1]:compror[i]] = [max(C0 - C1 / L, 0)] * L
    return IR, code, compror

def get_IR_cum(oracle, alpha=1):

    code, compror = encode(oracle)

    if type(oracle) == dict:
        sfx = oracle['sfx']
    else:
        sfx = oracle.sfx

    N_states = len(sfx)    

    cw0 = np.zeros((N_states)) #cw0 counts the appearance of new states only 
    cw1 = np.zeros((N_states)) #cw1 counts the appearance of all compror states
    BL = np.zeros((N_states))  #BL is the block length of compror codewords

    j = 0
    for i in range(len(code)):
        if code[i][0] == 0:
            cw0[j] = 1
            cw1[j] = 1
            BL[j] = 1
            j = j+1
        else:
            L = code[i][0]	
            cw0[j:j+L] = [0]*L
            cw1[j:j+L] = np.concatenate(([1], np.zeros(L-1)))
            BL[j:j+L] = L #range(1,L+1)
            j = j+L

    H0 = np.array([math.log(x,2) for x in np.cumsum(cw0)])
    H1 = np.array([math.log(x,2) for x in np.cumsum(cw1)])
    H1 = H1/BL
    IR = alpha*H0-H1
    IR = np.array([max(0, x) for x in IR])

    return IR, code, compror
