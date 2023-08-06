#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Tue Apr  8 18:49:31 CEST 2014
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

class ParaGridParameters(facereclib.utils.GridParameters):
  """This class is defining the options that are required to submit parallel jobs to the SGE grid.
  """

  def __init__(
    self,
    # queue setup for the SGE grid (only used if grid = 'sge', the default)
    init_training_queue = '8G',
    **kwargs
  ):

    # call base class constructor with its set of parameters
    facereclib.utils.GridParameters.__init__(self, **kwargs)

    # the queues
    self.init_training_queue = self.queue(init_training_queue)

