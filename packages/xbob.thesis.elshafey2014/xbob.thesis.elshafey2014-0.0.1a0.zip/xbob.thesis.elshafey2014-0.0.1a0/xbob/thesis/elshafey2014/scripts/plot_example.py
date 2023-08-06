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

"""This script generates sample ROC, DET and CMM curves from the ARface experiments.
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


DATABASE = 'arface'
ALGORITHM = 'PCA'
NORM = 'nonorm'
PROTOCOL = 'illumination'
ALGORITHM_PATH = 'pca'



def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-o', '--output', default = 'example.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  far_list = measure.myfar_list()
  det_list = [1e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 4e-1, 8e-1]
  cmc_list = [1, 5, 10, 20, 50, 100]
  colors = ('r', 'g')
  markers = ('x', 'o') 

  files = measure.parse_results(os.path.join(args.results_directory, DATABASE), 4, ('scores-dev', 'scores-eval'))

  assert ALGORITHM_PATH in files
  assert 'scores' in files[ALGORITHM_PATH]
  assert PROTOCOL in files[ALGORITHM_PATH]['scores']
  assert NORM in files[ALGORITHM_PATH]['scores'][PROTOCOL]
  if NORM in files[ALGORITHM_PATH]['scores'][PROTOCOL]:
    # DET
    figure = mpl.figure()
    for d, de in enumerate(('scores-dev', 'scores-eval')):
      assert de in files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM]
      filename = files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM][de]
      neg, pos = bob.measure.load.split_four_column(filename)
      frr, far = bob.measure.det(neg, pos, 1000) # Bob 1.2.x returns this order (more recent version returns far, frr)
      marker = markers[d]
      color = colors[d]
      mpl.plot(far, frr, marker, ls='-', color = color, lw=2, ms=10, mew=2, markevery=15)
    ticks = [bob.measure.ppndf(d) for d in det_list]
    labels = [("%.5f" % (d*100)).rstrip('0').rstrip('.') for d in det_list]
    mpl.xticks(ticks, labels)
    mpl.yticks(ticks, labels)
    mpl.axis((ticks[0], ticks[-1], ticks[0], ticks[-1]))
    mpl.xlabel('False Acceptance Rate (\%)')
    mpl.ylabel('False Rejection Rate (\%)')
    mpl.grid(True, color=(0.3,0.3,0.3))
    #bbox_anchor_y = (1.10 + 0.05 * ((len(algs_path)-1) / 3 + 1))
    pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25)

    # ROC
    figure = mpl.figure()
    for d, de in enumerate(('scores-dev', 'scores-eval')):
      assert de in files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM]
      filename = files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM][de]
      neg, pos = bob.measure.load.split_four_column(filename)
      roc = bob.measure.roc_for_far(neg, pos, far_list)[1]
      rocs = [r*100 for r in roc]
      marker = markers[d]
      color = colors[d]
      mpl.semilogx(far_list, rocs, marker, ls='-', color = color, lw=2, ms=10, mew=2)
    mpl.axis((far_list[0], 1, 0, 100))
    mpl.xticks([far_list[i] for i in range(0,len(far_list)+1,4)], [("%.4f" % (far_list[i]*100)).rstrip('0').rstrip('.') + "\%" for i in range(0,len(far_list)+1,4)], va='baseline')
    mpl.yticks(range(0, 101, 20), ["%d\%%" % d for d in range(0, 101, 20)])
    mpl.xlabel(r'False Acceptance Rate (\%)')
    mpl.ylabel(r'Correct Acceptance Rate (\%)')
    pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25)

    # CMC
    figure = mpl.figure()
    for d, de in enumerate(('scores-dev', 'scores-eval')):
      assert de in files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM]
      filename = files[ALGORITHM_PATH]['scores'][PROTOCOL][NORM][de]
      cmc_scores = bob.measure.load.cmc_four_column(filename)
      marker = markers[d]
      color = colors[d]
      bob.measure.plot.cmc(cmc_scores, logx=True, marker=marker, ls='-', color=color, lw=2, ms=10, mew=2, markevery=2)
    mpl.xticks(cmc_list, ["%d" % (val,) for val in cmc_list])
    mpl.xlabel(r'Rank')
    mpl.ylabel(r'Hit (\%)')
    pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25)

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
