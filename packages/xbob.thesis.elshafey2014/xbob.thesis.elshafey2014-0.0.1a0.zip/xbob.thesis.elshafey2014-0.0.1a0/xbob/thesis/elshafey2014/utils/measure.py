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

import bob
import os
import numpy
import matplotlib.pyplot as mpl


COLOR_MAP = {
  'PCA' : (1, 1, 0.2), # 255,255,51
  'LRPCA' : (0.6, 0.6, 0.6), # 153,153,153
  'LDA-IR' : (0.969, 0.506, 0.749), # 247,129,191
  'GMM' : (0.302, 0.686, 0.29), # 77,175,74
  'ISV' : (0.216, 0.494, 0.722), #  55,126,184
  'JFA' : (0.651, 0.337, 0.157), # 166,86,40
  'TV-Cosine' : (0.894, 0.102, 0.11), # 228,26,28
  'TV-PLDA' :  (0.596, 0.306, 0.639), # 152,78,163
  'SIFT-PLDA' : (1, 0.498, 0), # 255,127,0
}

MARKER_MAP = {
  'PCA' : 'x',
  'LRPCA' : '+',
  'LDA-IR' : '^',
  'GMM' : 'v',
  'ISV' : 'o',
  'JFA' : 'h',
  'TV-Cosine' : 'd',
  'TV-PLDA' : 's',
  'SIFT-PLDA' : 'p'
}


def mycolors(count):
  return [cmap(i) for i in numpy.linspace(0, 1.0, count+1)]
markers = ('-d', '-o', '-x', '-s', '-*', '-h', '-^', '-v')

def mymarker(algo):
  return '-' + MARKER_MAP[algo]

def mycolor(algo):
  return COLOR_MAP[algo]

def myfar_list(density=4, lowest_power=-4):
  """Creates and returns a regular FAR list with 'density' steps between two powers of 10, and starting at 10 ^'lowest_power' (must be negative)."""
  return [10.**(x/float(density)) for x in range(lowest_power*density,1)]

def roc(score_file, density=4, lowest_power=-4):
  """Computes the Receiver Operating Characteristics (ROC) for the given score file."""
  neg, pos = bob.measure.load.split_four_column(score_file)
  return bob.measure.roc_for_far(neg, pos, myfar_list(density, lowest_power))[1]

def mydet_list():
  return [1e-5, 1e-3, 1e-2, 1e-1, 5e-1, 1-1e-1, 1-1e-2, 1-1e-3, 1-1e-5]

def det(score_file, points = 20):
  """Computes Detection Error Tradeoff (DET) curves for the given score file."""
  neg, pos = bob.measure.load.split_four_column(score_file)
  det = bob.measure.det(neg, pos, points)
  return (det[0], det[1])


def plot_roc_det(pdf, protocols, protocols_algs_path, algs, files, database):
    
  colors = [mycolor(a) for a in algs]

  # plot ROC and DET curves
  far_list = myfar_list()
  det_list = mydet_list()

  algs = algs + ('baseline',) if database == 'frgc' else algs
  for p in protocols_algs_path:
    protocols_algs_path[p] = protocols_algs_path[p] + ('baseline',) if database == 'frgc' else protocols_algs_path[p]
  
  rocs = [[None for a in range(len(algs))] for p in range(len(protocols_algs_path))]
  dets = [[None for a in range(len(algs))] for p in range(len(protocols_algs_path))]

  # Note: indices are: algorithm, 'scores', protocol, 'nonorm', 'scores-dev'
  for p, protocol in enumerate(protocols):
    algs_path = protocols_algs_path[protocol]
    for a, algorithm in enumerate(algs):
      algorithm_path = algs_path[a]
      if algorithm_path in files:
        assert 'scores' in files[algorithm_path]
        if protocol in files[algorithm_path]['scores']:
          # read score file
          neg, pos = bob.measure.load.split_four_column(files[algorithm_path]['scores'][protocol]['nonorm']['scores-dev'])
          roc = bob.measure.roc_for_far(neg, pos, far_list)[1]
          rocs[p][a] = [r*100 for r in roc]
          frr, far = bob.measure.det(neg, pos, 20) # Bob 1.2.x returns this order (more recent version returns far, frr)
          dets[p][a] = (far, frr)

  if database == 'frgc':
    # add baseline results
    for p, protocol in enumerate(protocols):
      rocs[p][-1] = {'2.0.1' : 66., '2.0.2': 88., '2.0.4': 12.}[protocol]

  for p, protocol in enumerate(protocols):
    # plot ROC
    figure = mpl.figure()
    algs_path = protocols_algs_path[protocol]
    for a, algorithm in enumerate(algs):
      marker = 's' if algorithm == 'baseline' else mymarker(algorithm)
      markersize = 18 if algorithm == 'baseline' else 10
      color = 'k' if algorithm == 'baseline' else mycolor(algorithm)
      X = 0.001 if algorithm == 'baseline' else far_list
      if rocs[p][a] is not None:
        mpl.semilogx(X, rocs[p][a], marker, color = color, lw=2, ms=markersize, mew=2)
      else:
        # create fake plot to get the legends right
        mpl.semilogx(X, [-1. for f in far_list], marker, color = color, lw=2, ms=markersize, mew=2)

    # generate legend
    if 'frgc': NN = 4
    else: NN = 3
    bbox_anchor_y = (1.11 + 0.05 * ((len(algs)-1) / NN + 1))
    legend_handle = mpl.legend(algs, ncol=NN, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y), numpoints=1)
    mpl.axis((far_list[0], 1, 0, 100))
    mpl.xticks([far_list[i] for i in range(0,len(far_list)+1,4)], [("%.4f" % (far_list[i]*100)).rstrip('0').rstrip('.') + "\%" for i in range(0,len(far_list)+1,4)], va='baseline')
    mpl.yticks(range(0, 101, 20), ["%d\%%" % d for d in range(0, 101, 20)])

    mpl.xlabel(r'False Acceptance Rate (\%)')
    mpl.ylabel(r'Correct Acceptance Rate (\%)')

    pdf.savefig(figure,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

    # plot DET
    figure = mpl.figure()
    for a, algorithm in enumerate(algs):
      marker = 's' if algorithm == 'baseline' else mymarker(algorithm)
      markersize = 18 if algorithm == 'baseline' else 10
      color = 'k' if algorithm == 'baseline' else mycolor(algorithm)
      if dets[p][a] is not None:
        mpl.plot(dets[p][a][0], dets[p][a][1], marker, color = color, lw=2, ms=10, mew=2)
      else:
        # create fake plot to get the legends right
        mpl.plot(det_list, [-1. for f in det_list], marker, color = color, lw=2, ms=10, mew=2)

    # generate legend
    if 'frgc': NN = 4
    else: NN = 3
    bbox_anchor_y = (1.11 + 0.05 * ((len(algs)-1) / NN + 1))
    legend_handle = mpl.legend(algs, ncol=NN, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y), numpoints=1)
    ticks = [bob.measure.ppndf(d) for d in det_list]
    labels = [("%.5f" % (d*100)) .rstrip('0').rstrip('.') + "\%" for d in det_list]
    mpl.xticks(ticks, labels, va='baseline')
    mpl.yticks(ticks, labels)
    mpl.axis((ticks[1], ticks[-3], ticks[0], ticks[-2]))  

    mpl.xlabel(r'False Acceptance Rate (\%)')
    mpl.ylabel(r'False Rejection Rate (\%)')

    pdf.savefig(figure,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("This tables report the CAR at FAR = 0.1% on " + database + "\n")
  print("\\TableHeader{" + "} {".join(algs) + "}\\n")
  for p, protocol in enumerate(protocols):
    if rocs[p][0]:
      print("\\TableContent{" + protocol + "} {" + "} {".join(["%3.2f" % (rocs[p][a][4] if isinstance(rocs[p][a], list) else rocs[p][a]) for a in range(len(algs))]) + "}\\n")


def eer_hter(dev_file, eval_file):
  """Computes the Equal Error Rate using the given score file"""
  # read score file
  neg, pos = bob.measure.load.split_four_column(dev_file)
  # compute EER on dev
  thres = bob.measure.eer_threshold(neg, pos)
  far, frr = bob.measure.farfrr(neg, pos, thres)

  eer = (far+frr) / 2.

  # read other score file
  neg, pos = bob.measure.load.split_four_column(eval_file)
  # compute EER on dev
  far, frr = bob.measure.farfrr(neg, pos, thres)

  hter = (far+frr) / 2.

  return (eer, hter)


def eer(score_file):
  """Computes the Equal Error Rate using the given score file"""
  # read score file
  neg, pos = bob.measure.load.split_four_column(score_file)
  # compute EER
  thres = bob.measure.eer_threshold(neg, pos)
  far, frr = bob.measure.farfrr(neg, pos, thres)

  return (far+frr) / 2.


def rr(score_file):
  """Computes the recognition rate for the given score file."""
  # read source file
  cmc_scores = bob.measure.load.cmc_four_column(score_file)
  # compute recognition rate
  return bob.measure.recognition_rate(cmc_scores)



def lfw_classification_result(negatives, positives, threshold):
  return (
      bob.measure.correctly_classified_negatives(negatives, threshold).sum(dtype=numpy.float64) +
      bob.measure.correctly_classified_positives(positives, threshold).sum(dtype=numpy.float64)
    ) / float(len(positives) + len(negatives))



def parse_results(directory, depth, score_files = ('scores-dev',)):
  if not os.path.exists(directory):
    return {}
  # collect all result files; sorted by algorithm
  if depth > 0:
    # recurse into all sub-directories
    subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory,d))]
    results = {}
    for subdir in subdirs:
      sub_result = parse_results(os.path.join(directory, subdir), depth-1, score_files)
      if len(sub_result):
        results[subdir] = sub_result
    return results
  else:
    # find all files that have the requested file name; should only be one!
    res = {}
    for root, dirs, files in os.walk(directory):
      for score_file in score_files:
        if score_file in files:
          #print("Found result file %s" % os.path.join(root, score_file))
          res[os.path.basename(score_file)] = os.path.join(root, score_file)
    return res


