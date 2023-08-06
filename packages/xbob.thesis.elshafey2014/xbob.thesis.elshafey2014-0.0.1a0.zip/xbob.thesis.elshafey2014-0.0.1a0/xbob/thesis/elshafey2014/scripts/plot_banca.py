#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Thu Jan  9 19:07:27 CET 2014
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

"""This script generates plots from the BANCA experiments.
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
PROTOCOLS = ('P',)
DEFAULT_PATHS = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u100', 'jfa_uv2', 'ivec200_cosine', 'ivec200_plda_fg30', 'sift_plda_fg30')


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-a', '--algorithms', default = ALGORITHMS, choices = ALGORITHMS, nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('-b', '--algorithms-path', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the protocol P")
  parser.add_argument('-o', '--output', default = 'banca.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  protocols = args.protocols  
  algs = args.algorithms
  algs_path = args.algorithms_path

  protocols_algs_path = {}
  for p in protocols:
    protocols_algs_path[p] = algs_path

  database = 'banca'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval'))

  #measure.plot_banca(pdf, protocols, protocols_algs_path, algs, files, database)
  figure = mpl.figure()
  results = {}
  x = numpy.array(range(1,len(algs)+1))
  eer = numpy.ndarray((len(protocols), len(algs)), dtype = numpy.float)
  eer[:] = numpy.nan
  hter = numpy.ndarray((len(protocols), len(algs)), dtype = numpy.float)
  hter[:] = numpy.nan

  # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
  for p, protocol in enumerate(protocols):
    for a, algorithm in enumerate(algs):
      algs_path = protocols_algs_path[protocol]
      algorithm_path = algs_path[a]
      assert 'scores' in files[algorithm_path]
      if protocol in files[algorithm_path]['scores']:
        if algorithm_path in files:
          e, h = measure.eer_hter(files[algorithm_path]['scores'][protocol]['ztnorm']['scores-dev'], files[algorithm_path]['scores'][protocol]['ztnorm']['scores-eval'])
          #print(algorithm, protocol, e * 100, h * 100)
          eer[p,a] = e * 100 
          hter[p,a] = h * 100 

  # create plots split into the different protocols
  colors = [measure.mycolor(algs[a]) for a in range(len(algs))]
  x = range((len(algs) * 2 + 2) * (len(protocols)+1))
  y = [0] * len(x)
  c = [(0,0,0,0)] * len(x)
  index = 1 
  for p in range(len(protocols)):
    for a in range(len(algs)):
      y[index] = hter[p,a]
      c[index] = colors[a]
      index += 1
    index += 2

  mpl.bar(x, y, color=c, align='center' )
  mpl.axis((0, index-2, 0, numpy.nanmax(y)* 1.02))
  ticks = [(len(algs))/2. + .5 + i * (len(algs) +2) for i in range(len(protocols))]
  mpl.xticks(ticks, protocols, va='baseline')

  # dirty HACK to generate legends
  l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
  legend_handle = mpl.legend(l, algs, loc=9, ncol=3, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  mpl.ylabel(r'HTER (\%)')

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("")
  print("\\TableHeader{" + "} {".join(sorted(algs)) + "}")
  for p, protocol in enumerate(protocols):
    print("\\TableContent{" + protocol + "} {" + "} {".join(["%3.2f} {%3.2f" % (eer[p,a], hter[p,a]) for a in range(len(algs))]) + ("}" if p < len(protocols)-1 else "}\\hline"))
  print("")





  pdf.close()
  return 0

if __name__ == "__main__":
  main()
