#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Wed Apr  9 13:22:09 CEST 2014
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

"""This script postprocesses the scores from NIST SRE12
to calibrate them and to transform them as compound LLRs.
"""

import numpy
import bob
import os
import sys

from ..utils import measure
from .. import utils

NORM = ('nonorm', 'ztnorm')
PROTOCOLS = ('female', 'male')
DEFAULT_PATHS = ('gmm', 'isv_u200', 'jfa_uv100', 'jfa_uv50', 'ivec400_cosine', 'ivec400_plda_fg100', 'ivec400_plda_fg50')

def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-b', '--algorithms-path', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the protocol P")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  protocols = args.protocols  
  algs_path = args.algorithms_path

  protocols_algs_path = {}
  for p in protocols:
    protocols_algs_path[p] = algs_path

  database = 'nist_sre12'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval'))

  for p, protocol in enumerate(protocols):
    for n, norm in enumerate(NORM):
      for a, algorithm_path in enumerate(algs_path):
        assert 'scores' in files[algorithm_path]
        if protocol in files[algorithm_path]['scores']:
          if algorithm_path in files:
            filename_dev  = files[algorithm_path]['scores'][protocol][norm]['scores-dev']
            filename_eval = files[algorithm_path]['scores'][protocol][norm]['scores-eval']

            # Calibration
            filename_dev_cal  = filename_dev  + '.cal'
            filename_eval_cal = filename_eval + '.cal'
            machine = utils.train_llr([filename_dev])
            utils.fuse(machine, [filename_dev], filename_dev_cal)
            utils.fuse(machine, [filename_eval], filename_eval_cal)

            # Compound LLR
            filename_dev_cal_comp  = filename_dev_cal  + '.compound'
            filename_eval_cal_comp = filename_eval_cal + '.compound'
            utils.compound_llr_files(filename_dev_cal, filename_dev_cal_comp)
            utils.compound_llr_files(filename_eval_cal, filename_eval_cal_comp)

  return 0

if __name__ == "__main__":
  main()
