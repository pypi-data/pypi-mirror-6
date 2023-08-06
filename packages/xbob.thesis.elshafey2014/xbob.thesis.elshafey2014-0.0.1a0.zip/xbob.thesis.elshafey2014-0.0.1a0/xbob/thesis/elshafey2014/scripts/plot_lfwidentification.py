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

"""This script generates plots from the LFW Identification experiments.
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
  parser.add_argument('-o', '--output', default = 'lfwidentification.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  results_dir = args.results_directory
  protocols = args.protocols  
  algs = args.algorithms
  algs_path = args.algorithms_path

  database = 'lfwidentification'
  files = measure.parse_results(os.path.join(results_dir, database), 4, score_files = ('scores-eval',))

    # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
  for p, protocol in enumerate(protocols):
    cmc_scores = []
    for a, algorithm in enumerate(algs):
      algorithm_path = DEFAULT_PATHS[a]
      assert 'scores' in files[algorithm_path]
      if protocol in files[algorithm_path]['scores']:
        if algorithm_path in files:
          assert protocol in files[algorithm_path]['scores']
          assert 'nonorm' in files[algorithm_path]['scores'][protocol]
          assert 'scores-eval' in files[algorithm_path]['scores'][protocol]['nonorm']
          filename = files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval']
          cmc_scores.append(bob.measure.load.cmc_four_column(filename))

    for logx in [False, True]:
      figure = mpl.figure()
      for a, algorithm in enumerate(algs):
        color = measure.mycolor(algorithm)
        markersize = 10
        marker = measure.mymarker(algorithm)
        bob.measure.plot.cmc(cmc_scores[a], logx=logx, linestyle=marker[0], marker=marker[1], color=color, lw=2, ms=markersize, mew=2, markevery=50)
      bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
      legend_handle = mpl.legend(algs, ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y), numpoints=1)
      if logx == False:
        mpl.xlabel(r'Rank')
      else:
        mpl.xlabel(r'Rank')
      mpl.ylabel(r'Hit (\%)')
      pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
