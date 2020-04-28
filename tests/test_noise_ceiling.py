#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:59:33 2020

@author: heiko
"""

import unittest
import numpy as np


class TestNoiseCeiling(unittest.TestCase):
    def test_cv_noise_ceiling(self):
        from pyrsa.inference import cv_noise_ceiling
        from pyrsa.inference import sets_k_fold_rdm
        from pyrsa.rdm import RDMs
        dis = np.random.rand(11,10)  # 11 5x5 rdms
        mes = "Euclidean"
        des = {'subj':0}
        rdm_des = {'session':np.array([1,1,2,2,4,5,6,7,7,7,7])}
        pattern_des = {'type':np.array([0,1,2,2,4])}
        rdms = RDMs(dissimilarities=dis,
                    rdm_descriptors=rdm_des,
                    pattern_descriptors=pattern_des,
                    dissimilarity_measure=mes,
                    descriptors=des)
        train_set, test_set, ceil_set = sets_k_fold_rdm(rdms, k_rdm=3,
                                                          random=False)
        noise_min, noise_max = cv_noise_ceiling(rdms, ceil_set, test_set,
                                                method='cosine')

    def test_boot_noise_ceiling(self):
        from pyrsa.inference import boot_noise_ceiling
        from pyrsa.rdm import RDMs
        dis = np.random.rand(11,10)  # 11 5x5 rdms
        mes = "Euclidean"
        des = {'subj':0}
        rdm_des = {'session':np.array([1,1,2,2,4,5,6,7,7,7,7])}
        pattern_des = {'type':np.array([0,1,2,2,4])}
        rdms = RDMs(dissimilarities=dis,
                    rdm_descriptors=rdm_des,
                    pattern_descriptors=pattern_des,
                    dissimilarity_measure=mes,
                    descriptors=des)
        noise_min, noise_max = boot_noise_ceiling(rdms, method='cosine')
