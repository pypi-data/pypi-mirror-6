#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Tue Jan 8 13:36:12 CET 2013
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

"""This script computes the relative common erros on the MOBIO database."""

import bob
import os
import sys
import numpy

from .. import utils

DATABASES = ('mobio_face', 'mobio_speaker', 'mobio_fusion')
DEFAULT_PROTOCOLS = ('mobile1-male',)
PROTOCOLS = ('mobile1-female', 'mobile1-male', 'laptop1-female', 'laptop1-male', 'laptop_mobile1-female', 'laptop_mobile1-male')
NORMS = ('nonorm', 'ztnorm')

ALGORITHMS = ('GMM', 'ISV', 'JFA', 'TV-Cosine', 'TV-PLDA')
SYSTEMS = {}
SYSTEMS['mobio_face']    = ('F-GMM', 'F-ISV', 'F-JFA', 'F-TV-Cosine', 'F-TV-PLDA', 'F-ALL')
SYSTEMS['mobio_speaker'] = ('S-GMM', 'S-ISV', 'S-JFA', 'S-TV-Cosine', 'S-TV-PLDA', 'S-ALL')
SYSTEMS['mobio_fusion'] = ('B-GMM', 'B-ISV', 'B-JFA', 'B-TV-Cosine', 'B-TV-PLDA', 'B-ALL')

#COMBIS = (('GMM', 'ISV'), ('GMM', 'JFA'), ('GMM', 'TV-Cosine'), ('GMM', 'TV-PLDA'), ('ISV', 'GMM'), ('ISV', 'JFA'), ('ISV', 'TV-Cosine'), ('ISV', 'TV-PLDA'), ALGORITHMS)
COMBIS = (('ISV', 'GMM'), ('ISV', 'JFA'), ('ISV', 'TV-Cosine'), ('ISV', 'TV-PLDA'), ALGORITHMS)

DEFAULT_PATHS = {}

DEFAULT_PATHS['mobio_face'] = {}
DEFAULT_PATHS['mobio_face']['mobile1-female']           = ('gmm', 'isv_u200', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['mobile1-male']             = ('gmm', 'isv_u200', 'jfa_uv30', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_face']['laptop1-female']           = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['laptop1-male']             = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_face']['laptop_mobile1-female']    = ('gmm',  'isv_u50', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg40')
DEFAULT_PATHS['mobio_face']['laptop_mobile1-male']      = ('gmm', 'isv_u200', 'jfa_uv20', 'ivec400_cosine', 'ivec400_plda_fg50')

DEFAULT_PATHS['mobio_speaker'] = {}
DEFAULT_PATHS['mobio_speaker']['mobile1-female']        = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['mobile1-male']          = ('gmm',  'isv_u20',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop1-female']        = ('gmm',  'isv_u20',  'jfa_uv2', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop1-male']          = ('gmm',  'isv_u20',  'jfa_uv2', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop_mobile1-female'] = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')
DEFAULT_PATHS['mobio_speaker']['laptop_mobile1-male']   = ('gmm',  'isv_u50',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')

DEFAULT_PATHS['mobio_fusion'] = {}
DEFAULT_PATHS_FUSION = ('b-gmm', 'b-isv', 'b-jfa', 'b-tv-cosine', 'b-tv-plda')
DEFAULT_PATHS['mobio_fusion']['mobile1-female']        = DEFAULT_PATHS_FUSION
DEFAULT_PATHS['mobio_fusion']['mobile1-male']          = DEFAULT_PATHS_FUSION
DEFAULT_PATHS['mobio_fusion']['laptop1-female']        = DEFAULT_PATHS_FUSION
DEFAULT_PATHS['mobio_fusion']['laptop1-male']          = DEFAULT_PATHS_FUSION
DEFAULT_PATHS['mobio_fusion']['laptop_mobile1-female'] = DEFAULT_PATHS_FUSION
DEFAULT_PATHS['mobio_fusion']['laptop_mobile1-male']   = DEFAULT_PATHS_FUSION

LAST_PATHS = {}
LAST_PATHS['mobio_face']    = 'f-all'
LAST_PATHS['mobio_speaker'] = 's-all'
LAST_PATHS['mobio_fusion']  = 'b-all'


def count_common_errors_set(dict_systems, file_lines, thresholds):
  # On the set
  common_errors = 0
  total_errors = numpy.zeros(len(dict_systems))
  for k in range(len(file_lines[0])):
    false_rejected = 0
    false_acceptance = 0
    for n in range(len(dict_systems)):
      cid, rid, samp_id, score = file_lines[n][k]
      if cid == rid and score < thresholds[n]:
        false_rejected = false_rejected + 1
        total_errors[n] +=  1
      if cid != rid and score > thresholds[n]:
        false_acceptance = false_acceptance + 1
        total_errors[n] += 1
    if false_rejected == len(dict_systems) or false_acceptance == len(dict_systems) :
      common_errors = common_errors + 1
  relative_common_errors = common_errors / numpy.min(total_errors)
  return common_errors, total_errors, relative_common_errors*100


def count_common_errors(dict_systems):
  thresholds = numpy.zeros(len(dict_systems))
  dev_file_lines = {}
  eval_file_lines = {}
  n = 0
  for k in dict_systems.iterkeys():
    dev_file= dict_systems[k][0]
    #print "Dev:", dev_file
    eval_file= dict_systems[k][1]
    #print "Eval:", eval_file
    neg, pos = bob.measure.load.split_four_column(dev_file)
    thresholds[n] = bob.measure.eer_threshold(neg, pos)
    #print "threshold = ", thresholds[n]
    dev_file_lines[n] = bob.measure.load.four_column(dev_file)
    eval_file_lines[n] = bob.measure.load.four_column(eval_file)
    n = n+1

  common_errors_dev, total_errors_dev, rce_dev = count_common_errors_set(dict_systems, dev_file_lines, thresholds)
  common_errors_eval, total_errors_eval, rce_eval = count_common_errors_set(dict_systems, eval_file_lines, thresholds)

  return common_errors_dev, total_errors_dev, rce_dev, common_errors_eval, total_errors_eval, rce_eval

def fuse_scores(machine, score_files):
  """Fuses the selected score files with the given machine and writes the results to the given file."""
  # read all score files; these score files need to have the scores in the same order.
  score_file_lines = [bob.measure.load.four_column(f) for f in score_files]

  # get the first score file as reference
  first = score_file_lines[0]
  score_count = len(first)

  neg = []
  pos = []
  # iterate over the client/probe pairs
  for i in range(score_count):
    # get the raw scores of all systems for this specific client/probe pair
    raw_scores = [float(line[i][-1]) for line in score_file_lines]
    # fuse these scores into one value by using the given machine
    fused_score = machine(raw_scores)
    if first[i][0] == first[i][1]:
      pos.append(fused_score[0])
    else:
      neg.append(fused_score[0])
  return numpy.array(neg), numpy.array(pos)

def train_llr(filenames_dev):
  """Trains a LLR fusion machine from data from development scores"""

  # Load Dev data
  data_dev = []
  for f_dev in filenames_dev:
    data_dev.append(bob.measure.load.split_four_column(f_dev))

  # Train LLR
  data_neg = numpy.vstack([data_dev[k][0] for k in range(len(data_dev))]).T.copy()
  data_pos = numpy.vstack([data_dev[k][1] for k in range(len(data_dev))]).T.copy()
  trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
  machine = trainer.train(data_neg, data_pos)
  return machine




def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = DEFAULT_PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, help = 'The base directory containing the results (score files).')

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  results_dir = args.results_directory
  databases = args.databases

  norm = 'ztnorm'
  for db in databases:
    SYSTEM = SYSTEMS[db]
    print("MODALITY: %s" % db)
    for p in args.protocols:
      print("PROTOCOL: %s" % p)
      for c in COMBIS:
        PATHS = DEFAULT_PATHS[db][p]
        dict_systems = {}
        # Common errors
        n = 0
        for a, alg in enumerate(PATHS):
          system = SYSTEM[a]
          filename_dev = os.path.join(results_dir, db, alg, 'scores', p, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, db, alg, 'scores', p, norm, 'scores-eval')
          if ALGORITHMS[a] in c:
            dict_systems[system] = [filename_dev, filename_eval]

        print(c)
        print(count_common_errors(dict_systems))

        # Fusion (HTER)
        filenames_dev = []
        filenames_eval = []
        for a, alg in enumerate(PATHS):
          system = SYSTEM[a]
          if ALGORITHMS[a] in c:
            filenames_dev.append(os.path.join(results_dir, db, alg, 'scores', p, norm, 'scores-dev'))
            filenames_eval.append(os.path.join(results_dir, db, alg, 'scores', p, norm, 'scores-eval'))
        # Train LLR machine
        machine = train_llr(filenames_dev)
        # Fuse scores
        neg_dev, pos_dev = fuse_scores(machine, filenames_dev)
        neg_eval, pos_eval = fuse_scores(machine, filenames_eval)
        # EER/HTER
        thres = bob.measure.eer_threshold(neg_dev, pos_dev)
        far, frr = bob.measure.farfrr(neg_dev, pos_dev, thres)
        eer = 100*(far+frr) / 2.
        far, frr = bob.measure.farfrr(neg_eval, pos_eval, thres)
        hter = 100*(far+frr) / 2.
        print("EER=%f -- HTER=%f\n" % (eer, hter))
      print("")
    print("")

  return 0

if __name__ == "__main__":
  main()
