#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sat Nov 23 16:51:32 CET 2013
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import facereclib

# Classification algorithms
tool = facereclib.tools.UBMGMM(
    # GMM parameters
    k_means_training_iterations = 50, # Maximum number of iterations for K-Means
    gmm_training_iterations = 50,     # Maximum number of iterations for ML GMM Training
    training_threshold = 0.,          # Threshold to end the ML training (Do not stop using this criterium)
    number_of_gaussians = 1024,
    relevance_factor = 4.,
    gmm_enroll_iterations = 1,
)


