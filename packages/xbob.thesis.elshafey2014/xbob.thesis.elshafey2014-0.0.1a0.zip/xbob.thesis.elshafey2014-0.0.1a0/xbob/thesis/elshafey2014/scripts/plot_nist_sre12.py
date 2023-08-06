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

"""This script generates plots from the NIST SRE12 experiments.
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


ALGORITHMS = utils.ALGORITHMS_SPK
NORM = ('nonorm', 'ztnorm')
PROTOCOLS = ('female', 'male')
DEFAULT_PATHS = ('gmm', 'isv_u200', 'jfa_uv100', 'ivec400_cosine', 'ivec400_plda_fg100',)

#female_values = (23.97, 38.20, 8.10, 27.68, 10.53, 32.44, 11.78, 36.50, 9.02, 21.93)
#male_values =       (19.93, 40.38, 7.62, 30.72, 11.82, 37.65, 11.21, 38.57, 8.21, 24.86)
female_nonorm_values = (24.12, 34.21, 9.29, 24.21, 12.22, 24.54, 9.48, 33.97, 7.57, 23.15)
female_ztnorm_values = (23.97, 38.20, 8.10, 27.68, 10.58, 33.38, 11.78, 36.50, 6.86, 20.26)
male_nonorm_values = (23.55, 36.18, 8.80, 25.13, 10.40, 24.69, 8.89, 35.83, 6.39, 25.19)
male_ztnorm_values = (19.93, 40.38, 7.62, 30.72, 9.40, 34.80, 11.21, 38.57, 6.85, 25.50)



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
  parser.add_argument('-o', '--output', default = 'nist_sre12.pdf', help = "The file to contain the plot")

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

  det_list = [1e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 4e-1, 8e-1]

  database = 'nist_sre12'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval', 'scores-dev.cal.compound', 'scores-eval.cal.compound'))

  #measure.plot_banca(pdf, protocols, protocols_algs_path, algs, files, database)
  results = {}
  x = numpy.array(range(1,len(algs)+1))
  eer = numpy.ndarray((len(protocols), len(NORM), len(algs)), dtype = numpy.float)
  eer[:] = numpy.nan
  hter = numpy.ndarray((len(protocols), len(NORM), len(algs)), dtype = numpy.float)
  hter[:] = numpy.nan

  if True:
    # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
    print "HTER"
    for p, protocol in enumerate(protocols):
      print protocol
      for n, norm in enumerate(NORM):
        print norm
        for a, algorithm in enumerate(algs):
          print algorithm
          algs_path = protocols_algs_path[protocol]
          algorithm_path = algs_path[a]
          assert 'scores' in files[algorithm_path]
          if protocol in files[algorithm_path]['scores']:
            if algorithm_path in files:
              e, h = measure.eer_hter(files[algorithm_path]['scores'][protocol][norm]['scores-dev'], files[algorithm_path]['scores'][protocol][norm]['scores-eval'])
              #print(algorithm, protocol, e * 100, h * 100)
              eer[p,n,a] = e * 100 
              hter[p,n,a] = h * 100 
  else:
    for i in range(len(male_nonorm_values)/2):
      eer[0, 0, i] = male_nonorm_values[2*i]
      hter[0, 0, i] = male_nonorm_values[2*i+1]
      eer[0, 1, i] = male_ztnorm_values[2*i]
      hter[0, 1, i] = male_ztonorm_values[2*i+1]
      eer[1, 0, i] = female_nonorm_values[2*i]
      hter[1, 0, i] = female_nonorm_values[2*i+1]
      eer[1, 1, i] = female_ztnorm_values[2*i]
      hter[1, 1, i] = female_ztnorm_values[2*i+1]

  # create plots split into the different protocols
  colors = [measure.mycolor(algs[a]) for a in range(len(algs))]
  x = range(len(algs) * 2 + 2)
  y = [0] * len(x)
  c = [(0,0,0,0)] * len(x)
  for p in range(len(protocols)):
    for n in range(len(NORM)):
      figure = mpl.figure()
      index = 0 
      for a in range(len(algs)):
        y[index] = eer[p,n,a]
        c[index] = colors[a]
        index += 1
      index += 2
      for a in range(len(algs)):
        y[index] = hter[p,n,a]
        c[index] = colors[a]
        index += 1

      mpl.bar(x, y, color=c, align='center' )
      mpl.axis((-1, index, 0, 41))
      ticks = [len(algs)/2. + i*(len(algs) + 2) for i in range(2)]
      mpl.xticks(ticks, ['Development', 'Evaluation'], va='baseline')

      # dirty HACK to generate legends
      l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
      bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
      legend_handle = mpl.legend(l, algs, loc=9, ncol=3, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
      mpl.ylabel(r'EER/HTER (\%)')

      pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("")
  print("\\TableHeader{" + "} {".join(sorted(algs)) + "}")
  for p, protocol in enumerate(protocols):
    for n, norm in enumerate(NORM):
      print("\\TableContent{" + protocol + "} {" + norm+ "} {" + "} {".join(["%3.2f} {%3.2f" % (eer[p,n,a], hter[p,n,a]) for a in range(len(algs))]) + ("}" if p < len(protocols)-1 else "}\\hline"))
  print("")


  print "DET"
  for p, protocol in enumerate(protocols):
    print protocol
    for n, norm in enumerate(NORM):
      print norm
      figure = mpl.figure()
      list_systems = []
      for a, algorithm in enumerate(algs):
        print algorithm
        algs_path = protocols_algs_path[protocol]
        algorithm_path = algs_path[a]
        assert 'scores' in files[algorithm_path]
        if protocol in files[algorithm_path]['scores']:
          if algorithm_path in files:
            filename_eval = files[algorithm_path]['scores'][protocol][norm]['scores-eval.cal.compound']
            neg, pos = bob.measure.load.split_four_column(filename_eval)
            frr, far = bob.measure.det(neg, pos, 1000) # Bob 1.2.x returns this order (more recent version returns far, frr)
            marker =  measure.mymarker(ALGORITHMS[a])
            color = measure.mycolor(ALGORITHMS[a])
            mpl.plot(far, frr, marker, color = color, lw=2, ms=10, mew=2, markevery=15)
          list_systems.append(ALGORITHMS[a])

      ticks = [bob.measure.ppndf(d) for d in det_list]
      labels = [("%.5f" % (d*100)).rstrip('0').rstrip('.') for d in det_list]
      mpl.xticks(ticks, labels)
      mpl.yticks(ticks, labels)
      mpl.axis((ticks[0], ticks[-1], ticks[0], ticks[-1]))

      mpl.xlabel('False Acceptance Rate (\%)')
      mpl.ylabel('False Rejection Rate (\%)')
      mpl.grid(True, color=(0.3,0.3,0.3))
      bbox_anchor_y = (1.10 + 0.05 * ((len(algs_path)-1) / 3 + 1))
      legend_handle = mpl.legend(list_systems, ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y), numpoints=1)
   
      pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
