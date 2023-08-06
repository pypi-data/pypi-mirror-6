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

"""This script generates plots from the Multi-PIE experiments.
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
PROTOCOLS_E = ('E',)
PROTOCOLS_I = ('M', 'U', 'G')
PROTOCOLS_P = ('P',)
PROTOCOLS = PROTOCOLS_E + PROTOCOLS_I + PROTOCOLS_P
DEFAULT_PATHS_E = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u100', 'jfa_uv2', 'ivec400_cosine', 'ivec400_plda_fg60', 'sift_plda_fg60')
DEFAULT_PATHS_M = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u200', 'jfa_uv100', 'ivec400_cosine', 'ivec400_plda_fg60', 'sift_plda_fg60')
DEFAULT_PATHS_U = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u200', 'jfa_uv50', 'ivec400_cosine', 'ivec400_plda_fg60', 'sift_plda_fg60')
DEFAULT_PATHS_G = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u200', 'jfa_uv100', 'ivec400_cosine', 'ivec400_plda_fg60', 'sift_plda_fg60')
DEFAULT_PATHS_P = ('pca', 'lrpca', 'ldair', 'gmm', 'isv_u20', 'jfa_uv50', 'ivec400_cosine', 'ivec400_plda_fg50', 'sift_plda_fg60')


def plot_multipie_expression(pdf, algs_path, algs, files, database):

  figure = mpl.figure(figsize=(11,6))

  import xbob.db.multipie
  db = xbob.db.multipie.Database()
  EXPRESSIONS = ['all'] + [str(e.name) for e in db.expressions()]

  from xbob.db.multipie.models import File

  eer = numpy.ndarray((len(EXPRESSIONS), len(algs)), dtype = numpy.float)
  eer[:] = numpy.nan
  hter = numpy.ndarray((len(EXPRESSIONS), len(algs)), dtype = numpy.float)
  hter[:] = numpy.nan

  expression_translation = {}
  for a, algorithm in enumerate(algs):
    algorithm_path = algs_path[a]
    if algorithm_path in files:
      pos_dev, neg_dev = dict([(e, []) for e in EXPRESSIONS]), dict([(e, []) for e in EXPRESSIONS])
      pos_eval, neg_eval = dict([(e, []) for e in EXPRESSIONS]), dict([(e, []) for e in EXPRESSIONS])
      with open(files[algorithm_path]['scores']['E']['ztnorm']['scores-dev']) as score_file:
        print "reading score file", files[algorithm_path]['scores']['E']['ztnorm']['scores-dev']
        for line in score_file:
          splits = line.split()
          assert len(splits) == 4
          # get the image type
          file_id = splits[2]
          if file_id not in expression_translation:
            expression_translation[file_id] = db.reverse([splits[2]])[0].expression.name
          expression = expression_translation[file_id]
          # extract the score
          score = float(splits[3])
          if splits[0] == splits[1]:
            pos_dev[expression].append(score)
            pos_dev['all'].append(score)
          else:
            neg_dev[expression].append(score)
            neg_dev['all'].append(score)

      with open(files[algorithm_path]['scores']['E']['ztnorm']['scores-eval']) as score_file:
        print "reading score file", files[algorithm_path]['scores']['E']['ztnorm']['scores-eval']
        for line in score_file:
          splits = line.split()
          assert len(splits) == 4
          # get the image type
          file_id = splits[2]
          if file_id not in expression_translation:
            expression_translation[file_id] = db.reverse([splits[2]])[0].expression.name
          expression = expression_translation[file_id]
          # extract the score
          score = float(splits[3])
          if splits[0] == splits[1]:
            pos_eval[expression].append(score)
            pos_eval['all'].append(score)
          else:
            neg_eval[expression].append(score)
            neg_eval['all'].append(score)

      # compute HTER for all expression types
      for e, expression in enumerate(EXPRESSIONS):
        thres = bob.measure.eer_threshold(neg_dev[expression], pos_dev[expression])
        far, frr = bob.measure.farfrr(neg_dev[expression], pos_dev[expression], thres)
        eer[e,a] = (far+frr) * 50 # / 2 * 100%
        far, frr = bob.measure.farfrr(neg_eval[expression], pos_eval[expression], thres)
        hter[e,a] = (far+frr) * 50 # / 2 * 100%
        print(algorithm, expression, eer[e,a], hter[e,a])


  # create plots split into the different protocols
  colors = [measure.mycolor(algs[a]) for a in range(len(algs))]
  x = range((len(algs) * 2 + 2) * (len(EXPRESSIONS)+1))
  y = [0] * len(x)
  c = [(0,0,0,0)] * len(x)
  index = 1
  for e in range(len(EXPRESSIONS)):
    for a in range(len(algs)):
      y[index] = hter[e,a]
      c[index] = colors[a]
      index += 1
    index += 3

  mpl.bar(x, y, color=c, align='center' )
  mpl.axis((0, index-2, 0, max(y) * 1.02))
  ticks = [(len(algs))/2. + .5 + i * (len(algs) +3) for i in range(len(EXPRESSIONS))]
  mpl.xticks(ticks, EXPRESSIONS, va='baseline')

  # dirty HACK to generate legends
  l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.08 + 0.05 * ((len(algs)-1) / 5 + 1))
  legend_handle = mpl.legend(l, algs, ncol=5, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  #mpl.legend(l, algs, loc=9, ncol=4, prop={'size':16})
  mpl.ylabel(r'HTER (\%)')
  mpl.xlabel(r'Tested facial expressions')

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("")
  print("\\TableHeader{" + "} {".join(sorted(algs)) + "}")
  for e, expression in enumerate(EXPRESSIONS):
    print("\\TableContent{" + expression + "} {" + "} {".join(["%3.2f} {%3.2f" % (eer[e,a], hter[e,a]) for a in range(len(algs))]) + "}")
  print("")


def plot_multipie_illumination(pdf, protocols, protocols_algs_path, algs, files, database):
  
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

  mpl.bar(x, y, color=c, align='center' )
  mpl.axis((0, index-2, 0, numpy.nanmax(y) * 1.02))
  ticks = [(len(algs))/2. + .5 + i * (len(algs) +2) for i in range(len(protocols))]
  mpl.xticks(ticks, protocols, va='baseline')

  # dirty HACK to generate legends
  l = [mpl.bar([j],[0],color=colors[j]) for j in range(len(algs))]
  bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
  legend_handle = mpl.legend(l, algs, ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y))
  #mpl.legend(l, algs, loc=9, ncol=3, prop={'size':16})
  mpl.ylabel(r'HTER (\%)')
  mpl.xlabel(r'Illumination enrollment and testing conditions')

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("")
  print("\\TableHeader{" + "} {".join(sorted(algs)) + "}")
  for p, protocol in enumerate(protocols):
    print("\\TableContent{" + protocol + "} {" + "} {".join(["%3.2f} {%3.2f" % (eer[p,a], hter[p,a]) for a in range(len(algs))]) + ("}" if p < len(protocols)-1 else "}\\hline"))
  print("")



def plot_multipie_pose(pdf, algs_path, algs, P_files, database):

  def cam_for_angle(angle):
    # get protocol
    protocol = ANGLES[angle]
    # translate into camera
    camera = protocol[1:3] + '_' + protocol[3]
    return camera


  ANGLES= {
    +90 : 'P240',
    +75 : 'P010',
    +60 : 'P200',
    +45 : 'P190',
    +30 : 'P041',
    +15 : 'P050',
    + 0 : 'P051',
    -15 : 'P140',
    -30 : 'P130',
    -45 : 'P080',
    -60 : 'P090',
    -75 : 'P120',
    -90 : 'P110'
  }

  PROTOCOLS = ['P'] + [ANGLES[p] for p in sorted(ANGLES.keys())]
  
  figure = mpl.figure()

  x = sorted(ANGLES.keys())
  eer = {}
  hter = {}
  for a, algorithm in enumerate(algs):
    algorithm_path = algs_path[a]
    eer[algorithm] = {}
    hter[algorithm] = {}
    y = [numpy.nan] * len(x)
    # read the data for the P protocol, split up into the single cameras
    if 'P' in P_files[algorithm_path]['scores']:

      # read file and extract positives and negatives
      pos_dev, neg_dev = dict([(cam_for_angle(p), []) for p in ANGLES.keys()]), dict([(cam_for_angle(p), []) for p in ANGLES.keys()])
      pos_eval, neg_eval = dict([(cam_for_angle(p), []) for p in ANGLES.keys()]), dict([(cam_for_angle(p), []) for p in ANGLES.keys()])
      with open(P_files[algorithm_path]['scores']['P']['ztnorm']['scores-dev']) as score_file:
        for line in score_file:
          splits = line.split()
          assert len(splits) == 4
          # get the camera
          camera = splits[2].split('/')[4]
          # extract the score
          score = float(splits[3])
          if splits[0] == splits[1]:
            pos_dev[camera].append(score)
          else:
            neg_dev[camera].append(score)

      if 'scores-eval' in P_files[algorithm_path]['scores']['P']['ztnorm']:
       with open(P_files[algorithm_path]['scores']['P']['ztnorm']['scores-eval']) as score_file:
        for line in score_file:
          splits = line.split()
          assert len(splits) == 4
          # get the camera
          camera = splits[2].split('/')[4]
          # extract the score
          score = float(splits[3])
          if splits[0] == splits[1]:
            pos_eval[camera].append(score)
          else:
            neg_eval[camera].append(score)

    elif len(P_files) > 1: # P-files > 1 -> LRPCA or LDA-IR
      # only for LPRCA and LDA-IR: read score files according to sub-protocol
      # read file and extract positives and negatives
      pos_dev, neg_dev = dict([(cam_for_angle(p), []) for p in ANGLES.keys()]), dict([(cam_for_angle(p), []) for p in ANGLES.keys()])
      pos_eval, neg_eval = dict([(cam_for_angle(p), []) for p in ANGLES.keys()]), dict([(cam_for_angle(p), []) for p in ANGLES.keys()])
      for angle in ANGLES:
        if ANGLES[angle] in P_files[algorithm_path]['scores']:
          with open(P_files[algorithm_path]['scores'][ANGLES[angle]]['ztnorm']['scores-dev']) as score_file:
            for line in score_file:
              splits = line.split()
              assert len(splits) == 4
              # get the camera
              camera = splits[2].split('/')[4]
              assert camera == cam_for_angle(angle)
              # extract the score
              score = float(splits[3])
              if splits[0] == splits[1]:
                pos_dev[camera].append(score)
              else:
                neg_dev[camera].append(score)
          with open(P_files[algorithm_path]['scores'][ANGLES[angle]]['ztnorm']['scores-eval']) as score_file:
            for line in score_file:
              splits = line.split()
              assert len(splits) == 4
              # get the camera
              camera = splits[2].split('/')[4]
              assert camera == cam_for_angle(angle)
              # extract the score
              score = float(splits[3])
              if splits[0] == splits[1]:
                pos_eval[camera].append(score)
              else:
                neg_eval[camera].append(score)

    if P_files[algorithm_path]:
      for i, angle in enumerate(x):
        # compute HTER
        camera = cam_for_angle(angle)
        if len(neg_dev[camera]) and len(pos_dev[camera]) and len(neg_eval[camera]) and len(pos_eval[camera]):
          thres = bob.measure.eer_threshold(neg_dev[camera], pos_dev[camera])
          far, frr = bob.measure.farfrr(neg_dev[camera], pos_dev[camera], thres)
          eer[algorithm][angle] = "%3.2f\\,\\%%" % ((far+frr) * 50) # / 2 * 100 %
          far, frr = bob.measure.farfrr(neg_eval[camera], pos_eval[camera], thres)
          hter[algorithm][angle] = "%3.2f\\,\\%%" % ((far+frr) * 50) # / 2 * 100 %
          y[i] = (far+frr) * 50 # / 2 * 100 %
          print algorithm, angle, y[i]
        else:
          eer[algorithm][angle] = "n/a"
          hter[algorithm][angle] = "n/a"

    else:
      for angle in x:
        eer[algorithm][angle] = "n/a"
        hter[algorithm][angle] = "n/a"


    mpl.plot(x, y, measure.mymarker(algorithm), color = measure.mycolor(algorithm), lw=2, ms=10, mew=2)


  mpl.xticks(x, [r'%s$^\circ$'%a for a in x], va='baseline')
  mpl.axis((min(x)-10, max(x)+10, 0, 60))

  mpl.xlabel(r'Facial pose rotation angle in degree')
  mpl.ylabel(r'HTER (\%)')

  bbox_anchor_y = (1.10 + 0.05 * ((len(algs)-1) / 3 + 1))
  legend_handle = mpl.legend(algs, ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y), numpoints=1)
  #mpl.legend(algs, loc=9, ncol=3, prop={'size':16}, numpoints=1)
  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  print("")
  print("\\TableHeader{" + "} {".join(algs) + "}")
  for angle in x:
    print("\\TableContent{%+i} {"%angle + "} {".join(["%s} {%s" % (eer[a][angle], hter[a][angle]) for a in algs]) + "}")
  print("")


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
  parser.add_argument('-b', '--algorithms-path-e', default = DEFAULT_PATHS_E, nargs = '+', help = "Select the base dir of the corresponding algorithms for the expression protocol E")
  parser.add_argument('-c', '--algorithms-path-m', default = DEFAULT_PATHS_M, nargs = '+', help = "Select the base dir of the corresponding algorithms for the illumination protocol M")
  parser.add_argument('-d', '--algorithms-path-u', default = DEFAULT_PATHS_U, nargs = '+', help = "Select the base dir of the corresponding algorithms for the illumination protocol U")
  parser.add_argument('-e', '--algorithms-path-g', default = DEFAULT_PATHS_G, nargs = '+', help = "Select the base dir of the corresponding algorithms for the illumination protocol G")
  parser.add_argument('-f', '--algorithms-path-p', default = DEFAULT_PATHS_P, nargs = '+', help = "Select the base dir of the corresponding algorithms for the pose protocol")
  parser.add_argument('-o', '--output', default = 'multipie.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  protocols = args.protocols  
  algs = args.algorithms
  algs_path_e = args.algorithms_path_e
  algs_path_m = args.algorithms_path_m
  algs_path_u = args.algorithms_path_u
  algs_path_g = args.algorithms_path_g
  algs_path_p = args.algorithms_path_p

  database = 'multipie'
  files = measure.parse_results(os.path.join(args.results_directory, database), 4, ('scores-dev', 'scores-eval'))

  if 'E' in protocols:
    plot_multipie_expression(pdf, algs_path_e, algs, files, database)
  if all(p in protocols for p in PROTOCOLS_I):
    protocols_algs_path = {}
    protocols_algs_path['M'] = algs_path_m
    protocols_algs_path['U'] = algs_path_u
    protocols_algs_path['G'] = algs_path_g
    plot_multipie_illumination(pdf, PROTOCOLS_I, protocols_algs_path, algs, files, database)
  if 'P' in protocols:
    plot_multipie_pose(pdf, algs_path_p, algs, files, database)

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
