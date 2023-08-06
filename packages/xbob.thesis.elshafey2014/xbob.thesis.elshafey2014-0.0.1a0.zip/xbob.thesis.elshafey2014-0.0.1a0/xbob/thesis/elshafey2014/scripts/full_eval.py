#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Wed Jan  8 19:18:46 CET 2014
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

"""This script evaluates a system (returning several measures),
from score files in four or five column format.
"""

import bob
import os
import sys
import numpy

from .. import utils

def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-d', '--score-development', required = True, help = 'The development score file in 4 or 5 column format.')
  parser.add_argument('-t', '--score-evaluation', required = True, help = 'The evaluation score file in 4 or 5 column format.')

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  # read data
  if not os.path.isfile(args.score_development): raise IOError("The given development score file does not exist")
  dev_neg, dev_pos = bob.measure.load.split_four_column(args.score_development)
  if not os.path.isfile(args.score_development): raise IOError("The given evaluation score file does not exist")
  eval_neg, eval_pos = bob.measure.load.split_four_column(args.score_evaluation)

  # compute a threshold based on the EER on the development set
  threshold = bob.measure.eer_threshold(dev_neg, dev_pos)
  # compute the EER on the development set
  far, frr = bob.measure.farfrr(dev_neg, dev_pos, threshold)
  eer = (far + frr) / 2.
  eer_rocch =  bob.measure.eer_rocch(dev_neg, dev_pos)
  # compute the HTER on the evaluation set
  far, frr = bob.measure.farfrr(eval_neg, eval_pos, threshold)
  hter = (far + frr) / 2.
  # compute the cllr and min cllr
  cllr_dev = bob.measure.calibration.cllr(dev_neg, dev_pos) 
  cllr_eval = bob.measure.calibration.cllr(eval_neg, eval_pos) 
  min_cllr_dev = bob.measure.calibration.min_cllr(dev_neg, dev_pos) 
  min_cllr_eval = bob.measure.calibration.min_cllr(eval_neg, eval_pos)
  # compute cprimary
  cprimary_dev = utils.nist_sre12_cprimary(dev_neg, dev_pos)
  cprimary_eval = utils.nist_sre12_cprimary(eval_neg, eval_pos)

  print("EER threshold computed on the development set:\t %f" % threshold)
  print("EER           on the development set:\t %f" % eer)
  print("EER (using ROCCH) on development set:\t %f" % eer_rocch)
  print("HTER          on the evaluation set: \t %f" % hter)
  print("Cllr          on the development set:\t %f" % cllr_dev)
  print("Cllr          on the evaluation set: \t %f" % cllr_eval)
  print("minCllr       on the development set:\t %f" % min_cllr_dev)
  print("minCllr       on the evaluation set: \t %f" % min_cllr_eval)
  print("Cprimary      on the development set:\t %f" % cprimary_dev)
  print("Cprimary      on the evaluation set: \t %f" % cprimary_eval)

  return 0

if __name__ == "__main__":
  main()
