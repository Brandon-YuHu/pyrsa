#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 14:56:15 2020

@author: heiko
"""

import numpy as np
from scipy.stats import rankdata
from pyrsa.model import Model
from pyrsa.rdm import RDMs
from collections.abc import Iterable


def input_check_model(model, theta, fitter=None, N=1):
    if isinstance(model, Model):
        evaluations = np.zeros(N)
    elif isinstance(model, Iterable):
        if N > 1:
            evaluations = np.zeros((N,len(model)))
        else:
            evaluations = np.zeros(len(model))
        if not theta is None:
            assert isinstance(theta, Iterable), 'If a list of models is' \
                + ' passed theta must be a list of parameters'
            assert len(model) == len(theta), 'there should equally many' \
                + ' models as parameters'
        else:
            theta = [None] * len(model)
        if fitter is None:
            fitter = [None] * len(model)
        else:
            assert len(fitter) == len(model), 'if fitters are passed ' \
                + 'there should be as many as models'
        for k in range(len(model)):
            if fitter[k] is None:
                fitter[k] = model[k].default_fitter
    else:
        raise ValueError('model should be a pyrsa.model.Model or a list of'
                         + ' such objects')
    return evaluations, theta, fitter


def pool_rdm(rdms, method='cosine'):
    """pools multiple RDMs into the one with maximal performance under a given
    evaluation metric
    rdm_descriptors of the generated rdms are empty

    Args:
        rdms (pyrsa.rdm.RDMs):
            RDMs to be pooled
        method : String, optional
            Which comparison method to optimize for. The default is 'cosine'.

    Returns:
        pyrsa.rdm.RDMs: the pooled RDM, i.e. a RDM with maximal performance
            under the chosen method

    """
    rdm_vec = rdms.get_vectors()
    if method == 'euclid':
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
    elif method == 'cosine':
        rdm_vec = rdm_vec/np.mean(rdm_vec, axis=1, keepdims=True)
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
    elif method == 'corr':
        rdm_vec = rdm_vec - np.mean(rdm_vec, axis=1, keepdims=True)
        rdm_vec = rdm_vec / np.std(rdm_vec, axis=1, keepdims=True)
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
        rdm_vec = rdm_vec - np.min(rdm_vec)
    elif method == 'spearman':
        rdm_vec = np.array([rankdata(v) for v in rdm_vec])
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
    elif method == 'kendall' or method == 'tau-b':
        Warning('Noise ceiling for tau based on averaged ranks!')
        rdm_vec = np.array([rankdata(v) for v in rdm_vec])
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
    elif method == 'tau-a':
        Warning('Noise ceiling for tau based on averaged ranks!')
        rdm_vec = np.array([rankdata(v) for v in rdm_vec])
        rdm_vec = np.mean(rdm_vec, axis=0, keepdims=True)
    else:
        raise ValueError('Unknown RDM comparison method requested!')
    return RDMs(rdm_vec,
                dissimilarity_measure=rdms.dissimilarity_measure,
                descriptors=rdms.descriptors,
                rdm_descriptors=None,
                pattern_descriptors=rdms.pattern_descriptors)


def pair_tests(evaluations):
    """pairwise bootstrapping significant tests for a difference in model
    performance

    Args:
        evaluations (numpy.ndarray):
            RDMs to be pooled

    Returns:
        numpy.ndarray: matrix of proportions of opposit conclusions, i.e.
        p-values for the bootstrap test
    """
    proportions = np.zeros((evaluations.shape[1], evaluations.shape[1]))
    while len(evaluations.shape) > 2:
        evaluations = np.mean(evaluations, axis=-1)
    for i_model in range(evaluations.shape[1]-1):
        for j_model in range(i_model + 1, evaluations.shape[1]):
            proportions[i_model, j_model] = np.sum( \
                evaluations[:, i_model] < evaluations[:, j_model]) \
                / (evaluations.shape[0] - 
                   np.sum(evaluations[:, i_model] == evaluations[:, j_model]))
            proportions[j_model, i_model] = proportions[i_model, j_model]
    proportions = np.minimum(proportions, 1 - proportions)
    np.fill_diagonal(proportions,1)
    return proportions