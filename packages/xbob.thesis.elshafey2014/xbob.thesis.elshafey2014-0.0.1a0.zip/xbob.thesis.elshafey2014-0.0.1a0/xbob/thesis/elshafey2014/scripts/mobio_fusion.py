#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Tue Jan 8 13:36:12 CET 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
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

"""This script fuses scores from the MOBIO database in various ways."""

import bob
import os
import sys
import numpy

from .. import utils


DATABASES = ('mobio_face', 'mobio_speaker')
PROTOCOLS = ('mobile1-female', 'mobile1-male', 'laptop1-female', 'laptop1-male', 'laptop_mobile1-female', 'laptop_mobile1-male')
NORMS = ('nonorm', 'ztnorm')

BIMODAL_SYSTEMS = ('b-gmm', 'b-isv', 'b-jfa', 'b-tv-cosine', 'b-tv-plda')
MULTI_ALGORITHM_SYSTEMS = ('f-all', 's-all')
BIMODAL_MULTI_ALGORITHM_SYSTEMS = ('b-all', )

DEFAULT_PATHS = {}

DEFAULT_PATHS['mobio_face'] = {}
DEFAULT_PATHS['mobio_face']['mobile1-female']           = ('gmm', 'isv_u200', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['mobile1-male']             = ('gmm', 'isv_u200', 'jfa_uv30', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_face']['laptop1-female']           = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['laptop1-male']             = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_face']['laptop_mobile1-female']    = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['laptop_mobile1-male']      = ('gmm', 'isv_u200', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg50')

DEFAULT_PATHS['mobio_speaker'] = {}
DEFAULT_PATHS['mobio_speaker']['mobile1-female']        = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['mobile1-male']          = ('gmm',  'isv_u20',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop1-female']        = ('gmm',  'isv_u20',  'jfa_uv2', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop1-male']          = ('gmm',  'isv_u20',  'jfa_uv2', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop_mobile1-female'] = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop_mobile1-male']   = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')


def fuse_scores(machine, score_files, output_file):
  """Fuses the selected score files with the given machine and writes the results to the given file."""
  # read all score files; these score files need to have the scores in the same order.
  score_file_lines = [bob.measure.load.four_column(f) for f in score_files]

  # get the first score file as reference
  first = score_file_lines[0]
  score_count = len(first)
  # create output file
  output = open(output_file, 'w')
  # iterate over the client/probe pairs
  for i in range(score_count):
    # get the raw scores of all systems for this specific client/probe pair
    raw_scores = [float(line[i][-1]) for line in score_file_lines]
    # fuse these scores into one value by using the given machine
    fused_score = machine(raw_scores)
    # write the fused score to file, using the reference client id, probe id and probe name
    output.write("%s %s %s %f\n" % (first[i][0] , first[i][1], first[i][2], fused_score))


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-f', '--fusion-subdirectory', default = 'mobio_fusion', help = 'The subdirectory containing the fused results (score files).')

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  results_dir = args.results_directory
  fusion_dir = args.fusion_subdirectory

  # Bimodal systems
  for i, s in enumerate(BIMODAL_SYSTEMS): # 5 algorithms: GMM, ISV, JFA, TV-Cosine, TV-PLDA
    for p in args.protocols:
      for norm in NORMS:
        # Development filenames
        filenames_dev = []
        for d in DATABASES:
          filenames_dev.append(os.path.join(results_dir, d, DEFAULT_PATHS[d][p][i], 'scores', p, norm, 'scores-dev'))

        # Train LLR machine
        machine = utils.train_llr(filenames_dev)

        # Evaluation filenames
        f_dev = []
        f_eval = []
        for d in DATABASES:
          f_dev.append(os.path.join(results_dir, d, DEFAULT_PATHS[d][p][i], 'scores', p, norm, 'scores-dev'))
          f_eval.append(os.path.join(results_dir, d, DEFAULT_PATHS[d][p][i], 'scores', p, norm, 'scores-eval'))

        # Output filenames
        f_out_dev = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-dev')
        f_out_eval = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-eval')
        utils.ensure_dir(f_out_dev)

        # Fuse scores
        fuse_scores(machine, f_dev, f_out_dev)
        fuse_scores(machine, f_eval, f_out_eval)

  # Multi-algorithm systems
  for i, s in enumerate(MULTI_ALGORITHM_SYSTEMS): # 5 algorithms: GMM, ISV, JFA, TV-Cosine, TV-PLDA
    d = DATABASES[i]
    for p in args.protocols:
      for norm in NORMS:
        # Development filenames
        filenames_dev = []
        for alg in DEFAULT_PATHS[d][p]:
          filenames_dev.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-dev'))

        # Train LLR machine
        machine = utils.train_llr(filenames_dev)

        # Evaluation filenames
        f_dev = []
        f_eval = []
        for alg in DEFAULT_PATHS[d][p]:
          f_dev.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-dev'))
          f_eval.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-eval'))

        # Output filenames
        f_out_dev = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-dev')
        f_out_eval = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-eval')
        utils.ensure_dir(f_out_dev)

        # Fuse scores
        fuse_scores(machine, f_dev, f_out_dev)
        fuse_scores(machine, f_eval, f_out_eval)
 
  # Bimodal multi-algorithm systems
  for i, s in enumerate(BIMODAL_MULTI_ALGORITHM_SYSTEMS): # (only one)
    for p in args.protocols:
      for norm in NORMS:
        # Development filenames
        filenames_dev = []
        for d in DATABASES:
          for alg in DEFAULT_PATHS[d][p]:
            filenames_dev.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-dev'))

        # Train LLR machine
        machine = utils.train_llr(filenames_dev)

        # Evaluation filenames
        f_dev = []
        f_eval = []
        for d in DATABASES:
          for alg in DEFAULT_PATHS[d][p]:
            f_dev.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-dev'))
            f_eval.append(os.path.join(results_dir, d, alg, 'scores', p, norm, 'scores-eval'))

        # Output filenames
        f_out_dev = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-dev')
        f_out_eval = os.path.join(results_dir, fusion_dir, s, 'scores', p, norm, 'scores-eval')
        utils.ensure_dir(f_out_dev)

        # Fuse scores
        fuse_scores(machine, f_dev, f_out_dev)
        fuse_scores(machine, f_eval, f_out_eval)
  
  return 0

if __name__ == "__main__":
  main()
