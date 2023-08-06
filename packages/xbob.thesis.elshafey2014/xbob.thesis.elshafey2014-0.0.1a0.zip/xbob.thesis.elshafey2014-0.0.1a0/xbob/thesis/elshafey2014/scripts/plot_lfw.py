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

"""This script generates plots from the LFW experiments.
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
DEFAULT_PATHS = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u100', 'jfa_uv50', 'ivec400_cosine', 'ivec400_plda_fg40', 'sift_plda_fg50')


def plot_lfw(pdf, algs_path, algs, files, database):
  
  # for lfw, we just report the final result

  scores = {}
  folds = {}

  folds_name = ('fold1', 'fold2', 'fold3', 'fold4', 'fold5', 'fold6', 'fold7','fold8', 'fold9', 'fold10')
  errors = {}
  means = {}
  stds = {}
  for a, algorithm in enumerate(algs):
    algorithm_path = algs_path[a]
    errors[algorithm] = numpy.ndarray((10,), numpy.float64)
    if algorithm_path in files:
      assert 'scores' in files[algorithm_path]
      for p, protocol in enumerate(folds_name):
        if protocol in files[algorithm_path]['scores']:
          e, h = measure.eer_hter(files[algorithm_path]['scores'][protocol]['nonorm']['scores-dev'], files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval'])
          # compute threshold on dev data
          dev_negatives, dev_positives = bob.measure.load.split_four_column(files[algorithm_path]['scores'][protocol]['nonorm']['scores-dev'])
          threshold = bob.measure.eer_threshold(dev_negatives, dev_positives)

          # compute FAR and FRR for eval data
          eval_negatives, eval_positives = bob.measure.load.split_four_column(files[algorithm_path]['scores'][protocol]['nonorm']['scores-eval'])

          far, frr = bob.measure.farfrr(eval_negatives, eval_positives, threshold)
          hter = (far + frr)/2.0
   
          errors[algorithm][p] = 100 * measure.lfw_classification_result(eval_negatives, eval_positives, threshold)

    # compute mean and std error
    means[algorithm] = numpy.mean(errors[algorithm])
    stds[algorithm] = numpy.std(errors[algorithm])

  # plot results with error bars
  figure = mpl.figure(figsize=(10,6))

  x = [1 + 2*x for x in range(len(algs)) ]
  y = [means[alg] for alg in algs]
  e = [stds[alg] for alg in algs]
  c = [measure.mycolor(alg) for alg in algs]
  mpl.bar(x, y, color=c, align='center', yerr=e, ecolor='k', capsize=5, error_kw={'lw':2, 'mew':2})

  mpl.xticks(x, [r'%2.1f\%%' % means[algorithm] for algorithm in algs], va='baseline')
  l = [mpl.bar([j],[0],color=c[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.08 + 0.05 * ((len(algs)-1) / 5 + 1))
  legend_handle = mpl.legend(l, algs, ncol=5, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  mpl.axis((0, max(x)+1, 0, 100))

  mpl.ylabel(r'Classification rate (\%)')
#      mpl.xlabel("Parameters")

  pdf.savefig(figure,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

  #v = ["fold%d"%i for i in range(1,11)]
  print("\\TableHeader{" + "} {".join(algs) + "}\n")
  for f, fold in enumerate(folds_name):
    print("\\TableContent{" + fold + "} {" + "} {".join(["%3.2f\\,\\%%" % errors[a][f] for a in algs]) + ("}\n" if fold != 'fold10' else "}\\hline\n"))
  print("\\TableContent{mean} {" + "} {".join(["%3.2f\\,\\%%" % means[a] for a in algs]) + "}\n")
  print("\\TableContent{std} {" + "} {".join(["%3.2f" % stds[a] for a in algs]) + "}\n")






def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-a', '--algorithms', default = ALGORITHMS, choices = ALGORITHMS, nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('-b', '--algorithms-path', default = DEFAULT_PATHS, nargs = '+', help = "Select the base dir of the corresponding algorithms for the first protocol")
  parser.add_argument('-o', '--output', default = 'lfw.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  algs = args.algorithms
  algs_path = args.algorithms_path

  database = 'lfw'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval'))

  plot_lfw(pdf, algs_path, algs, files, database)

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
