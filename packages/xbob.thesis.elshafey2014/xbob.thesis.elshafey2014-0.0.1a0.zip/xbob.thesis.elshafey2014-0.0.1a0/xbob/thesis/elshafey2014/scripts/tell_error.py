#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Thu Jan  9 19:07:27 CET 2014
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

"""This script tells the largest error performed by a recognition system
on the identification protocol of LFW.
"""

import numpy
import bob
import os
import sys

from ..utils import measure
from .. import utils

ALGORITHMS = utils.ALGORITHMS
PROTOCOLS = ('P0',)
DEFAULT_PATHS = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u10', 'jfa_uv10', 'ivec400_cosine', 'ivec400_plda_fg60', 'sift_plda_fg20')


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-a', '--algorithms', default = ALGORITHMS, choices = ALGORITHMS, nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('-d', '--algorithms-path', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the third protocol")
  parser.add_argument('-n', '--number-trials', default = 2, type=int, help = "The number of trials to return for each algorithm and protocol")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  results_dir = args.results_directory
  protocols = args.protocols  
  algs = args.algorithms
  algs_path = args.algorithms_path
  n_trials = args.number_trials

  database = 'lfwidentification'
  files = measure.parse_results(os.path.join(results_dir, database), 4, score_files = ('scores-eval',))

    # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
  for p, protocol in enumerate(protocols):
    cmc_scores = []
    for a, algorithm in enumerate(algs):
      algorithm_path = algs_path[a]
      assert 'scores' in files[algorithm_path]
      if protocol in files[algorithm_path]['scores']:
        if algorithm_path in files:
          assert protocol in files[algorithm_path]['scores']
          assert 'nonorm' in files[algorithm_path]['scores'][protocol]
          assert 'scores-eval' in files[algorithm_path]['scores'][protocol]['nonorm']
          filename = files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval']
          data = bob.measure.load.four_column(filename)
          high_score_negatives = []
          low_score_positives = []
          for k in data:
            if k[0] == k[1]:
              if len(low_score_positives) < n_trials:
                low_score_positives.append(k)
              else:
                if k[3] < low_score_positives[0][3]:
                  low_score_positives[0] = k
              low_score_positives_ =  sorted(low_score_positives, key=lambda x: x[3], reverse=True)
              low_score_positives = low_score_positives_
            else:
              if len(high_score_negatives) < n_trials:
                high_score_negatives.append(k)
              else:
                if k[3] > high_score_negatives[0][3]:
                  high_score_negatives[0] = k
              high_score_negatives_ = sorted(high_score_negatives,  key=lambda x: x[3])
              high_score_negatives = high_score_negatives_
          print(protocol)
          print(algorithm)
          print(low_score_positives)
          print(high_score_negatives)

  return 0

if __name__ == "__main__":
  main()
