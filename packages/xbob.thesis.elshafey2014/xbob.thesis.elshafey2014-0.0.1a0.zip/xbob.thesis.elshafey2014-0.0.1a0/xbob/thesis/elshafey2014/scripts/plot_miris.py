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

"""This script generates plots from the M-iris toy example
"""

import numpy
import bob
import os
import sys

from ..utils import miris

from matplotlib.backends.backend_pdf import PdfPages

ALGORITHMS = ('Dataset', 'ML', 'MAP', 'ISV', 'JFA', 'TV', 'PLDA')


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-a', '--algorithms', default = ALGORITHMS, choices = ALGORITHMS, nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('-o', '--output', default = 'miris.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots on the M-iris dataset."""
  args = parse_command_line(command_line_options)

  algs = args.algorithms

  # Plot
  pdf = PdfPages(args.output)
  if 'Dataset' in algs: miris.plot_miris(pdf)
  if 'ML' in algs: miris.plot_miris_ml(pdf)
  if 'MAP' in algs: miris.plot_miris_map(pdf)
  if 'ISV' in algs: miris.plot_miris_isv(pdf)
  if 'JFA' in algs: miris.plot_miris_jfa(pdf)
  if 'TV' in algs: miris.plot_miris_tv(pdf)
  if 'PLDA' in algs: miris.plot_miris_plda(pdf)
  pdf.close()

  return 0

if __name__ == "__main__":
  main()
