#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>
# Elie Khoury <Elie.Khoury@idiap.ch>
# Wed Aug 28 14:51:26 CEST 2013
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
#

import sys, os, shutil
import argparse
import bob
import numpy

from facereclib.script import faceverify
from facereclib import toolchain, tools, utils

#from .. import toolchain as mytoolchain
from .. import tools as mytools


class ToolChainExecutorJFA (faceverify.ToolChainExecutorZT, mytools.ParaUBMGMM):
  """Class that executes the ZT tool chain (locally or in the grid)."""

  def __init__(self, args):
    # call base class constructor
    faceverify.ToolChainExecutorZT.__init__(self, args)
    mytools.ParaUBMGMM.__init__(self)

    if not isinstance(self.m_tool, mytools.JFA):
      raise ValueError("This script is specifically designed to compute JFA tests. Please select an according tool.")

    self.m_tool.m_gmm_jfa_split = True

    if args.protocol:
      self.m_database.protocol = args.protocol

    self.m_tool.m_gmm_filename = os.path.join(self.m_configuration.temp_directory, 'gmm/Projector.hdf5')
    self.m_configuration.jfa_intermediate_file_1 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_1', 'i_%05d', 'jfa.hdf5')
    self.m_configuration.jfa_stats_file_1 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_1', 'i_%05d', 'stats_%05d-%05d.hdf5')
    self.m_configuration.jfa_intermediate_file_2 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_2', 'i_%05d', 'jfa.hdf5')
    self.m_configuration.jfa_stats_file_2 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_2', 'i_%05d', 'stats_%05d-%05d.hdf5')
    self.m_configuration.jfa_intermediate_file_3 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_3', 'i_%05d', 'jfa.hdf5')
    self.m_configuration.jfa_stats_file_3 = os.path.join(self.m_configuration.temp_directory, 'jfa_temp_3', 'i_%05d', 'stats_%05d-%05d.hdf5')
    self.m_tool.m_jfa_filename = os.path.join(self.m_configuration.temp_directory, 'jfa.hdf5')
    self.m_tool.m_projected_toreplace = 'projected'
    self.m_tool.m_projected_gmm = 'gmm/projected'
    self.m_tool.m_projected_jfa = 'projected'
    self.m_tool.m_projector_toreplace = self.m_configuration.projector_file

    self.m_configuration.models_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.models_directories[0], self.m_database.protocol)
    self.m_configuration.scores_no_norm_directory = os.path.join(self.m_configuration.user_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_score_directories[0])
    # add specific configuration for ZT-normalization
    if args.zt_norm:
      self.m_configuration.t_norm_models_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.models_directories[1], self.m_database.protocol)
      models_directories = (self.m_configuration.models_directory, self.m_configuration.t_norm_models_directory)

      self.m_configuration.scores_zt_norm_directory = os.path.join(self.m_configuration.user_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_score_directories[1])
      score_directories = (self.m_configuration.scores_no_norm_directory, self.m_configuration.scores_zt_norm_directory)

      self.m_configuration.zt_norm_A_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_temp_directories[0])
      self.m_configuration.zt_norm_B_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_temp_directories[1])
      self.m_configuration.zt_norm_C_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_temp_directories[2])
      self.m_configuration.zt_norm_D_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_temp_directories[3])
      self.m_configuration.zt_norm_D_sameValue_directory = os.path.join(self.m_configuration.temp_directory, self.m_args.score_sub_directory, self.m_database.protocol, self.m_args.zt_temp_directories[4])
      zt_score_directories = (self.m_configuration.zt_norm_A_directory, self.m_configuration.zt_norm_B_directory, self.m_configuration.zt_norm_C_directory, self.m_configuration.zt_norm_D_directory, self.m_configuration.zt_norm_D_sameValue_directory)
    else:
      models_directories = (self.m_configuration.models_directory,)
      score_directories = (self.m_configuration.scores_no_norm_directory,)
      zt_score_directories = None

    # specify the file selector to be used
    self.m_file_selector = toolchain.FileSelector(
        self.m_database,
        preprocessed_directory = self.m_configuration.preprocessed_directory,
        extractor_file = self.m_configuration.extractor_file,
        features_directory = self.m_configuration.features_directory,
        projector_file = self.m_configuration.projector_file,
        projected_directory = self.m_configuration.projected_directory,
        enroller_file = self.m_configuration.enroller_file,
        model_directories = models_directories,
        score_directories = score_directories,
        zt_score_directories = zt_score_directories
    )

    # create the tool chain to be used to actually perform the parts of the experiments
    self.m_tool_chain = toolchain.ToolChain(self.m_file_selector)

#######################################################################################
####################  Functions that will be executed in the grid  ####################
#######################################################################################

  def training_list(self):
    """Returns the list of feature files that is required for training"""
    features = self.m_file_selector.training_list('features', 'train_projector', arrange_by_client=True)
    if self.m_args.normalize_features:
      return [f.replace(self.m_configuration.features_directory, self.m_configuration.normalized_directory) for f in features]
    else:
      return features
 

  def jfa_initialize(self, force=False):
    """Initializes the JFA training (non-parallel)."""
    output_file = self.m_configuration.jfa_intermediate_file_1 % 0

    if self.m_tool_chain.__check_file__(output_file, force, 1000):
      utils.info("JFA training: Skipping JFA initialization since the file '%s' already exists" % output_file)
    else:
      # read data
      utils.info("JFA training: initializing jfa")
      #data = []
      training_list = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)
      data = [[]]
      #data = numpy.vstack([self.m_extractor.read_feature(str(training_list[index])) for index in utils.quasi_random_indices(len(training_list), self.m_args.limit_training_examples)])
      #for client_files in training_list:
      #  # data for the client
      #  data.append([self.m_tool.read_feature(str(f)) for f in client_files])
      # Perform JFA initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      # train JFA model
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.rng = bob.core.random.mt19937(self.m_tool.m_init_seed)
      jfa_base = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer.initialize(jfa_base, data)
      utils.ensure_dir(os.path.dirname(output_file))
      jfa_base.save(bob.io.HDF5File(output_file, 'w'))
      utils.info("JFA training: saved initial JFA machine to '%s'" % output_file)


  def jfa_estep_1(self, indices, force=False):
    """Performs a single E-step of the JFA algorithm (parallel)"""
    stats_file = self.m_configuration.jfa_stats_file_1 % (self.m_args.iteration, indices[0], indices[1])

    if  self.m_tool_chain.__check_file__(stats_file, force, 1000):
      utils.info("JFA training: Skipping JFA E-Step since the file '%s' already exists" % stats_file)
    else:
      utils.info("JFA training: E-Step from range(%d, %d)" % indices)

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      machine_file = self.m_configuration.jfa_intermediate_file_1 % self.m_args.iteration
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(machine_file))
      jfa_base.ubm = ubm

      # Load data
      training_list_ = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)
      training_list = [training_list_[index] for index in range(indices[0], indices[1])]
      data = []
      #for client_files in [training_list[index] for index in utils.quasi_random_indices(len(training_list))]:
      for client_files in training_list:
        # data for the client
        data.append([self.m_tool.read_feature(str(f)) for f in client_files])
      #data = [self.m_tool.read_feature(str(training_list[index])) for index in range(indices[0], indices[1])]

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)

      # Performs the E-step
      jfa_trainer.e_step1(jfa_base, data)

      # write results to file
      nsamples = numpy.array([indices[1] - indices[0]], dtype=numpy.float64)

      utils.ensure_dir(os.path.dirname(stats_file))
      f = bob.io.HDF5File(stats_file, 'w')
      f.set('acc_v_a1', jfa_trainer.acc_v_a1)
      f.set('acc_v_a2', jfa_trainer.acc_v_a2)
      #n_y = len(jfa_trainer.__Y__)
      #f.set('n_y', n_y)
      #for iy in range(n_y):
      #  f.set('y_%05d' % iy, jfa_trainer.__Y__[iy])
      f.set('nsamples', nsamples)
      
      utils.info("JFA training: Wrote Stats file '%s'" % stats_file)


  def _read_stats_1(self, filename):
    """Reads accumulated JFA statistics from file"""
    utils.debug("JFA training: Reading stats file '%s'" % filename)
    f = bob.io.HDF5File(filename)
    acc_v_a1    = f.read('acc_v_a1')
    acc_v_a2    = f.read('acc_v_a2')
    #n_y         = f.read('n_y')
    #y = []
    #for iy in range(n_y):
    #  y.append(f.read('y_%05d' % iy))
    return (acc_v_a1, acc_v_a2)

  def jfa_mstep_1(self, counts, force=False):
    """Performs a single M-step of the JFA algorithm (non-parallel)"""
    old_machine_file = self.m_configuration.jfa_intermediate_file_1 % self.m_args.iteration
    new_machine_file = self.m_configuration.jfa_intermediate_file_1 % (self.m_args.iteration + 1)

    if  self.m_tool_chain.__check_file__(new_machine_file, force, 1000):
      utils.info("JFA training: Skipping JFA M-Step since the file '%s' already exists" % new_machine_file)
    else:
      # get the files from e-step
      training_list = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)

      # try if there is one file containing all data
      if os.path.exists(self.m_configuration.jfa_stats_file_1 % (self.m_args.iteration, 0, len(training_list))):
        stats_file = self.m_configuration.jfa_stats_file_1 % (self.m_args.iteration, 0, len(training_list))
        # load stats file
        acc_v_a1, acc_v_a2 = self._read_stats_1(stats_file)
      else:
        # load several files
        job_ids = range(self._generate_job_array(training_list, counts)[1])
        job_indices = [(counts * job_id, min(counts * (job_id+1), len(training_list))) for job_id in job_ids]
        stats_files = [self.m_configuration.jfa_stats_file_1 % (self.m_args.iteration, indices[0], indices[1]) for indices in job_indices]

        # read all stats files
        acc_v_a1, acc_v_a2 = self._read_stats_1(stats_files[0])
        for stats_file in stats_files[1:]:
          acc_v_a1_, acc_v_a2_ = self._read_stats_1(stats_file)
          acc_v_a1 += acc_v_a1_
          acc_v_a2 += acc_v_a2_

      # TODO read some features (needed for computation, but not really required)
      data = [[]]

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(old_machine_file))
      jfa_base.ubm = ubm

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)

      # Performs the M-step
      jfa_trainer.acc_v_a1 = acc_v_a1
      jfa_trainer.acc_v_a2 = acc_v_a2
      jfa_trainer.m_step1(jfa_base, data) # data is not used in M-step
      utils.info("JFA training: Performed M step %d" % (self.m_args.iteration,))

      # Save the JFA model
      utils.ensure_dir(os.path.dirname(new_machine_file))
      jfa_base.save(bob.io.HDF5File(new_machine_file, 'w'))
      shutil.copy(new_machine_file, self.m_tool.m_jfa_filename)
      utils.info("JFA training: Wrote new JFA machine '%s'" % new_machine_file)

      hdf5file = bob.io.HDF5File(self.m_tool.m_projector_toreplace, "w")
      hdf5file.create_group('Projector')
      hdf5file.cd('Projector')
      ubm.save(hdf5file)

      hdf5file.cd('/')
      hdf5file.create_group('Enroller')
      hdf5file.cd('Enroller')
      jfa_base.save(hdf5file)

      #if self.m_args.iteration+1 == self.m_tool.m_jfa_training_iterations:

    if self.m_args.clean_intermediate and self.m_args.iteration > 0:
      old_file = self.m_configuration.jfa_intermediate_file_1 % (self.m_args.iteration-1)
      utils.info("Removing old intermediate directory '%s'" % os.path.dirname(old_file))
      shutil.rmtree(os.path.dirname(old_file))

  def jfa_finalize_1(self, counts, force=False):
    """Performs a single M-step of the JFA algorithm (non-parallel)"""
    machine_file = self.m_configuration.jfa_intermediate_file_1 % self.m_args.iteration
    new_machine_file = self.m_configuration.jfa_intermediate_file_2 % (0)

    if  self.m_tool_chain.__check_file__(new_machine_file, force, 1000):
      utils.info("JFA training: Skipping JFA M-Step since the file '%s' already exists" % new_machine_file)
    else:
        utils.ensure_dir(os.path.dirname(new_machine_file))
        shutil.copy(machine_file, new_machine_file)


  def jfa_estep_2(self, indices, force=False):
    """Performs a single E-step of the JFA algorithm (parallel)"""
    old_stats_file = self.m_configuration.jfa_stats_file_2 % (self.m_args.iteration-1, indices[0], indices[1])
    stats_file = self.m_configuration.jfa_stats_file_2 % (self.m_args.iteration, indices[0], indices[1])

    if  self.m_tool_chain.__check_file__(stats_file, force, 1000):
      utils.info("JFA training: Skipping JFA E-Step since the file '%s' already exists" % stats_file)
    else:
      utils.info("JFA training: E-Step from range(%d, %d)" % indices)

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      machine_file = self.m_configuration.jfa_intermediate_file_2 % self.m_args.iteration
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(machine_file))
      jfa_base.ubm = ubm

      # Load data
      training_list_ = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)
      training_list = [training_list_[index] for index in range(indices[0], indices[1])]
      data = []
      #for client_files in [training_list[index] for index in utils.quasi_random_indices(len(training_list))]:
      for client_files in training_list:
        # data for the client
        data.append([self.m_tool.read_feature(str(f)) for f in client_files])
      #data = [self.m_tool.read_feature(str(training_list[index])) for index in range(indices[0], indices[1])]

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)
      if self.m_args.iteration == 0:
        jfa_trainer.finalize1(jfa_base, data)
      else:
        #if os.path.exists(old_stats_file):
        # load stats file
        acc_u_a1, acc_u_a2, y = self._read_stats_2(old_stats_file)
        assert len(jfa_trainer.__Y__) == len(y)
        jfa_trainer.__Y__ = y

      # Performs the E-step
      jfa_trainer.e_step2(jfa_base, data)

      # write results to file
      nsamples = numpy.array([indices[1] - indices[0]], dtype=numpy.float64)

      utils.ensure_dir(os.path.dirname(stats_file))
      f = bob.io.HDF5File(stats_file, 'w')
      f.set('acc_u_a1', jfa_trainer.acc_u_a1)
      f.set('acc_u_a2', jfa_trainer.acc_u_a2)
      n_y = len(jfa_trainer.__Y__)
      f.set('n_y', n_y)
      for iy in range(n_y):
        f.set('y_%05d' % iy, jfa_trainer.__Y__[iy])
      f.set('nsamples', nsamples)
      utils.info("JFA training: Wrote Stats file '%s'" % stats_file)

  def _read_stats_2(self, filename):
    """Reads accumulated JFA statistics from file"""
    utils.debug("JFA training: Reading stats file '%s'" % filename)
    f = bob.io.HDF5File(filename)
    acc_u_a1    = f.read('acc_u_a1')
    acc_u_a2    = f.read('acc_u_a2')
    n_y         = f.read('n_y')
    y = []
    for iy in range(n_y):
      y.append(f.read('y_%05d' % iy))
    return (acc_u_a1, acc_u_a2, y)

  def jfa_mstep_2(self, counts, force=False):
    """Performs a single M-step of the JFA algorithm (non-parallel)"""
    old_machine_file = self.m_configuration.jfa_intermediate_file_2 % self.m_args.iteration
    new_machine_file = self.m_configuration.jfa_intermediate_file_2 % (self.m_args.iteration + 1)

    if  self.m_tool_chain.__check_file__(new_machine_file, force, 1000):
      utils.info("JFA training: Skipping JFA M-Step since the file '%s' already exists" % new_machine_file)
    else:
      # get the files from e-step
      training_list = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)

      # try if there is one file containing all data
      if os.path.exists(self.m_configuration.jfa_stats_file_2 % (self.m_args.iteration, 0, len(training_list))):
        stats_file = self.m_configuration.jfa_stats_file_2 % (self.m_args.iteration, 0, len(training_list))
        # load stats file
        acc_u_a1, acc_u_a2, y_ = self._read_stats_2(stats_file)
      else:
        # load several files
        job_ids = range(self._generate_job_array(training_list, counts)[1])
        job_indices = [(counts * job_id, min(counts * (job_id+1), len(training_list))) for job_id in job_ids]
        stats_files = [self.m_configuration.jfa_stats_file_2 % (self.m_args.iteration, indices[0], indices[1]) for indices in job_indices]

        # read all stats files
        acc_u_a1, acc_u_a2, y_ = self._read_stats_2(stats_files[0])
        for stats_file in stats_files[1:]:
          acc_u_a1_, acc_u_a2_, y_ = self._read_stats_2(stats_file)
          acc_u_a1 += acc_u_a1_
          acc_u_a2 += acc_u_a2_

      # TODO read some features (needed for computation, but not really required)
      data = [[]]

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(old_machine_file))
      jfa_base.ubm = ubm

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)

      # Performs the M-step
      jfa_trainer.acc_u_a1 = acc_u_a1
      jfa_trainer.acc_u_a2 = acc_u_a2
      jfa_trainer.m_step2(jfa_base, data) # data is not used in M-step
      utils.info("JFA training: Performed M step %d" % (self.m_args.iteration,))

      # Save the JFA model
      utils.ensure_dir(os.path.dirname(new_machine_file))
      jfa_base.save(bob.io.HDF5File(new_machine_file, 'w'))
      shutil.copy(new_machine_file, self.m_tool.m_jfa_filename)
      utils.info("JFA training: Wrote new JFA machine '%s'" % new_machine_file)

      hdf5file = bob.io.HDF5File(self.m_tool.m_projector_toreplace, "w")
      hdf5file.create_group('Projector')
      hdf5file.cd('Projector')
      ubm.save(hdf5file)

      hdf5file.cd('/')
      hdf5file.create_group('Enroller')
      hdf5file.cd('Enroller')
      jfa_base.save(hdf5file)

      if self.m_args.iteration+1 == self.m_tool.m_jfa_training_iterations:
        utils.ensure_dir(os.path.dirname(self.m_configuration.jfa_intermediate_file_3 % (0)))
        shutil.copy(new_machine_file, self.m_configuration.jfa_intermediate_file_3 % (0))

    if self.m_args.clean_intermediate and self.m_args.iteration > 0:
      old_file = self.m_configuration.jfa_intermediate_file_2 % (self.m_args.iteration-1)
      utils.info("Removing old intermediate directory '%s'" % os.path.dirname(old_file))
      shutil.rmtree(os.path.dirname(old_file))

  def jfa_finalize_2(self, counts, force=False):
    """Performs a single M-step of the JFA algorithm (non-parallel)"""
    machine_file = self.m_configuration.jfa_intermediate_file_2 % self.m_args.iteration
    new_machine_file = self.m_configuration.jfa_intermediate_file_3 % (0)

    if self.m_tool_chain.__check_file__(new_machine_file, force, 1000):
      utils.info("JFA training: Skipping JFA M-Step since the file '%s' already exists" % new_machine_file)
    else:
        utils.ensure_dir(os.path.dirname(new_machine_file))
        shutil.copy(machine_file, new_machine_file)


  def jfa_estep_3(self, indices, force=False):
    """Performs a single E-step of the JFA algorithm (parallel)"""
    old_stats_file = self.m_configuration.jfa_stats_file_3 % (self.m_args.iteration-1, indices[0], indices[1])
    stats_file = self.m_configuration.jfa_stats_file_3 % (self.m_args.iteration, indices[0], indices[1])

    if  self.m_tool_chain.__check_file__(stats_file, force, 1000):
      utils.info("JFA training: Skipping JFA E-Step since the file '%s' already exists" % stats_file)
    else:
      utils.info("JFA training: E-Step from range(%d, %d)" % indices)

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      machine_file = self.m_configuration.jfa_intermediate_file_3 % self.m_args.iteration
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(machine_file))
      jfa_base.ubm = ubm

      # Load data
      training_list_ = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)
      training_list = [training_list_[index] for index in range(indices[0], indices[1])]
      data = []
      #for client_files in [training_list[index] for index in utils.quasi_random_indices(len(training_list))]:
      for client_files in training_list:
        # data for the client
        data.append([self.m_tool.read_feature(str(f)) for f in client_files])
      #data = [self.m_tool.read_feature(str(training_list[index])) for index in range(indices[0], indices[1])]

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)
      if self.m_args.iteration == 0:
        jfa_trainer.finalize1(jfa_base, data)
        jfa_trainer.finalize2(jfa_base, data)
      else:
        if os.path.exists(old_stats_file):
          # load stats file
          acc_u_a1, acc_u_a2, y, x = self._read_stats_3(old_stats_file)
          assert len(jfa_trainer.__Y__) == len(y)
          jfa_trainer.__Y__ = y
          assert len(jfa_trainer.__X__) == len(x)
          jfa_trainer.__X__ = x

      # Performs the E-step
      jfa_trainer.e_step3(jfa_base, data)

      # write results to file
      nsamples = numpy.array([indices[1] - indices[0]], dtype=numpy.float64)

      utils.ensure_dir(os.path.dirname(stats_file))
      f = bob.io.HDF5File(stats_file, 'w')
      f.set('acc_d_a1', jfa_trainer.acc_d_a1)
      f.set('acc_d_a2', jfa_trainer.acc_d_a2)
      n_y = len(jfa_trainer.__Y__)
      f.set('n_y', n_y)
      for iy in range(n_y):
        f.set('y_%05d' % iy, jfa_trainer.__Y__[iy])
      n_x = len(jfa_trainer.__X__)
      f.set('n_x', n_x)
      for ix in range(n_x):
        f.set('x_%05d' % ix, jfa_trainer.__X__[ix])
      f.set('nsamples', nsamples)
      utils.info("JFA training: Wrote Stats file '%s'" % stats_file)

  def _read_stats_3(self, filename):
    """Reads accumulated JFA statistics from file"""
    utils.debug("JFA training: Reading stats file '%s'" % filename)
    f = bob.io.HDF5File(filename)
    acc_d_a1    = f.read('acc_d_a1')
    acc_d_a2    = f.read('acc_d_a2')
    n_y         = f.read('n_y')
    y = []
    for iy in range(n_y):
      y.append(f.read('y_%05d' % iy))
    n_x         = f.read('n_x')
    x = []
    for ix in range(n_x):
      x.append(f.read('x_%05d' % ix))
    return (acc_d_a1, acc_d_a2, y, x)

  def jfa_mstep_3(self, counts, force=False):
    """Performs a single M-step of the JFA algorithm (non-parallel)"""
    old_machine_file = self.m_configuration.jfa_intermediate_file_3 % self.m_args.iteration
    new_machine_file = self.m_configuration.jfa_intermediate_file_3 % (self.m_args.iteration + 1)

    if  self.m_tool_chain.__check_file__(new_machine_file, force, 1000):
      utils.info("JFA training: Skipping JFA M-Step since the file '%s' already exists" % new_machine_file)
    else:
      # get the files from e-step
      training_list = self.m_file_selector.training_list('projected', 'train_projector', arrange_by_client = True)

      # try if there is one file containing all data
      if os.path.exists(self.m_configuration.jfa_stats_file_3 % (self.m_args.iteration, 0, len(training_list))):
        stats_file = self.m_configuration.jfa_stats_file_3 % (self.m_args.iteration, 0, len(training_list))
        # load stats file
        acc_d_a1, acc_d_a2, y_, x_ = self._read_stats_3(stats_file)
      else:
        # load several files
        job_ids = range(self._generate_job_array(training_list, counts)[1])
        job_indices = [(counts * job_id, min(counts * (job_id+1), len(training_list))) for job_id in job_ids]
        stats_files = [self.m_configuration.jfa_stats_file_3 % (self.m_args.iteration, indices[0], indices[1]) for indices in job_indices]

        # read all stats files
        acc_d_a1, acc_d_a2, y_, x_ = self._read_stats_3(stats_files[0])
        for stats_file in stats_files[1:]:
          acc_d_a1_, acc_d_a2_, y_, x_ = self._read_stats_3(stats_file)
          acc_d_a1 += acc_d_a1_
          acc_d_a2 += acc_d_a2_

      # TODO read some features (needed for computation, but not really required)
      data = [[]]

      # Temporary machine used for initialization
      ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))
      m = bob.machine.JFABase(ubm, self.m_tool.m_subspace_dimension_of_u, self.m_tool.m_subspace_dimension_of_v)
      # Load machine
      jfa_base = bob.machine.JFABase(bob.io.HDF5File(old_machine_file))
      jfa_base.ubm = ubm

      # Creates the JFATrainer and call the initialization procedure
      jfa_trainer = bob.trainer.JFATrainer(self.m_tool.m_jfa_training_iterations)
      jfa_trainer.initialize(m, data)

      # Performs the M-step
      jfa_trainer.acc_d_a1 = acc_d_a1
      jfa_trainer.acc_d_a2 = acc_d_a2
      jfa_trainer.m_step3(jfa_base, data) # data is not used in M-step
      utils.info("JFA training: Performed M step %d" % (self.m_args.iteration,))

      # Save the JFA model
      utils.ensure_dir(os.path.dirname(new_machine_file))
      jfa_base.save(bob.io.HDF5File(new_machine_file, 'w'))
      shutil.copy(new_machine_file, self.m_tool.m_jfa_filename)
      utils.info("JFA training: Wrote new JFA machine '%s'" % new_machine_file)

      hdf5file = bob.io.HDF5File(self.m_tool.m_projector_toreplace, "w")
      hdf5file.create_group('Projector')
      hdf5file.cd('Projector')
      ubm.save(hdf5file)

      hdf5file.cd('/')
      hdf5file.create_group('Enroller')
      hdf5file.cd('Enroller')
      jfa_base.save(hdf5file)


    if self.m_args.clean_intermediate and self.m_args.iteration > 0:
      old_file = self.m_configuration.jfa_intermediate_file_3 % (self.m_args.iteration-1)
      utils.info("Removing old intermediate directory '%s'" % os.path.dirname(old_file))
      shutil.rmtree(os.path.dirname(old_file))


  def jfa_project(self, indices, force=False):
    """Performs JFA projection"""
    # read UBM into the JFA class
    self.m_tool._load_projector_gmm_resolved(self.m_tool.m_gmm_filename)
    self.m_tool._load_projector_jfa_resolved(self.m_tool.m_jfa_filename)

    projected_files = self.m_file_selector.projected_list()

    # select a subset of indices to iterate
    if indices != None:
      index_range = range(indices[0], indices[1])
      utils.info("- Projection: splitting of index range %s" % str(indices))
    else:
      index_range = range(len(projected_files))

    utils.info("- Projection: projecting %d gmm stats from directory '%s' to directory '%s'" % (len(index_range), self.m_tool._resolve_projected_gmm(self.m_file_selector.projected_directory), self.m_tool._resolve_projected_jfa(self.m_file_selector.projected_directory)))
    # extract the features
    for i in index_range:
      projected_file = projected_files[i]
      projected_file_gmm_resolved = self.m_tool._resolve_projected_gmm(projected_file)
      projected_file_jfa_resolved = self.m_tool._resolve_projected_jfa(projected_file)

      if not self.m_tool_chain.__check_file__(projected_file_jfa_resolved, force):
        # load feature
        feature = self.m_tool.read_feature(str(projected_file))
        # project feature
        projected = self.m_tool._project_jfa(feature)
        # write it
        utils.ensure_dir(os.path.dirname(projected_file_jfa_resolved))
        self.m_tool._save_feature_jfa(projected, str(projected_file))

#######################################################################################
##############  Functions dealing with submission and execution of jobs  ##############
#######################################################################################

  def add_jobs_to_grid(self, external_dependencies):
    """Adds all (desired) jobs of the tool chain to the grid."""
    # collect the job ids
    job_ids = {}

    # if there are any external dependencies, we need to respect them
    deps = external_dependencies[:]

    # I-vector
    if not self.m_args.skip_jfa:
      # initialization
      if not self.m_args.jfa_start_iteration:
        job_ids['jfa-init'] = self.submit_grid_job(
                'jfa-init',
                name = 'jfa-init',
                dependencies = deps,
                **self.m_grid.training_queue)
        deps.append(job_ids['jfa-init'])

      # several iterations of E and M steps
      for iteration in range(self.m_args.jfa_start_iteration, self.m_args.jfa_training_iterations):
        # E-step
        job_ids['jfa-e-step-1'] = self.submit_grid_job(
                'jfa-e-step-1 --iteration %d' % iteration,
                name='jfa-e-1-%d' % iteration,
                list_to_split = self.m_file_selector.training_list(directory_type='projected', step='train_enroller', arrange_by_client=True),
                number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
                dependencies = [job_ids['jfa-m-step-1']] if iteration != self.m_args.jfa_start_iteration else deps,
                **self.m_grid.projection_queue)

        # M-step
        job_ids['jfa-m-step-1'] = self.submit_grid_job(
                'jfa-m-step-1 --iteration %d' % iteration,
                name='jfa-m-1-%d' % iteration,
                dependencies = [job_ids['jfa-e-step-1']],
                **self.m_grid.training_queue)
      # add dependence to the last m step
      deps.append(job_ids['jfa-m-step-1'])

      # Finalize
      job_ids['jfa-finalize-1'] = self.submit_grid_job(
                'jfa-finalize-1 --iteration %d' % self.m_args.jfa_training_iterations,
                name='jfa-finalize-1-%d' % self.m_args.jfa_training_iterations,
                dependencies = deps,
                **self.m_grid.training_queue)
      # add dependence to the last m step
      deps.append(job_ids['jfa-finalize-1'])

      # several iterations of E and M steps
      for iteration in range(self.m_args.jfa_start_iteration, self.m_args.jfa_training_iterations):
        # E-step
        job_ids['jfa-e-step-2'] = self.submit_grid_job(
                'jfa-e-step-2 --iteration %d' % iteration,
                name='jfa-e-2-%d' % iteration,
                list_to_split = self.m_file_selector.training_list(directory_type='projected', step='train_enroller', arrange_by_client=True),
                number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
                dependencies = [job_ids['jfa-m-step-2']] if iteration != self.m_args.jfa_start_iteration else deps,
                **self.m_grid.projection_queue)

        # M-step
        job_ids['jfa-m-step-2'] = self.submit_grid_job(
                'jfa-m-step-2 --iteration %d' % iteration,
                name='jfa-m-2-%d' % iteration,
                dependencies = [job_ids['jfa-e-step-2']],
                **self.m_grid.training_queue)

      # add dependence to the last m step
      deps.append(job_ids['jfa-m-step-2'])

      # Finalize
      job_ids['jfa-finalize-2'] = self.submit_grid_job(
                'jfa-finalize-2 --iteration %d' % self.m_args.jfa_training_iterations,
                name='jfa-finalize-2-%d' % self.m_args.jfa_training_iterations,
                dependencies = deps,
                **self.m_grid.training_queue)
      # add dependence to the last m step
      deps.append(job_ids['jfa-finalize-2'])

      # several iterations of E and M steps
      for iteration in range(self.m_args.jfa_start_iteration, self.m_args.jfa_training_iterations):
        # E-step
        job_ids['jfa-e-step-3'] = self.submit_grid_job(
                'jfa-e-step-3 --iteration %d' % iteration,
                name='jfa-e-3-%d' % iteration,
                list_to_split = self.m_file_selector.training_list(directory_type='projected', step='train_enroller', arrange_by_client=True),
                number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
                dependencies = [job_ids['jfa-m-step-3']] if iteration != self.m_args.jfa_start_iteration else deps,
                **self.m_grid.projection_queue)

        # M-step
        job_ids['jfa-m-step-3'] = self.submit_grid_job(
                'jfa-m-step-3 --iteration %d' % iteration,
                name='jfa-m-3-%d' % iteration,
                dependencies = [job_ids['jfa-e-step-3']],
                **self.m_grid.training_queue)
      # add dependence to the last m step
      deps.append(job_ids['jfa-m-step-3'])


    # jfa projection
    if not self.m_args.skip_jfa_projection:
      job_ids['jfa-project'] = self.submit_grid_job(
              'jfa-project',
              name = 'jfa-project',
              list_to_split = self.m_file_selector.projected_list(),
              number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
              dependencies = deps,
              **self.m_grid.projection_queue)
      deps.append(job_ids['jfa-project'])


    # enroll models
    enroll_deps_n = {}
    enroll_deps_t = {}
    score_deps = {}
    concat_deps = {}
    for group in self.m_args.groups:
      enroll_deps_n[group] = deps[:]
      enroll_deps_t[group] = deps[:]
      if not self.m_args.skip_enrollment:
        job_ids['enroll_%s_N'%group] = self.submit_grid_job(
                'enroll --group %s --model-type N'%group,
                name = "enr-N-%s"%group,
                list_to_split = self.m_file_selector.model_ids(group),
                number_of_files_per_job = self.m_grid.number_of_enrolled_models_per_job,
                dependencies = deps,
                **self.m_grid.enrollment_queue)
        enroll_deps_n[group].append(job_ids['enroll_%s_N'%group])

        if self.m_args.zt_norm:
          job_ids['enroll_%s_T'%group] = self.submit_grid_job(
                  'enroll --group %s --model-type T'%group,
                  name = "enr-T-%s"%group,
                  list_to_split = self.m_file_selector.t_model_ids(group),
                  number_of_files_per_job = self.m_grid.number_of_enrolled_models_per_job,
                  dependencies = deps,
                  **self.m_grid.enrollment_queue)
          enroll_deps_t[group].append(job_ids['enroll_%s_T'%group])

      # compute A,B,C, and D scores
      if not self.m_args.skip_score_computation:
        job_ids['score_%s_A'%group] = self.submit_grid_job(
                'compute-scores --group %s --score-type A'%group,
                name = "score-A-%s"%group,
                list_to_split = self.m_file_selector.model_ids(group),
                number_of_files_per_job = self.m_grid.number_of_models_per_scoring_job,
                dependencies = enroll_deps_n[group],
                **self.m_grid.scoring_queue)
        concat_deps[group] = [job_ids['score_%s_A'%group]]

        if self.m_args.zt_norm:
          job_ids['score_%s_B'%group] = self.submit_grid_job(
                  'compute-scores --group %s --score-type B'%group,
                  name = "score-B-%s"%group,
                  list_to_split = self.m_file_selector.model_ids(group),
                  number_of_files_per_job = self.m_grid.number_of_models_per_scoring_job,
                  dependencies = enroll_deps_n[group],
                  **self.m_grid.scoring_queue)

          job_ids['score_%s_C'%group] = self.submit_grid_job(
                  'compute-scores --group %s --score-type C'%group,
                  name = "score-C-%s"%group,
                  list_to_split = self.m_file_selector.t_model_ids(group),
                  number_of_files_per_job = self.m_grid.number_of_models_per_scoring_job,
                  dependencies = enroll_deps_t[group],
                  **self.m_grid.scoring_queue)

          job_ids['score_%s_D'%group] = self.submit_grid_job(
                  'compute-scores --group %s --score-type D'%group,
                  name = "score-D-%s"%group,
                  list_to_split = self.m_file_selector.t_model_ids(group),
                  number_of_files_per_job = self.m_grid.number_of_models_per_scoring_job,
                  dependencies = enroll_deps_t[group],
                  **self.m_grid.scoring_queue)

          # compute zt-norm
          score_deps[group] = [job_ids['score_%s_A'%group], job_ids['score_%s_B'%group], job_ids['score_%s_C'%group], job_ids['score_%s_D'%group]]
          job_ids['score_%s_Z'%group] = self.submit_grid_job(
                  'compute-scores --group %s --score-type Z'%group,
                  name = "score-Z-%s"%group,
                  dependencies = score_deps[group])
          concat_deps[group].extend([job_ids['score_%s_B'%group], job_ids['score_%s_C'%group], job_ids['score_%s_D'%group], job_ids['score_%s_Z'%group]])
      else:
        concat_deps[group] = []

      # concatenate results
      if not self.m_args.skip_concatenation:
        job_ids['concat_%s'%group] = self.submit_grid_job(
                'concatenate --group %s'%group,
                name = "concat-%s"%group,
                dependencies = concat_deps[group])

    # return the job ids, in case anyone wants to know them
    return job_ids


  def execute_grid_job(self):
    """Run the desired job of the ZT tool chain that is specified on command line."""
    # I-vector initialization
    if self.m_args.sub_task == 'jfa-init':
      self.jfa_initialize(
          force = self.m_args.force)

    # I-vector e-step
    elif self.m_args.sub_task == 'jfa-e-step-1':
      self.jfa_estep_1(
          indices = self.indices(self.training_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

    # I-vector m-step
    elif self.m_args.sub_task == 'jfa-m-step-1':
      self.jfa_mstep_1(
          counts = self.m_grid.number_of_projected_features_per_job,
          force = self.m_args.force)

    # I-vector m-step
    elif self.m_args.sub_task == 'jfa-finalize-1':
      self.jfa_finalize_1(
          counts = self.m_grid.number_of_projected_features_per_job,
          force = self.m_args.force)

    # I-vector e-step
    elif self.m_args.sub_task == 'jfa-e-step-2':
      self.jfa_estep_2(
          indices = self.indices(self.training_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

    # I-vector m-step
    elif self.m_args.sub_task == 'jfa-m-step-2':
      self.jfa_mstep_2(
          counts = self.m_grid.number_of_projected_features_per_job,
          force = self.m_args.force)

    # I-vector m-step
    elif self.m_args.sub_task == 'jfa-finalize-2':
      self.jfa_finalize_2(
          counts = self.m_grid.number_of_projected_features_per_job,
          force = self.m_args.force)

    # I-vector e-step
    elif self.m_args.sub_task == 'jfa-e-step-3':
      self.jfa_estep_3(
          indices = self.indices(self.training_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

    # I-vector m-step
    elif self.m_args.sub_task == 'jfa-m-step-3':
      self.jfa_mstep_3(
          counts = self.m_grid.number_of_projected_features_per_job,
          force = self.m_args.force)

    # project using jfa
    elif self.m_args.sub_task == 'jfa-project':
      self.jfa_project(
          indices = self.indices(self.m_file_selector.projected_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

    # enroll the models
    elif self.m_args.sub_task == 'enroll':
      if self.m_args.model_type == 'N':
        self.m_tool_chain.enroll_models(
            self.m_tool,
            self.m_extractor,
            self.m_args.zt_norm,
            indices = self.indices(self.m_file_selector.model_ids(self.m_args.group), self.m_grid.number_of_enrolled_models_per_job),
            groups = [self.m_args.group],
            types = ['N'],
            force = self.m_args.force)

      else:
        self.m_tool_chain.enroll_models(
            self.m_tool,
            self.m_extractor,
            self.m_args.zt_norm,
            indices = self.indices(self.m_file_selector.t_model_ids(self.m_args.group), self.m_grid.number_of_enrolled_models_per_job),
            groups = [self.m_args.group],
            types = ['T'],
            force = self.m_args.force)

    # compute scores
    elif self.m_args.sub_task == 'compute-scores':
      if self.m_args.score_type in ['A', 'B']:
        self.m_tool_chain.compute_scores(
            self.m_tool,
            self.m_args.zt_norm,
            indices = self.indices(self.m_file_selector.model_ids(self.m_args.group), self.m_grid.number_of_models_per_scoring_job),
            groups = [self.m_args.group],
            types = [self.m_args.score_type],
            preload_probes = self.m_args.preload_probes,
            force = self.m_args.force)

      elif self.m_args.score_type in ['C', 'D']:
        self.m_tool_chain.compute_scores(
            self.m_tool,
            self.m_args.zt_norm,
            indices = self.indices(self.m_file_selector.t_model_ids(self.m_args.group), self.m_grid.number_of_models_per_scoring_job),
            groups = [self.m_args.group],
            types = [self.m_args.score_type],
            preload_probes = self.m_args.preload_probes,
            force = self.m_args.force)

      else:
        self.m_tool_chain.zt_norm(groups = [self.m_args.group])

    # concatenate
    elif self.m_args.sub_task == 'concatenate':
      self.m_tool_chain.concatenate(
          self.m_args.zt_norm,
          groups = [self.m_args.group])

    # Test if the keyword was processed
    else:
      raise ValueError("The given subtask '%s' could not be processed. THIS IS A BUG. Please report this to the authors." % self.m_args.sub_task)


def parse_args(command_line_parameters):
  """This function parses the given options (which by default are the command line options)."""
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      conflict_handler='resolve')

  # add the arguments required for all tool chains
  config_group, dir_group, file_group, sub_dir_group, other_group, skip_group = ToolChainExecutorJFA.required_command_line_options(parser)

  config_group.add_argument('-P', '--protocol', metavar='PROTOCOL',
      help = 'Overwrite the protocol that is stored in the database by the given one (might not by applicable for all databases).')
  config_group.add_argument('-p', '--preprocessing', default = ['default-tan-triggs'], metavar = 'x', nargs = '+', dest = 'preprocessor', help = 'Image preprocessing configuration.')
  config_group.add_argument('-f', '--features', default = ['default-dct-blocks'], metavar = 'x', nargs = '+', help = 'Feature extraction configuration.')
  config_group.add_argument('-t', '--tool', metavar = 'x', nargs = '+', default = ['default-jfa'],
      help = 'JFA-based face recognition; registered face recognition tools are: %s'%utils.resources.resource_keys('tool'))
  config_group.add_argument('-g', '--grid', metavar = 'x', nargs = '+', required = True,
      help = 'Configuration file for the grid setup; needs to be specified.')

  sub_dir_group.add_argument('--gmm-directory', metavar = 'DIR', required = True,
        help = 'The directory containing the GMM-related files.')
  sub_dir_group.add_argument('--models-directories', metavar = 'DIR', nargs = 2,
      default = ['models', 'tmodels'],
      help = 'Sub-directories (of --temp-directory) where the models should be stored')
  sub_dir_group.add_argument('--zt-temp-directories', metavar = 'DIR', nargs = 5,
      default = ['zt_norm_A', 'zt_norm_B', 'zt_norm_C', 'zt_norm_D', 'zt_norm_D_sameValue'],
      help = 'Sub-directories (of --temp-directory) where to write the ZT-norm values')
  sub_dir_group.add_argument('--zt-score-directories', metavar = 'DIR', nargs = 2,
      default = ['nonorm', 'ztnorm'],
      help = 'Sub-directories (of --user-directory) where to write the results to')

  #######################################################################################
  ############################ other options ############################################
  other_group.add_argument('-z', '--zt-norm', action='store_true',
      help = 'Enable the computation of ZT norms')
  other_group.add_argument('-F', '--force', action='store_true',
      help = 'Force to erase former data if already exist')
  other_group.add_argument('-w', '--preload-probes', action='store_true',
      help = 'Preload probe files during score computation (needs more memory, but is faster and requires fewer file accesses). WARNING! Use this flag with care!')
  other_group.add_argument('--groups', metavar = 'GROUP', nargs = '+', default = ['dev'],
      help = "The group (i.e., 'dev' or  'eval') for which the models and scores should be generated")

  other_group.add_argument('-F', '--force', action='store_true',
      help = 'Force to erase former data if already exist')

  other_group.add_argument('-n', '--normalize-features', action='store_true',
      help = 'Normalize features before JFA training?')
  other_group.add_argument('-C', '--clean-intermediate', action='store_true',
      help = 'Clean up temporary files of older iterations?')
  other_group.add_argument('-M', '--jfa-training-iterations', type=int, default=10,
      help = 'Specify the number of training iterations for the JFA training')
  other_group.add_argument('-m', '--jfa-start-iteration', type=int, default=0,
      help = 'Specify the first iteration for the JFA training (i.e. to restart)')

  skip_group.add_argument('--skip-jfa', '--noi', action='store_true',
      help = "Skip the JFA step")
  skip_group.add_argument('--skip-jfa-projection', '--noip', action='store_true',
      help = "Skip the GMM jfa projection")

  #######################################################################################
  #################### sub-tasks being executed by this script ##########################
  parser.add_argument('--sub-task',
      choices = ('jfa-init', 'jfa-e-step-1', 'jfa-m-step-1', 'jfa-finalize-1', 'jfa-e-step-2', 'jfa-m-step-2', 'jfa-finalize-2', 'jfa-e-step-3', 'jfa-m-step-3', 'jfa-project', 'enroll', 'compute-scores', 'concatenate'),
      help = argparse.SUPPRESS) #'Executes a subtask (FOR INTERNAL USE ONLY!!!)'
  parser.add_argument('--model-type', choices = ['N', 'T'],
      help = argparse.SUPPRESS) #'Which type of models to generate (Normal or TModels)'
  parser.add_argument('--score-type', choices = ['A', 'B', 'C', 'D', 'Z'],
      help = argparse.SUPPRESS) #'The type of scores that should be computed'
  parser.add_argument('--group',
      help = argparse.SUPPRESS) #'The group for which the current action should be performed'
  parser.add_argument('--iteration', type=int,
      help = argparse.SUPPRESS) #'The current iteration of KMeans or GMM training'

  return parser.parse_args(command_line_parameters)


def face_verify(args, command_line_parameters, external_dependencies = [], external_fake_job_id = 0):
  """This is the main entry point for computing face verification experiments.
  You just have to specify configuration scripts for any of the steps of the toolchain, which are:
  -- the database
  -- the preprocessing
  -- the feature extraction
  -- the score computation tool
  -- and the grid configuration (in case, the function should be executed in the grid).
  Additionally, you can skip parts of the toolchain by selecting proper --skip-... parameters.
  If your probe files are not too big, you can also specify the --preload-probes switch to speed up the score computation.
  If files should be re-generated, please specify the --force option (might be combined with the --skip-... options)."""


  # generate tool chain executor
  executor = ToolChainExecutorJFA(args)
  # as the main entry point, check whether the grid option was given
  if args.sub_task:
    # execute the desired sub-task
    executor.execute_grid_job()
    return {}
  else:
    # no other parameter given, so deploy new jobs

    # get the name of this file
    this_file = __file__
    if this_file[-1] == 'c':
      this_file = this_file[0:-1]

    # Check if gmm directory exists
    gmm_dir = os.path.join(executor.m_configuration.temp_directory, 'gmm')
    if os.path.exists(gmm_dir) or os.path.islink(gmm_dir):
      # Check for symbolic link
      if os.path.islink(gmm_dir):
        os.remove(gmm_dir)
        os.symlink(args.gmm_directory, gmm_dir)
      else:
        utils.info("- GMM directory '%s' already exists and is not a symbolic link" % gmm_dir)
    else:
      base_dir = os.path.dirname(gmm_dir)
      utils.ensure_dir(base_dir)
      os.symlink(args.gmm_directory, gmm_dir)

    # initialize the executor to submit the jobs to the grid
    executor.set_common_parameters(calling_file = this_file, parameters = command_line_parameters, fake_job_id = external_fake_job_id)

    # add the jobs
    return executor.add_jobs_to_grid(external_dependencies)


def main(command_line_parameters = sys.argv):
  """Executes the main function"""
  # do the command line parsing
  args = parse_args(command_line_parameters[1:])

  # perform face verification test
  face_verify(args, command_line_parameters)

if __name__ == "__main__":
  main()


