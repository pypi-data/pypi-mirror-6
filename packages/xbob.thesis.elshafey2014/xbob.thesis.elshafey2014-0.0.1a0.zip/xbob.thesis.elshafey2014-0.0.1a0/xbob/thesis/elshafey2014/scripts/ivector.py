#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>
# Elie Khoury <Elie.Khoury@idiap.ch>
# Wed Aug 28 14:51:13 CEST 2013
#
# Copyright (C) 2012-2013 Idiap Research Institute, Martigny, Switzerland
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

from facereclib.script import ToolChainExecutor
from facereclib import toolchain, tools, utils

from .. import toolchain as mytoolchain
from .. import tools as mytools

class ToolChainExecutorIVector (ToolChainExecutor.ToolChainExecutor, tools.ParallelUBMGMM):
  """Class that executes the ZT tool chain (locally or in the grid)."""

  def __init__(self, args):
    # call base class constructor
    ToolChainExecutor.ToolChainExecutor.__init__(self, args)
    tools.ParallelUBMGMM.__init__(self)
    
    if not isinstance(self.m_tool, mytools.IVector):
      raise ValueError("This script is specifically designed to compute IVector tests. Please select an according tool.")

    self.m_tool.m_gmm_ivec_split = True

    if args.protocol:
      self.m_database.protocol = args.protocol

    self.m_configuration.normalized_directory = os.path.join(self.m_configuration.temp_directory, 'normalized_features')
    self.m_tool.m_gmm_filename = os.path.join(self.m_configuration.temp_directory, 'gmm/Projector.hdf5')
    self.m_tool.m_ivec_filename = os.path.join(self.m_configuration.temp_directory, 'ivec.hdf5')
    self.m_tool.m_projected_toreplace = 'projected'
    self.m_tool.m_projected_gmm = 'gmm/projected'
    self.m_tool.m_projected_ivec = 'projected'
    self.m_tool.m_projector_toreplace = self.m_configuration.projector_file
    self._ivec_training_configuration()

    # specify the file selector to be used
    self.m_file_selector = mytoolchain.FileSelectorIVector(
        self.m_database,
        preprocessed_directory = self.m_configuration.preprocessed_directory,
        extractor_file = self.m_configuration.extractor_file,
        features_directory = self.m_configuration.features_directory,
        projector_file = self.m_configuration.projector_file,
        projected_directory = self.m_configuration.projected_directory,
        whitening_projector_file = self.m_configuration.whitening_enroler_file,
        projected_whitening_directory = self.m_configuration.whitened_ivector_dir,
        projected_lnorm_directory = self.m_configuration.lnorm_ivector_dir,
        wccn_projector_file = self.m_configuration.wccn_projector_file,
        projected_wccn_directory = self.m_configuration.wccn_projected_ivector_dir,
        enroller_file = self.m_configuration.enroller_file,
    )

    # create the tool chain to be used to actually perform the parts of the experiments
    self.m_tool_chain = mytoolchain.ToolChainIVector(self.m_file_selector)

  def _ivec_training_configuration(self):
    """Configuration specific for this IVector toolchain"""
    self.m_configuration.whitening_enroler_file = os.path.join(self.m_configuration.temp_directory, self.m_args.whitening_enroler_file)
    self.m_configuration.wccn_projector_file = os.path.join(self.m_configuration.temp_directory, self.m_args.wccn_projector_file)
    self.m_configuration.whitened_ivector_dir = os.path.join(self.m_configuration.temp_directory, self.m_args.whitened_ivector_dir)
    self.m_configuration.lnorm_ivector_dir = os.path.join(self.m_configuration.temp_directory, self.m_args.lnorm_ivector_dir)
    self.m_configuration.wccn_projected_ivector_dir = os.path.join(self.m_configuration.temp_directory, self.m_args.wccn_projected_ivector_dir)


#######################################################################################
####################  Functions that will be executed in the grid  ####################
#######################################################################################

  def ivector_training(self, force=False):
    """Finally, the UBM is used to train the IVector projector/enroller."""
    if self.m_tool_chain.__check_file__(self.m_tool.m_ivec_filename, force, 800):
      utils.info("IVector training: Skipping IVector training since '%s' already exists" % self.m_tool.m_ivec_filename)
    else:
      # read UBM into the IVector class
      self.m_tool.m_ubm = bob.machine.GMMMachine(bob.io.HDF5File(self.m_tool.m_gmm_filename))

      # read training data
      training_list = self.m_file_selector.training_list('projected', 'train_projector')
      train_features = self.m_tool_chain.__read_features__(training_list, self.m_tool)

      # perform IVector training
      utils.info("IVector training: training IVector with %d clients" % len(train_features))
      self.m_tool._train_ivector(train_features)
      utils.ensure_dir(os.path.dirname(self.m_tool.m_ivec_filename))
      self.m_tool._save_projector_ivector_resolved(self.m_tool.m_ivec_filename)
      utils.info("IVector training: saved IVector matrix to '%s'" % self.m_tool.m_ivec_filename)
      self.m_tool._save_projector_together(self.m_configuration.projector_file)


  def ivector_project(self, indices=None, force=False):
    """Performs IVector projection"""
    # read UBM into the IVector class
    self.m_tool._load_projector_gmm_resolved(self.m_tool.m_gmm_filename)
    #ivec_file = self.m_configuration.projector_file
    self.m_tool._load_projector_ivector_resolved(self.m_tool.m_ivec_filename)

    projected_files = self.m_file_selector.projected_list()

    # select a subset of indices to iterate
    if indices != None:
      index_range = range(indices[0], indices[1])
      utils.info("- Projection: splitting of index range %s" % str(indices))
    else:
      index_range = range(len(projected_files))

    utils.info("- Projection: projecting %d gmm stats from directory '%s' to directory '%s'" % (len(index_range), self.m_tool._resolve_projected_gmm(self.m_file_selector.projected_directory), self.m_tool._resolve_projected_ivector(self.m_file_selector.projected_directory)))
    # extract the features
    for i in index_range:
      projected_file = projected_files[i]
      projected_file_gmm_resolved = self.m_tool._resolve_projected_gmm(projected_file)
      projected_file_ivec_resolved = self.m_tool._resolve_projected_ivector(projected_file)

      if not self.m_tool_chain.__check_file__(projected_file_ivec_resolved, force):
        # load feature
        feature = self.m_tool.read_feature(str(projected_file))
        # project feature
        projected = self.m_tool._project_ivector(feature)
        # write it
        utils.ensure_dir(os.path.dirname(projected_file_ivec_resolved))
        self.m_tool._save_feature_ivector(projected, str(projected_file))

#######################################################################################
##############  Functions dealing with submission and execution of jobs  ##############
#######################################################################################
  def execute_tool_chain(self):
    """Run the desired job of the ZT tool chain that is specified on command line."""
    # train the feature projector
    if not self.m_args.skip_ivector:
      if self.m_args.dry_run:
        print "Would have trained I-Vector ..."
      else:
        self.ivector_training(
            force = self.m_args.force)

    # project using ivector
    if not self.m_args.skip_ivector_projection:
      if self.m_args.dry_run:
        print "Would have projected I-Vector ..."
      else:
        self.ivector_project(
            force = self.m_args.force)

    # train model whitening enroler
    if not self.m_args.skip_whitening_enroler_training:
      if self.m_args.dry_run:
        print "Would have whitened I-Vectors ..."
      else:
        self.m_tool_chain.train_whitening_enroler(
            self.m_tool, 
            dir_type='projected',
            force = self.m_args.force)
    
    # project the features ivector
    if not self.m_args.skip_whitening_ivector:
      if self.m_args.dry_run:
        print "Would have whitened I-Vectors ..."
      else:
        self.m_tool_chain.whitening_ivector(
            self.m_tool, 
            dir_type='projected',
            force = self.m_args.force)

    # project the features ivector
    if not self.m_args.skip_lnorm_ivector:
      if self.m_args.dry_run:
        print "Would have projected l-norm ..."
      else:
        self.m_tool_chain.lnorm_ivector(
            self.m_tool, 
            dir_type='projected_whitening',
            force = self.m_args.force)
                
    # train WCCN projector
    if not self.m_args.skip_wccn_train_projector:
      if self.m_args.dry_run:
        print "Would have trained WCCN ..."
      else:
        self.m_tool_chain.wccn_train_projector(
            self.m_tool, 
            dir_type='projected_lnorm',
            force = self.m_args.force)
    
    # project the features ivector
    if not self.m_args.skip_wccn_projection:
      if self.m_args.dry_run:
        print "Would have projected WCCN ..."
      else:
        self.m_tool_chain.wccn_project_ivector(
            self.m_tool, 
            dir_type='projected_lnorm',
            force = self.m_args.force)


  def add_jobs_to_grid(self, external_dependencies):
    """Adds all (desired) jobs of the tool chain to the grid."""
    # collect the job ids
    job_ids = {}

    # if there are any external dependencies, we need to respect them
    deps = external_dependencies[:]

    # feature projection training
    if not self.m_args.skip_ivector:
      # check if we have a special queue for the IVector training (which usually needs a lot of memory)
      queue = self.m_grid.ivector_training_queue if hasattr(self.m_grid, 'ivector_training_queue') else self.m_grid.training_queue
      job_ids['ivector_training'] = self.submit_grid_job(
              'train-ivector',
              name="ivector",
              dependencies = deps,
              **queue)
      deps.append(job_ids['ivector_training'])

    # ivector projection
    if not self.m_args.skip_ivector_projection:
      job_ids['ivector-project'] = self.submit_grid_job(
              'ivector-project',
              name = 'ivector-project',
              list_to_split = self.m_file_selector.projected_list(),
              number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
              dependencies = deps,
              **self.m_grid.projection_queue)
      deps.append(job_ids['ivector-project'])

    # train whitening
    if not self.m_args.skip_whitening_enroler_training and hasattr(self.m_tool, 'train_whitening_enroler'):
      job_ids['whitening_enrolment_training'] = self.submit_grid_job(
              'train-whitening-enroler', 
              name = "w-e-training",
              dependencies = deps, 
              **self.m_grid.training_queue)
      deps.append(job_ids['whitening_enrolment_training'])
    
    # whitening i-vectors
    if not self.m_args.skip_whitening_ivector and hasattr(self.m_tool, 'whitening_ivector'):
      job_ids['whitening_ivector'] = self.submit_grid_job(
              'whitening-ivector', 
              list_to_split = self.m_file_selector.projected_list(),
              number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
              dependencies = deps, 
              **self.m_grid.projection_queue)
      deps.append(job_ids['whitening_ivector'])

    # lnorm i-vectors
    if not self.m_args.skip_lnorm_ivector and hasattr(self.m_tool, 'lnorm_ivector'):
      job_ids['lnorm_ivector'] = self.submit_grid_job(
              'lnorm-ivector', 
              list_to_split = self.m_file_selector.projected_whitening_list(),
              number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
              dependencies = deps, 
              **self.m_grid.projection_queue)
      deps.append(job_ids['lnorm_ivector'])

    # train WCCN projector
    if not self.m_args.skip_wccn_train_projector and hasattr(self.m_tool, 'wccn_train_projector'):
      job_ids['wccn_train_projector'] = self.submit_grid_job(
              'wccn-train-projector', 
              name = "wccn-proj-training",
              dependencies = deps, 
              **self.m_grid.training_queue)
      deps.append(job_ids['wccn_train_projector'])
    
    # WCCN projection
    if not self.m_args.skip_wccn_projection and hasattr(self.m_tool, 'wccn_project_ivector'):
      job_ids['wccn_project_ivector'] = self.submit_grid_job(
              'wccn-project-ivector', 
              list_to_split = self.m_file_selector.projected_lnorm_list(),
              number_of_files_per_job = self.m_grid.number_of_projected_features_per_job,
              dependencies = deps, 
              **self.m_grid.projection_queue)
      deps.append(job_ids['wccn_project_ivector'])
    
    # return the job ids, in case anyone wants to know them
    return job_ids


  def execute_grid_job(self):
    """Run the desired job of the ZT tool chain that is specified on command line."""
    # train the feature projector
    if self.m_args.sub_task == 'train-ivector':
      self.ivector_training(
          force = self.m_args.force)

    # project using ivector
    elif self.m_args.sub_task == 'ivector-project':
      self.ivector_project(
          indices = self.indices(self.m_file_selector.projected_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

    # train model whitening enroler
    elif self.m_args.sub_task == 'train-whitening-enroler':
      self.m_tool_chain.train_whitening_enroler(
          self.m_tool, 
          dir_type='projected',
          force = self.m_args.force)
    
    # project the features ivector
    elif self.m_args.sub_task == 'whitening-ivector':
      self.m_tool_chain.whitening_ivector(
          self.m_tool, 
          dir_type='projected',
          indices = self.indices(self.m_file_selector.projected_whitening_list(), self.m_grid.number_of_projected_features_per_job), 
          force = self.m_args.force)

    # project the features ivector
    elif self.m_args.sub_task == 'lnorm-ivector':
      self.m_tool_chain.lnorm_ivector(
          self.m_tool, 
          dir_type='projected_whitening',
          indices = self.indices(self.m_file_selector.projected_lnorm_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)
              
    # train WCCN projector
    elif self.m_args.sub_task == 'wccn-train-projector':
      self.m_tool_chain.wccn_train_projector(
          self.m_tool, 
          dir_type='projected_lnorm',
          force = self.m_args.force)
    
    # project the features ivector
    elif self.m_args.sub_task == 'wccn-project-ivector':
      self.m_tool_chain.wccn_project_ivector(
          self.m_tool, 
          dir_type='projected_lnorm',
          indices = self.indices(self.m_file_selector.projected_wccn_list(), self.m_grid.number_of_projected_features_per_job),
          force = self.m_args.force)

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
  config_group, dir_group, file_group, sub_dir_group, other_group, skip_group = ToolChainExecutorIVector.required_command_line_options(parser)

  config_group.add_argument('-P', '--protocol', metavar='PROTOCOL',
      help = 'Overwrite the protocol that is stored in the database by the given one (might not by applicable for all databases).')
  config_group.add_argument('-p', '--preprocessing', default = ['default-tan-triggs'], metavar = 'x', nargs = '+', dest = 'preprocessor', help = 'Image preprocessing configuration.')
  config_group.add_argument('-f', '--features', default = ['default-dct-blocks'], metavar = 'x', nargs = '+', help = 'Feature extraction configuration.')
  config_group.add_argument('-t', '--tool', metavar = 'x', nargs = '+', default = ['default-ivector'],
      help = 'IVector-based face recognition; registered face recognition tools are: %s'%utils.resources.resource_keys('tool'))
  config_group.add_argument('-g', '--grid', metavar = 'x', nargs = '+', required = False,
      help = 'Configuration file for the grid setup; needs to be specified.')

  file_group.add_argument('--whitening-enroler-file' , type = str, metavar = 'FILE', default = 'WhiteEnroler.hdf5',
      help = 'Name of the file to write the model of whitening enroler into')
  file_group.add_argument('--wccn-projector-file' , type = str, metavar = 'FILE', default = 'WCCNProjector.hdf5',
      help = 'Name of the file to write the model of WCCN projector into')
  
  sub_dir_group.add_argument('--gmm-directory', metavar = 'DIR', required = True,
        help = 'The directory containing the GMM-related files.')
  sub_dir_group.add_argument('--whitened-ivector-directory', type = str, metavar = 'DIR', default = 'whitened_ivector', dest = 'whitened_ivector_dir',
      help = 'Name of the directory where the projected data should be stored')
  sub_dir_group.add_argument('--lnorm-ivector-directory', type = str, metavar = 'DIR', default = 'lnorm_ivector', dest = 'lnorm_ivector_dir',
      help = 'Name of the directory where the projected data should be stored')
  sub_dir_group.add_argument('--wccn-projected-ivector-directory', type = str, metavar = 'DIR', default = 'wccn_projected_ivector', dest = 'wccn_projected_ivector_dir',
      help = 'Name of the directory where the projected data should be stored')
 
  #######################################################################################
  ############################ other options ############################################
  other_group.add_argument('-F', '--force', action='store_true',
      help = 'Force to erase former data if already exist')

  skip_group.add_argument('--skip-ivector', '--noi', action='store_true',
      help = "Skip the IVector step")
  skip_group.add_argument('--skip-ivector-projection', '--noip', action='store_true',
      help = "Skip the GMM ivector projection")
  skip_group.add_argument('--skip-whitening-enroler-training', '--nowenrt', action='store_true', dest='skip_whitening_enroler_training',
      help = 'Skip the training of the model whitening enrolment')
  skip_group.add_argument('--skip-whitening-ivector', '--nowivec', action='store_true', dest='skip_whitening_ivector',
      help = 'Skip whitening i-vectors')
  skip_group.add_argument('--skip-lnorm-ivector', '--nolnivec', action='store_true', dest='skip_lnorm_ivector',
      help = 'Skip lnorm i-vectors')
  skip_group.add_argument('--skip-wccn-train-projector', '--nowccnprojt', action='store_true', dest='skip_wccn_train_projector',
      help = 'Skip the training of the WCCN projector')
  skip_group.add_argument('--skip-wccn-projection', '--nowccnproj', action='store_true', dest='skip_wccn_projection',
      help = 'Skip projecting i-vectors on WCCN')

  #######################################################################################
  #################### sub-tasks being executed by this script ##########################
  parser.add_argument('--sub-task',
      choices = ('train-ivector', 'ivector-project', 'train-whitening-enroler', 'whitening-ivector', 'lnorm-ivector', 'wccn-train-projector', 'wccn-project-ivector'),
      help = argparse.SUPPRESS) #'Executes a subtask (FOR INTERNAL USE ONLY!!!)'
  parser.add_argument('--iteration', type=int,
      help = argparse.SUPPRESS) #'The current iteration of KMeans or GMM training'
  parser.add_argument('--model-type', choices = ['N', 'T'],
      help = argparse.SUPPRESS) #'Which type of models to generate (Normal or TModels)'
  parser.add_argument('--score-type', choices = ['A', 'B', 'C', 'D', 'Z'],
      help = argparse.SUPPRESS) #'The type of scores that should be computed'
  parser.add_argument('--group',
      help = argparse.SUPPRESS) #'The group for which the current action should be performed'

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
  executor = ToolChainExecutorIVector(args)
  # as the main entry point, check whether the grid option was given
  if not args.grid:
    if args.timer is not None and not len(args.timer):
      args.timer = ('real', 'system', 'user')
    # not in a grid, use default tool chain sequentially
    if args.timer:
      utils.info("- Timer: Starting timer")
      start_time = os.times()

    # Check if gmm directory exists
    gmm_dir = os.path.join(executor.m_configuration.temp_directory, 'gmm')
    if os.path.exists(gmm_dir):
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

    executor.write_info(command_line_parameters)

    executor.execute_tool_chain()

    if args.timer:
      end_time = os.times()
      utils.info("- Timer: Stopped timer")

      for t in args.timer:
        index = {'real':4, 'system':1, 'user':0}[t]
        print "Elapsed", t ,"time:", end_time[index] - start_time[index], "seconds"

    return {}

  elif args.sub_task:
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


