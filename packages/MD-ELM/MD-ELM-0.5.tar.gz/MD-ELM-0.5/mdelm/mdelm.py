# -*- coding: utf-8 -*-
"""MD-ELM multi-class implementation.

Momo's version, counts errors less than the original one.
Created on Thu Feb  6 13:43:20 2014

@author: akusoka1
"""

import numpy as np
from numpy.linalg import inv
from random import sample

def MDELM(H, Y, k, flips, MSE_orig):
    """Find probable mislabeled samples in a dataset.
    
    Mislabelled samples get higher scores.
    
    H - hidden layer output of an ELM
    Y - desired outputs of an ELM
    k - number of samples to relabel at each iteration
    flips - number of flips to try
    MSE_orig - MSE error threshold
    """
    N = H.shape[0]    

    # pre-calculate parameters for reduced PRESS
    C = inv(np.dot(H.T, H))
    P = H.dot(C)
    D = np.ones((N,)) - np.einsum('ij,ji->i', P, H.T)
    D = D.reshape((-1,1))    

    # create expandable array to store all scores
    c = Y.shape[1]
    score = np.zeros((N,c))

    # make the swaps
    Yorig = Y.copy()
    for _ in xrange(flips):
        idx_sw = np.array(sample(xrange(N), k))  # random samples to relabel
        Y = Yorig.copy()
    
        # relabeling
        for i in idx_sw:
            c_candidate = np.where(Y[i] == 0)[0]
            Y[i] = 0
            Y[i, c_candidate[np.random.randint(c-1)]] = 1        
    
        # reduced MSE    
        W = C.dot(H.T.dot(Y))        
        e = (Y - H.dot(W)) / D
        MSE = np.mean(e**2)
    
        # saving successful flip
        if MSE < MSE_orig:
            c_sw = np.argmax(Y[idx_sw], 1)
            score[idx_sw, c_sw] += 1
    
    return score


