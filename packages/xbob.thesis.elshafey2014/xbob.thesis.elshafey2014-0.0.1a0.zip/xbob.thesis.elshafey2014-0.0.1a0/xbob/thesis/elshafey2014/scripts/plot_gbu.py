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

"""This script generates plots from the GBU experiments.
"""

import numpy
import bob
import os
import sys

from ..utils import measure
from .. import utils

import matplotlib
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=18)
matplotlib.rcParams['xtick.major.pad'] = 16 

ALGORITHMS = utils.ALGORITHMS
PROTOCOLS = ('Good', 'Bad', 'Ugly')
DEFAULT_PATHS = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u100', 'jfa_uv50', 'ivec400_cosine', 'ivec400_plda_fg40', 'sift_plda_fg40')

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
  parser.add_argument('-b', '--algorithms-path-1', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the first protocol")
  parser.add_argument('-c', '--algorithms-path-2', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the second protocol")
  parser.add_argument('-d', '--algorithms-path-3', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the third protocol")
  parser.add_argument('-o', '--output', default = 'gbu.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  protocols = args.protocols  
  algs = args.algorithms
  #algs_path = args.algorithms_path

  protocols_algs_path = {}
  if (len(protocols) >=1):
    assert( len(args.algorithms_path_1) == len(algs) )
    protocols_algs_path[protocols[0]] = args.algorithms_path_1
  if (len(protocols) >=2):
    assert( len(args.algorithms_path_2) == len(algs) )
    protocols_algs_path[protocols[1]] = args.algorithms_path_2
  if (len(protocols) >=3):
    assert( len(args.algorithms_path_3) == len(algs) )
    protocols_algs_path[protocols[2]] = args.algorithms_path_3

  database = 'gbu'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4)

  measure.plot_roc_det(pdf, protocols, protocols_algs_path, algs, files, database)

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
