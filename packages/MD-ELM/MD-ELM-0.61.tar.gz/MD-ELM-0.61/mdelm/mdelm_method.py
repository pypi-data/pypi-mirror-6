# -*- coding: utf-8 -*-
"""MD-ELM multi-class implementation.

Momo's version, counts errors less than the original one.
Created on Thu Feb  6 13:43:20 2014

@author: akusoka1
"""

import numpy as np
from numpy.linalg import inv
import cPickle
import os
from time import time
from random import sample

from mdelm import MDELM
from opelm.elm import ELM


def PRESS(H, Y):
    """Fast PRESS statistics calculation.
    """
    X = H
    N = X.shape[0]    
    C = inv(np.dot(X.T, X))
    P = X.dot(C)
    D = np.ones((N,)) - np.einsum('ij,ji->i', P, X.T)        
    W = C.dot(X.T).dot(Y)        
    e = (Y - X.dot(W)) / D.reshape((-1,1))
    MSE = np.mean(e**2)
    return MSE

def build_models(X, Y, L, k=4, max_flips = 100000, elm_models=3, artificial_sets=3, path=".", nn=30):
    """Prepare exhaustive set of models for finding artificial mislabels reliably.
    
    X,Y - dataset
    L - number of artificial mislabels
    elm_models - number of different ELM models
    artificial_sets - number of different sets of artificial mislabels
    path - path to store data files
    nn - number of neurons in ELM models
    
    mfiles - return array(data) of arrays(models) of files
    """
    c = Y.shape[1]
    N = X.shape[0]
    Yorig = Y.copy()
    mfiles = []  # list of model files - mfiles[data][elm_model]
    
    for data in xrange(artificial_sets):    
        Y = Yorig.copy()
        
        # generate artificial mislabels
        idx_sw = np.array(sample(xrange(N), L))
        for i in idx_sw:
            c_candidate = np.where(Y[i] == 0)[0]  # find all negative classes
            Y[i] = 0  # remove positive class
            # set a random negative class as a positive one
            Y[i, c_candidate[np.random.randint(c-1)]] = 1        
        
        mfiles.append([])
        # build different ELM models
        for elm in xrange(elm_models):
            H,MSE = build_opelm(X,Y,nn=nn)            
            scores = np.zeros((N,c))

            D = {}
            D['dataset'] = X,Y
            D['elm'] = H,MSE
            D['k'] = k
            D['scores'] = scores
            D['artificial_ml'] = idx_sw
            D['max_flips'] = max_flips
            D['last_flip'] = 0
    
            fname = os.path.join(path, "MDELM_data%d_elm%d.pkl" % (data, elm))    
            cPickle.dump(D, open(fname,"wb"), -1)
            mfiles[-1].append(fname)
            print "prepaired model %d-%d" % (data, elm)
    return mfiles

def build_opelm(X, Y, nn):
    """Build a good OP-ELM, max 9 trials.
    
    A single OP-ELM can be bad with random initialization.
    """
    improvements = 0
    trial = 0
    MSE0 = np.inf
    while improvements < 3:    
        trial += 1
        elm = ELM(X.shape[1], Y.shape[1], mirror=X.shape[1], tanh=nn)
        elm.train(X, Y, method='op')
        X1 = elm._norm_X(X)
        H = elm.get_nn()._project(X1)
    
        MSE = PRESS(H, Y)
        if MSE < MSE0:  # this passes at least once
            goodH = H.copy()
            goodMSE = MSE
            improvements += 1
            trial = 0
            MSE0 = MSE
        if trial > 3:
            trial = 0
            improvements += 1
    return goodH, goodMSE

def run_model(mfile, time_limit=5):
    """ Runs a single MD-ELM model from model file.
    
    Writes results back to that file.
    Stops at a time limit, can continue later.
    
    time - time in minutes
    save_each_iteration - whether to save often, or only at exit
    maxt - time to interrupt the method
    D - dictionary containing:
        D['dataset'] = (X,Y)
        D['elm'] = (H,MSE)
        D['scores'] = scores
        D['last_flip'] = last calculated flip
        D['max_flips'] = desired number of flips
        D['artificial_ml'] = indexes of artificial mislabels
    """
    
    save_each_iteration = True
    flips = 10000  # swaps per one iteration
    maxt = time_limit*60  # in seconds
    t = time()
    
    D = cPickle.load(open(mfile, 'rb'))    
    scores = D['scores']
    k = D['k']
    X,Y = D['dataset']

    if D['elm'] == ():
        H,MSE = build_opelm(X,Y,nn=30)
    else:
        H,MSE = D['elm']
    
    while ((time() - t) < maxt) and (D['last_flip'] < D['max_flips']):
        flips = min(flips, D['max_flips'] - D['last_flip'])
        scores += MDELM(H, Y, k, flips, MSE)
        D['last_flip'] += flips
        D['scores'] = scores  # not necessary, added for readability
        if save_each_iteration:
            cPickle.dump(D, open(mfile,'wb'), -1)

        print "%s %d/%d iter, %.0f minutes" % (mfile.split("/")[-1], 
                                               D['last_flip'], 
                                               D['max_flips'], 
                                               (time()-t)/60)

    if not save_each_iteration:
        cPickle.dump(D, open(mfile,'wb'), -1)
    all_done = D['last_flip'] == D['max_flips']
    return all_done

def analyze_models(mfiles):
    """Combine and analyze results of MD-ELM runs, return detected mislabeled sample.
    
    Assume the same set of artificial mislabels.
    mfiles - list of model file names for the same dataset and artificial mislabels,
             but different ELM models, mfiles[elm_model]
    """
    scores = []
    for mfile in mfiles:
        D = cPickle.load(open(mfile, "rb"))
        if scores==[]:
            scores = D['scores']
        else:
            scores += D['scores']
        
    idx_ml = D['artificial_ml']
    L = len(idx_ml)
    rank = np.argsort(scores.sum(1), 0)[::-1]  # descending order
    set_L = set(rank[:L])
    set_A = set(idx_ml)
    found = list(set_L - set_A)  # samples in L but not artificially mislabeled
    return found
    


if __name__ == "__main__":   
    X,Y = cPickle.load(open("data.pkl","rb"))
    mfiles = build_models(X,Y, X.shape[0]/10, k=4, path="./try")

    # run all experiments
    for data in mfiles:
        for elm in data:
            run_model(elm)

    scores = np.zeros((X.shape[0],))
    for data in mfiles:
        found = analyze_models(data)
        scores[found] += 1
    print scores
    print "done"












