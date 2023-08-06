#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bob
import numpy
import scipy.spatial

from facereclib.tools.Tool import Tool
from facereclib import utils

class Distance (Tool):
  """Tool for computing distance-based scores"""

  def __init__(
      self,
      requires_projector_training = False, # No training required 
      distance_function = scipy.spatial.distance.cosine,
      is_distance_function = True,
      **kwargs  # parameters directly sent to the base class
  ):

    """Initializes the Distance tool with the given setup"""
    # call base class constructor and register that the tool performs a projection
    Tool.__init__(
        self,

        distance_function = str(distance_function),
        is_distance_function = is_distance_function,

        **kwargs
    )

    self.m_distance_function = distance_function
    self.m_factor = -1 if is_distance_function else 1.


  def enroll(self, enroll_features):
    """Enrolls the model by computing an average of the given input vectors"""
    assert len(enroll_features)
    # just store all the features
    model = numpy.zeros((len(enroll_features), enroll_features[0].shape[0]), numpy.float64)
    for n, feature in enumerate(enroll_features):
      model[n,:] += feature[:]
    # No normalization?
    # return enrolled model
    return model


  def score(self, model, probe):
    """Computes the distance of the model to the probe using the distance function taken from the config file"""
    # return the negative distance (as a similarity measure)
    if len(model.shape) == 2:
      # we have multiple models, so we use the multiple model scoring
      return self.score_for_multiple_models(model, probe)
    else:
      # single model, single probe (multiple probes have already been handled)
      return self.m_factor * self.m_distance_function(model, probe)
