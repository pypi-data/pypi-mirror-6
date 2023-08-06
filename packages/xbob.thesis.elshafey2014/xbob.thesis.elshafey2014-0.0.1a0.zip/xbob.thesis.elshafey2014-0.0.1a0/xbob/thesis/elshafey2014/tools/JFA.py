#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Tue Mar  4 19:04:50 CET 2014
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
from facereclib.tools.UBMGMM import UBMGMM
from facereclib import utils


class JFA (UBMGMM):
  """Tool for computing Unified Background Models and Gaussian Mixture Models of the features"""

  def __init__(
      self,
      # JFA training
      subspace_dimension_of_u,       # U subspace dimension
      subspace_dimension_of_v,       # V subspace dimension
      jfa_training_iterations = 10,  # Number of EM iterations for the JFA training
      # JFA enrollment
      jfa_enroll_iterations = 1,     # Number of iterations for the enrollment phase
      # Parameters when splitting GMM and JFA files
      gmm_jfa_split = False,
      projected_toreplace = 'projected', # 'Magic' string in path that will be replaced by the GMM or JFA one
      projected_gmm = 'projected_gmm', # subdirectory for the projected gmm
      projected_jfa = 'projected_jfa', # subdirectory for the projected jfa
      projector_toreplace = 'Projector.hdf5', # 'Magic' string in path that will be replaced by the GMM or JFA one
      gmm_filename = 'gmm.hdf5', # filename for the GMM model
      jfa_filename = 'jfa.hdf5', # filename for the JFA model
      # parameters of the GMM
      **kwargs
  ):
    """Initializes the local UBM-GMM tool with the given file selector object"""
    # call base class constructor with its set of parameters
    UBMGMM.__init__(self, **kwargs)

    # call tool constructor to overwrite what was set before
    Tool.__init__(
        self,
        performs_projection = True,
        use_projected_features_for_enrollment = True,
        requires_enroller_training = False, # not needed anymore because it's done while training the projector
        split_training_features_by_client = True,

        subspace_dimension_of_u = subspace_dimension_of_u,
        subspace_dimension_of_v = subspace_dimension_of_v,
        jfa_training_iterations = jfa_training_iterations,
        jfa_enroll_iterations = jfa_enroll_iterations,

        gmm_jfa_split = gmm_jfa_split,
        projected_toreplace = projected_toreplace,
        projected_gmm =projected_gmm,
        projected_jfa = projected_jfa,
        projector_toreplace = projector_toreplace,
        gmm_filename = gmm_filename,
        jfa_filename = jfa_filename,

        multiple_model_scoring = None,
        multiple_probe_scoring = None,
        **kwargs
    )

    self.m_subspace_dimension_of_u = subspace_dimension_of_u
    self.m_subspace_dimension_of_v = subspace_dimension_of_v
    self.m_jfa_training_iterations = jfa_training_iterations
    self.m_jfa_enroll_iterations = jfa_enroll_iterations

    self.m_gmm_jfa_split = gmm_jfa_split
    self.m_projected_toreplace = projected_toreplace
    self.m_projected_gmm = projected_gmm
    self.m_projected_jfa = projected_jfa
    self.m_projector_toreplace = projector_toreplace
    self.m_gmm_filename = gmm_filename
    self.m_jfa_filename = jfa_filename

  def _train_jfa(self, data):
    """Train the JFA model given a dataset"""
    utils.info("  -> Training JFA enroller")
    self.m_jfabase = bob.machine.JFABase(self.m_ubm, self.m_subspace_dimension_of_u, self.m_subspace_dimension_of_v)
    # train JFA model
    t = bob.trainer.JFATrainer(self.m_jfa_training_iterations)
    t.rng = bob.core.random.mt19937(self.m_init_seed)
    t.train(self.m_jfabase, data)


  def _load_train_jfa(self, train_features):
    utils.info("  -> Projecting training data")
    data = []
    for client_features in train_features:
      list = []
      for feature in client_features:
        # Initializes GMMStats object
        self.m_gmm_stats = bob.machine.GMMStats(self.m_ubm.dim_c, self.m_ubm.dim_d)
        list.append(UBMGMM.project(self, feature))
      data.append(list)

    self._train_jfa(data)

  def train_projector(self, train_features, projector_file):
    """Train Projector and Enroller at the same time"""

    data1 = numpy.vstack([feature for client in train_features for feature in client])

    UBMGMM._train_projector_using_array(self, data1)
    # to save some memory, we might want to delete these data
    del data1

    # train JFA
    self._load_train_jfa(train_features)

    # Save the JFA base AND the UBM into the same file
    self._save_projector(projector_file)


  def _save_projector_together(self, projector_file):
    """Save the GMM and the JFA model in the same HDF5 file"""
    hdf5file = bob.io.HDF5File(projector_file, "w")
    hdf5file.create_group('Projector')
    hdf5file.cd('Projector')
    self.m_ubm.save(hdf5file)

    hdf5file.cd('/')
    hdf5file.create_group('Enroller')
    hdf5file.cd('Enroller')
    self.m_jfabase.save(hdf5file)


  def _resolve_gmm_filename(self, projector_file):
    return projector_file.replace(self.m_projector_toreplace, self.m_gmm_filename)

  def _resolve_jfa_filename(self, projector_file):
    return projector_file.replace(self.m_projector_toreplace, self.m_jfa_filename)

  def _resolve_projected_gmm(self, projected_file):
    return projected_file.replace(self.m_projected_toreplace, self.m_projected_gmm)

  def _resolve_projected_jfa(self, projected_file):
    return projected_file.replace(self.m_projected_toreplace, self.m_projected_jfa)


  def _save_projector_gmm_resolved(self, gmm_filename):
    self.m_ubm.save(bob.io.HDF5File(gmm_filename, "w"))

  def _save_projector_gmm(self, projector_file):
    gmm_filename = self._resolve_gmm_filename(projector_file)
    self._save_projector_gmm_resolved(gmm_filename)

  def _save_projector_jfa_resolved(self, jfa_filename):
    self.m_jfabase.save(bob.io.HDF5File(jfa_filename, "w"))

  def _save_projector_jfa(self, projector_file):
    jfa_filename = self._resolve_jfa_filename(projector_file)
    self._save_projector_jfa_resolved(jfa_filename)

  def _save_projector(self, projector_file):
    """Save the GMM and the JFA model"""
    if not self.m_gmm_jfa_split:
      self._save_projector_together(projector_file)
    else:
      self._save_projector_gmm(projector_file)
      self._save_projector_jfa(projector_file)


  # Here, we just need to load the UBM from the projector file.
  def _load_projector_gmm_resolved(self, gmm_filename):
    self.m_ubm = bob.machine.GMMMachine(bob.io.HDF5File(gmm_filename))
    self.m_ubm.set_variance_thresholds(self.m_variance_threshold)
    # Initializes GMMStats object
    self.m_gmm_stats = bob.machine.GMMStats(self.m_ubm.dim_c, self.m_ubm.dim_d)

  def _load_projector_gmm(self, projector_file):
    gmm_filename = self._resolve_gmm_filename(projector_file)
    self._load_projector_gmm_resolved(gmm_filename)

  def _load_projector_jfa_resolved(self, jfa_filename):
    self.m_jfabase = bob.machine.JFABase(bob.io.HDF5File(jfa_filename))
    # add UBM model from base class
    self.m_jfabase.ubm = self.m_ubm

  def _load_projector_jfa(self, projector_file):
    jfa_filename = self._resolve_jfa_filename(projector_file)
    self._load_projector_jfa_resolved(jfa_filename)

  def _load_projector_together(self, projector_file):
    """Load the GMM and the JFA model from the same HDF5 file"""
    hdf5file = bob.io.HDF5File(projector_file)

    # Load Projector
    hdf5file.cd('/Projector')
    # read UBM
    self.m_ubm = bob.machine.GMMMachine(hdf5file)
    self.m_ubm.set_variance_thresholds(self.m_variance_threshold)
    # Initializes GMMStats object
    self.m_gmm_stats = bob.machine.GMMStats(self.m_ubm.dim_c, self.m_ubm.dim_d)

    # Load Enroller
    hdf5file.cd('/Enroller')
    self.m_jfabase = bob.machine.JFABase(hdf5file)
    # add UBM model from base class
    self.m_jfabase.ubm = self.m_ubm

  def load_projector(self, projector_file):
    """Reads the UBM model from file"""

    if not self.m_gmm_jfa_split:
      self._load_projector_together(projector_file)
    else:
      self._load_projector_gmm(projector_file)
      self._load_projector_jfa(projector_file)

    self.m_machine = bob.machine.JFAMachine(self.m_jfabase)
    self.m_trainer = bob.trainer.JFATrainer(self.m_jfa_training_iterations)
    self.m_trainer.rng = bob.core.random.mt19937(self.m_init_seed)


  #######################################################
  ################ JFA training #########################
  def _project_gmm(self, feature_array):
    return UBMGMM.project(self,feature_array)

  def _project_jfa(self, projected_ubm):
    projected_jfa = numpy.ndarray(shape=(self.m_ubm.dim_c*self.m_ubm.dim_d,), dtype=numpy.float64)
    model = bob.machine.JFAMachine(self.m_jfabase)
    model.estimate_ux(projected_ubm, projected_jfa)
    return projected_jfa

  def project(self, feature_array):
    """Computes GMM statistics against a UBM, then corresponding Ux vector"""
    projected_ubm = self._project_gmm(feature_array)
    projected_jfa = self._project_jfa(projected_ubm)
    return [projected_ubm, projected_jfa]

  #######################################################
  ################## JFA model enroll ####################

  def _save_feature_together(self, gmmstats, Ux, feature_file):
    hdf5file = bob.io.HDF5File(feature_file, "w")
    hdf5file.create_group('gmmstats')
    hdf5file.cd('gmmstats')
    gmmstats.save(hdf5file)
    hdf5file.cd('/')
    hdf5file.set('Ux', Ux)

  def _save_feature_gmm(self, data, feature_file):
    feature_file_gmm = self._resolve_projected_gmm(feature_file)
    data.save(bob.io.HDF5File(str(feature_file_gmm), 'w'))

  def _save_feature_jfa(self, data, feature_file):
    feature_file_jfa = self._resolve_projected_jfa(feature_file)
    bob.io.save(data, str(feature_file_jfa))

  def save_feature(self, data, feature_file):
    gmmstats = data[0]
    Ux = data[1]
    if not self.m_gmm_jfa_split:
      self._save_feature_together(gmmstats, Ux, feature_file)
    else:
      self._save_feature_gmm(gmmstats, feature_file)
      self._save_feature_jfa(Ux, feature_file)

  def read_feature(self, feature_file):
    """Read the type of features that we require, namely GMMStats"""
    if not self.m_gmm_jfa_split:
      hdf5file = bob.io.HDF5File(feature_file)
      hdf5file.cd('gmmstats')
      gmmstats = bob.machine.GMMStats(hdf5file)
    else:
      feature_file_gmm = self._resolve_projected_gmm(feature_file)
      gmmstats = bob.machine.GMMStats(bob.io.HDF5File(str(feature_file_gmm)))
    return gmmstats


  def enroll(self, enroll_features):
    """Performs JFA enrollment"""
    self.m_trainer.enrol(self.m_machine, enroll_features, self.m_jfa_enroll_iterations)
    # return the resulting gmm
    return self.m_machine


  ######################################################
  ################ Feature comparison ##################
  def read_model(self, model_file):
    """Reads the JFA Machine that holds the model"""
    machine = bob.machine.JFAMachine(bob.io.HDF5File(model_file))
    machine.jfa_base = self.m_jfabase
    return machine

  def read_probe(self, probe_file):
    """Read the type of features that we require, namely GMMStats"""
    if self.m_gmm_jfa_split:
      probe_file_gmm = self._resolve_projected_gmm(probe_file)
      gmmstats = bob.machine.GMMStats(bob.io.HDF5File(str(probe_file_gmm)))
      probe_file_jfa = self._resolve_projected_jfa(probe_file)
      Ux = bob.io.load(str(probe_file_jfa))
    else:
      hdf5file = bob.io.HDF5File(probe_file)
      hdf5file.cd('gmmstats')
      gmmstats = bob.machine.GMMStats(hdf5file)
      hdf5file.cd('/')
      Ux = hdf5file.read('Ux')
    return [gmmstats, Ux]

  def score(self, model, probe):
    """Computes the score for the given model and the given probe."""
    gmmstats = probe[0]
    Ux = probe[1]
    return model.forward_ux(gmmstats, Ux)

  def score_for_multiple_probes(self, model, probes):
    """This function computes the score between the given model and several given probe files."""
    # create GMM statistics from first probe statistics
    gmmstats_acc = bob.machine.GMMStats(probes[0][0])
    # add all other probe statistics
    for i in range(1,len(probes)):
      gmmstats_acc += probes[i][0]
    # compute JFA score with the accumulated statistics
    projected_jfa_acc = numpy.ndarray(shape=(self.m_ubm.dim_c*self.m_ubm.dim_d,), dtype=numpy.float64)
    model.estimate_ux(gmmstats_acc, projected_jfa_acc)
    return model.forward_ux(gmmstats_acc, projected_jfa_acc)


