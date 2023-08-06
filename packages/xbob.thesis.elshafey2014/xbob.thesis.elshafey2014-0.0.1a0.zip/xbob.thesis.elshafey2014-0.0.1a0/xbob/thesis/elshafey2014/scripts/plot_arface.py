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

"""This script generates plots from the gbu experiments.
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
PROTOCOLS = ('illumination', 'occlusion', 'occlusion_and_illumination')
PROTOCOLS_LEGEND = ('illumination', 'occlusion', 'both')
DEFAULT_PATHS_1 = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u200', 'jfa_uv10', 'ivec400_cosine', 'ivec400_plda_fg50', 'sift_plda_fg40')
DEFAULT_PATHS_2 = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u10',  'jfa_uv2',  'ivec400_cosine', 'ivec400_plda_fg50', 'sift_plda_fg50')
DEFAULT_PATHS_3 = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u20',  'jfa_uv2',  'ivec400_cosine', 'ivec400_plda_fg50', 'sift_plda_fg50')


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-l', '--protocols-legend', default = PROTOCOLS_LEGEND, choices = PROTOCOLS_LEGEND, nargs = '+', help = "How to display the protocols in the legend")
  parser.add_argument('-a', '--algorithms', default = ALGORITHMS, choices = ALGORITHMS, nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('-b', '--algorithms-path-1', default = DEFAULT_PATHS_1, nargs = '+', help = "Select the base dir of the corresponding algorithms for the first protocol")
  parser.add_argument('-c', '--algorithms-path-2', default = DEFAULT_PATHS_2, nargs = '+', help = "Select the base dir of the corresponding algorithms for the second protocol")
  parser.add_argument('-d', '--algorithms-path-3', default = DEFAULT_PATHS_3, nargs = '+', help = "Select the base dir of the corresponding algorithms for the third protocol")
  parser.add_argument('-o', '--output', default = 'arface.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  protocols = args.protocols  
  protocols_legend = args.protocols_legend
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

  database = 'arface'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval'))

  figure = mpl.figure()
  results = {}
  x = numpy.array(range(1,len(algs)+1))
  eer = numpy.ndarray((len(protocols), len(algs)), dtype = numpy.float)
  eer[:] = numpy.nan
  hter = numpy.ndarray((len(protocols), len(algs)), dtype = numpy.float)
  hter[:] = numpy.nan

  # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
  for p, protocol in enumerate(protocols):
    protocols_legend_p = protocols_legend[p]
    for a, algorithm in enumerate(algs):
      algs_path = protocols_algs_path[protocol]
      algorithm_path = algs_path[a]
      assert 'scores' in files[algorithm_path]
      if protocol in files[algorithm_path]['scores']:
        if algorithm_path in files:
          e, h = measure.eer_hter(files[algorithm_path]['scores'][protocol]['nonorm']['scores-dev'], files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval'])
          print(algorithm, protocol, e * 100, h * 100)
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

  mpl.bar(x, y, color=c, align='center')
  mpl.axis((0, index-2, 0, numpy.nanmax(y) * 1.02))
  ticks = [(len(algs))/2. + .5 + i * (len(algs) +2) for i in range(len(protocols))]
  mpl.xticks(ticks, protocols_legend, va='baseline')

  # dirty HACK to generate legends
  l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
  legend_handle = mpl.legend(l, algs, loc=9, ncol=3, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  mpl.ylabel(r'HTER (\%)')
  mpl.xlabel(r'Illumination and/or occlusion condition')

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])
  figure = mpl.figure()

  # collect results specific to one occlusion type
  OCCLUSIONS = ('scarf', 'sunglasses')
  eer2 = numpy.ndarray((len(OCCLUSIONS), len(algs)), dtype = numpy.float)
  eer2[:] = numpy.nan
  hter2 = numpy.ndarray((len(OCCLUSIONS), len(algs)), dtype = numpy.float)
  hter2[:] = numpy.nan
  from xbob.db.arface.models import File
  for a, algorithm in enumerate(algs):
    for p, protocol in enumerate(protocols):
      protocols_legend_p = protocols_legend[p]
      if protocol in protocols_algs_path:
        algs_path = protocols_algs_path[protocol]
        algorithm_path = algs_path[a]
        pos_dev, neg_dev = dict([(o, []) for o in OCCLUSIONS]), dict([(o, []) for o in OCCLUSIONS])
        pos_eval, neg_eval = dict([(o, []) for o in OCCLUSIONS]), dict([(o, []) for o in OCCLUSIONS])
        if 'occlusion' in protocol and protocol in files[algorithm_path]['scores']:
          with open(files[algorithm_path]['scores'][protocol]['nonorm']['scores-dev']) as score_file:
            for line in score_file:
              splits = line.split()
              assert len(splits) == 4
              # get the image type
              occlusion = File(splits[2]).occlusion
              # extract the score
              score = float(splits[3])
              if splits[0] == splits[1]:
                pos_dev[occlusion].append(score)
              else:
                neg_dev[occlusion].append(score)

          with open(files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval']) as score_file:
            for line in score_file:
              splits = line.split()
              assert len(splits) == 4
              # get the image type
              occlusion = File(splits[2]).occlusion
              # extract the score
              score = float(splits[3])
              if splits[0] == splits[1]:
                pos_eval[occlusion].append(score)
              else:
                neg_eval[occlusion].append(score)

    # compute HTER for both occlusion types
    for o, occlusion in enumerate(OCCLUSIONS):
      thres = bob.measure.eer_threshold(neg_dev[occlusion], pos_dev[occlusion])
      far, frr = bob.measure.farfrr(neg_dev[occlusion], pos_dev[occlusion], thres)
      eer2[o,a] = (far+frr) * 50 # / 2 * 100 %
      far, frr = bob.measure.farfrr(neg_eval[occlusion], pos_eval[occlusion], thres)
      hter2[o,a] = (far+frr) * 50 # / 2 * 100 %
      print(protocol, algorithm, occlusion, eer2[o,a], hter2[o,a])

  # create plots split into the different occlusions
  x = range((len(algs) * 2 + 2) * (len(OCCLUSIONS)+1))
  y = [0] * len(x)
  c = [(0,0,0,0)] * len(x)
  index = 1
  for o in range(len(OCCLUSIONS)):
    for a in range(len(algs)):
      y[index] = hter2[o,a]
      c[index] = colors[a]
      index += 1
    index += 2

  mpl.bar(x, y, color=c, align='center' )
  mpl.axis((0, index-2, 0, numpy.nanmax(y) * 1.02))
  ticks = [(len(algs))/2. + .5 + i * (len(algs) +2) for i in range(len(OCCLUSIONS))]
  mpl.xticks(ticks, OCCLUSIONS, va='baseline')

  # dirty HACK to generate legends
  l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
  legend_handle = mpl.legend(l, algs, loc=9, ncol=3, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  mpl.ylabel(r'HTER (\%)')
  mpl.xlabel(r'Occlusion type')

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("\\TableHeader{" + "} {".join(sorted(algs)) + "}")
  for p, protocol in enumerate(protocols):
    print("\\TableContent{" + protocol + "} {" + "} {".join(["%3.2f} {%3.2f" % (eer[p,a], hter[p,a]) for a in range(len(algs))]) + ("}\n" if p < len(protocols)-1 else "}\\hline\n"))
  for o, occlusion in enumerate(OCCLUSIONS):
    print("\\TableContent{" + occlusion + "} {" + "} {".join(["%3.2f} {%3.2f" % (eer2[o,a], hter2[o,a]) for a in range(len(algs))]) + "}\n")


  pdf.close()
  return 0

if __name__ == "__main__":
  main()
