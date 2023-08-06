#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# mat2npz.py
#
# purpose:  Convert matlab file from TEOS-10 group to a npz file
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.tiddlyspot.com/
# created:  06-Jun-2011
# modified: Mon 16 Sep 2013 01:40:54 PM BRT
#
# obs:
#

import numpy as np

from gsw.utilities import loadmatbunch

data_ver = 'v3_0'
gsw_data = loadmatbunch('gsw_data_%s.mat' % data_ver, masked=False)

print('Data version number: %s' % gsw_data.version_number)
print('Data version date: %s' % gsw_data.version_date)

# Delta SA Atlas.
ref_table = dict()
for k in gsw_data:
    if k == u'gsw_cv' or k == u'#refs#' or k == 'gsw_demo_data':
        pass
    else:
        ref_table[k] = gsw_data[k]
np.savez("data/gsw_data_%s" % data_ver, **ref_table)

# Save demo data values gsw_demo_data in a separate file.
gsw_demo_data = gsw_data['gsw_demo_data']

np.savez("data/gsw_demo_data_%s" % data_ver, **gsw_data['gsw_demo_data'])

# Save compare values `gsw_cv` in a separate file.
cv_vars = gsw_data['gsw_cv']

np.savez("data/gsw_cv_%s" % data_ver, **cv_vars)

# NOTE: The matfile gsw_cf.mat contains the results from
# `gsw_check_functions.m.` and is used later for tests.  Remember to save it as
# MatlabTM '-v6' otherwise will have to use hdf5 instead of loadmat to read it.
if True:
    gsw_cf = loadmatbunch('gsw_cf.mat', masked=False)
    np.savez("data/gsw_cf", **gsw_cf)
