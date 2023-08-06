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

from facereclib.tools.Tool import Tool
from facereclib.tools.PLDA import PLDA
from facereclib import utils

class MyPLDA (PLDA):
  """Tool chain for computing PLDA (over PCA-dimensionality reduced) features"""

  def __init__(
      self,
      subspace_dimension_of_f, # Size of subspace F
      subspace_dimension_of_g, # Size of subspace G

      #subspace_dimension_pca = None,  # if given, perform PCA on data and reduce the PCA subspace to the given dimension
      #plda_training_iterations = 200, # Maximum number of iterations for the EM loop
      ## TODO: refactor the remaining parameters!
      #INIT_SEED = 5489, # seed for initializing
      #INIT_F_METHOD = bob.trainer.PLDATrainer.BETWEEN_SCATTER,
      #INIT_F_RATIO = 1,
      #INIT_G_METHOD = bob.trainer.PLDATrainer.WITHIN_SCATTER,
      #INIT_G_RATIO = 1,
      #INIT_S_METHOD = bob.trainer.PLDATrainer.VARIANCE_DATA,
      #INIT_S_RATIO = 1,
      #multiple_probe_scoring = 'joint_likelihood',
      **kwargs
  ):

    """Initializes the local (PCA-)PLDA tool chain with the given file selector object"""
    # call base class constructor with its set of parameters
    PLDA.__init__(self, subspace_dimension_of_f, subspace_dimension_of_g, **kwargs)

    # call base class constructor and register that this class requires training for enrollment
    Tool.__init__(
        self,
        requires_enroller_training = True,

        subspace_dimension_of_f = subspace_dimension_of_f, # Size of subspace F
        subspace_dimension_of_g = subspace_dimension_of_g, # Size of subspace G

        #subspace_dimension_pca = subspace_dimension_pca,  # if given, perform PCA on data and reduce the PCA subspace to the given dimension
        #plda_training_iterations = plda_training_iterations, # Maximum number of iterations for the EM loop
        ## TODO: refactor the remaining parameters!
        #INIT_SEED = INIT_SEED, # seed for initializing
        #INIT_F_METHOD = str(INIT_F_METHOD),
        #INIT_F_RATIO = INIT_F_RATIO,
        #INIT_G_METHOD = str(INIT_G_METHOD),
        #INIT_G_RATIO = INIT_G_RATIO,
        #INIT_S_METHOD =str(INIT_S_METHOD),
        #INIT_S_RATIO = INIT_S_RATIO,
        #multiple_probe_scoring = multiple_probe_scoring,
        multiple_model_scoring = None,
        **kwargs
    )


  def train_enroller(self, training_features, projector_file):
    """Generates the PLDA base model from a list of arrays (one per identity),
       and a set of training parameters. If PCA is requested, it is trained on the same data.
       Both the trained PLDABase and the PCA machine are written."""


    # train PCA and perform PCA on training data
    if self.m_subspace_dimension_pca is not None:
      self.m_pca_machine = self.__train_pca__(training_features)
      training_features = self.__perform_pca__(self.m_pca_machine, training_features)
    else:
      training_features_ = []
      for client in training_features:
        client_data_list = []
        for feature in client:
          client_data_list.append(feature)
        client_data = numpy.vstack(client_data_list)
        training_features_.append(client_data)
      training_features = training_features_

    input_dimension = training_features[0].shape[1]

    utils.info("  -> Training PLDA base machine")
    # create trainer
    t = bob.trainer.PLDATrainer(self.m_plda_training_iterations)

    #t.rng.seed = self.m_init[0]
    t.rng = bob.core.random.mt19937(self.m_init[0])
    t.init_f_method = self.m_init[1]
    t.init_f_ratio = self.m_init[2]
    t.init_g_method = self.m_init[3]
    t.init_g_ratio = self.m_init[4]
    t.init_sigma_method = self.m_init[5]
    t.init_sigma_ratio = self.m_init[6]

    # train machine
    self.m_plda_base = bob.machine.PLDABase(input_dimension, self.m_subspace_dimension_of_f, self.m_subspace_dimension_of_g)
    t.train(self.m_plda_base, training_features)

    # write machines to file
    proj_hdf5file = bob.io.HDF5File(str(projector_file), "w")
    if self.m_subspace_dimension_pca is not None:
      proj_hdf5file.create_group('/pca')
      proj_hdf5file.cd('/pca')
      self.m_pca_machine.save(proj_hdf5file)
    proj_hdf5file.create_group('/plda')
    proj_hdf5file.cd('/plda')
    self.m_plda_base.save(proj_hdf5file)

  def enroll(self, enroll_features):
    """Enrolls the model by computing an average of the given input vectors"""
    if self.m_subspace_dimension_pca is not None:
      enroll_features_projected = self.__perform_pca_client__(self.m_pca_machine, enroll_features)
      self.m_plda_trainer.enrol(self.m_plda_machine,enroll_features_projected)
    else:
      enroll_features_ = []
      for features in enroll_features:
        enroll_features_.append(features)
      enroll_features = numpy.vstack(enroll_features_)
      self.m_plda_trainer.enrol(self.m_plda_machine,enroll_features)
    return self.m_plda_machine

  def score_for_multiple_probes(self, model, probes):
    """This function computes the score between the given model and several given probe files.
    In this base class implementation, it computes the scores for each probe file using the 'score' method,
    and fuses the scores using the fusion method specified in the constructor of this class."""
    n_probes = len(probes)
    if self.m_subspace_dimension_pca is not None:
      # project probe
      probe_ = numpy.ndarray((n_probes, self.m_pca_machine.shape[1]), numpy.float64)
      projected_probe = numpy.ndarray(self.m_pca_machine.shape[1], numpy.float64)
      for i in range(n_probes):
        self.m_pca_machine(probes[i], projected_probe)
        probe_[i,:] = projected_probe
      # forward
      if self.m_score_set == 'joint_likelihood':
        return model.forward(probe_)
      else:
        scores = [model.forward(probe_[i,:]) for i in range(n_probes)]
        return self.m_score_set(scores)
    else:
      # just forward
      if self.m_score_set == 'joint_likelihood':
        probe_ = numpy.ndarray((n_probes, probes[0].shape[0]), numpy.float64)
        for i in range(n_probes):
          probe_[i,:] = probes[i]
        return model.forward(probe_)
      # forward
      else:
        scores = [model.forward(probes[i]) for i in range(n_probes)]
        return self.m_score_set(scores)
