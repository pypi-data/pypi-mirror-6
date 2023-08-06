#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri Aug 30 11:50:25 CEST 2013
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

import os
import numpy
import bob

from facereclib import utils
from facereclib.toolchain import ToolChain

class ToolChainIVector(ToolChain):
  """This class includes functionalities for an I-Vector tool chain to produce verification scores"""

  def __init__(self, file_selector):
    """Initializes the tool chain object with the current file selector."""
    # call base class constructor with its set of parameters
    ToolChain.__init__(self, file_selector)
 

  ###############################################
  ####### Functions related to whitening ########
  ###############################################
  
  # Function 1/
  def train_whitening_enroler(self, tool, dir_type=None, force=False):
    """Traines the model enrolment stage using the projected features"""
    self.m_tool = tool
    if hasattr(tool, 'train_whitening_enroler'):
      enroler_file = self.m_file_selector.whitening_projector_file
      if self.__check_file__(enroler_file, force, 1000):
        utils.info("Enroler '%s' already exists." % enroler_file)
      else:
        # training models
        train_files = self.m_file_selector.training_list(dir_type, 'train_enroller', arrange_by_client=True)
        # perform training
        utils.info("Training Enroler '%s' using %d identities: " %(enroler_file, len(train_files)))
        tool.train_whitening_enroler(train_files, str(enroler_file))

  # Function 2/
  def whitening_ivector(self, tool, dir_type=None, indices = None, force=False):
    """Extract the ivectors for all files of the database"""
    self.m_tool = tool
    # load the projector file
    if hasattr(tool, 'whitening_ivector'):        
      if hasattr(tool, 'load_whitening_enroler'):
        tool.load_whitening_enroler(self.m_file_selector.whitening_projector_file)
      input_ivector_files = self.m_file_selector.projected_list()
      whitened_ivector_files = self.m_file_selector.projected_whitening_list()
      # extract the features
      if indices != None:
        index_range = range(indices[0], indices[1])
        utils.info("- Projection: splitting of index range %s" % str(indices))
      else:
        index_range = range(len(input_ivector_files))
      utils.info("project %d %s i-vectors to directory %s using Whitening Enroler" %(len(index_range), dir_type, self.m_file_selector.projected_whitening_directory))
      for k in index_range:
        ivector_file = input_ivector_files[k]
        whitened_ivector_file = whitened_ivector_files[k] 
        if not self.__check_file__(whitened_ivector_file, force): 
          ivector = bob.io.load(str(ivector_file))
          # project ivector feature
          whitened_ivector = tool.whitening_ivector(ivector)
          # write it
          utils.ensure_dir(os.path.dirname(whitened_ivector_file))
          bob.io.save(whitened_ivector, str(whitened_ivector_file))
  
  
  
  ##############################################
  ########## Function related to Lnorm #########
  ##############################################
  
  # Function 2/
  def lnorm_ivector(self, tool, dir_type=None, indices = None, force=False):
    """Extract the ivectors for all files of the database"""
    self.m_tool = tool
    # load the projector file
    if hasattr(tool, 'lnorm_ivector'):        
      input_ivector_files = self.m_file_selector.projected_whitening_list()
      lnorm_ivector_files = self.m_file_selector.projected_lnorm_list()
      # extract the features
      if indices != None:
        index_range = range(indices[0], indices[1])
        utils.info("- Projection: splitting of index range %s" % str(indices))
      else:
        index_range = range(len(input_ivector_files))
      utils.info("project %d %s i-vectors to directory %s" %(len(index_range), dir_type, self.m_file_selector.projected_lnorm_directory))
      for k in index_range:
        ivector_file = input_ivector_files[k]
        lnorm_ivector_file = lnorm_ivector_files[k] 
        if not self.__check_file__(lnorm_ivector_file, force): 
          ivector = bob.io.load(str(ivector_file))
          # project ivector feature
          lnorm_ivector = tool.lnorm_ivector(ivector)
          # write it
          utils.ensure_dir(os.path.dirname(lnorm_ivector_file))
          bob.io.save(lnorm_ivector, str(lnorm_ivector_file))

  ###################################################
  ################ WCCN projection ##################
  ###################################################
  
  # Function 1/
  def wccn_train_projector(self, tool, dir_type=None, force=False):
    """Traines the WCCN projector stage using the features given in dir_type"""
    self.m_tool = tool
    if hasattr(tool, 'wccn_train_projector'):
      wccn_projector_file = self.m_file_selector.wccn_projector_file
      if self.__check_file__(wccn_projector_file, force, 1000):
        utils.info("Projector '%s' already exists." % wccn_projector_file)
      else:
        train_files = self.m_file_selector.training_list(dir_type, 'train_enroller', arrange_by_client=True)
        # perform WCCN training
        utils.info("Training WCCN Projector '%s' using %d identities: " %(wccn_projector_file, len(train_files)))
        tool.wccn_train_projector(train_files, str(wccn_projector_file))
        
  # Function 2/
  def wccn_project_ivector(self, tool, dir_type=None, indices = None, force=False):
    """Project the ivectors using WCCN projection"""
    self.m_tool = tool
    # load the projector file
    if hasattr(tool, 'wccn_project_ivector'):        
      if hasattr(tool, 'wccn_load_projector'):
        tool.wccn_load_projector(self.m_file_selector.wccn_projector_file)
      input_ivector_files = self.m_file_selector.projected_lnorm_list()
      wccn_projected_ivector_files = self.m_file_selector.projected_wccn_list()
      # extract the features
      if indices != None:
        index_range = range(indices[0], indices[1])
        utils.info("- Projection: splitting of index range %s" % str(indices))
      else:
        index_range = range(len(input_ivector_files))
      utils.info("project %d %s i-vectors to directory %s using WCCN Projector" %(len(index_range), dir_type, self.m_file_selector.projected_wccn_directory))
      for k in index_range:
        lnorm_projected_ivector_file = input_ivector_files[k]
        wccn_projected_ivector_file = wccn_projected_ivector_files[k]
        if not self.__check_file__(wccn_projected_ivector_file, force):
          lnorm_projected_ivector = bob.io.load(str(lnorm_projected_ivector_file))
          # project ivector feature using WCCN
          wccn_projected_ivector = tool.wccn_project_ivector(lnorm_projected_ivector)
          # write it
          utils.ensure_dir(os.path.dirname(wccn_projected_ivector_file))
          bob.io.save(wccn_projected_ivector, str(wccn_projected_ivector_file))
          
