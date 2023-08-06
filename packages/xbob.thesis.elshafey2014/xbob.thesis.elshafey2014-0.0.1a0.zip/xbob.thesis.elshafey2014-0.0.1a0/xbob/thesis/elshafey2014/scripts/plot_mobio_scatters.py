#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Mon Jan 13 22:36:35 CET 2014
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

"""This script generates scatters on MOBIO
"""

import bob
import numpy
import os
import sys

import matplotlib
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=18)
matplotlib.rcParams['xtick.major.pad'] = 16 

DATABASES = ('mobio_speaker',)
DEFAULT_PROTOCOLS = ('mobile1-male',)
PROTOCOLS = ('mobile1-female', 'mobile1-male', 'laptop1-female', 'laptop1-male', 'laptop_mobile1-female', 'laptop_mobile1-male')

ALGORITHMS = ('GMM', 'ISV', 'JFA', 'TV-Cosine', 'TV-PLDA')
COMBIS = (('ISV', 'GMM'), ('ISV', 'JFA'), ('ISV', 'TV-Cosine'), ('ISV', 'TV-PLDA'))
DEFAULT_PATHS = {}
DEFAULT_PATHS['mobio_speaker'] = {}
DEFAULT_PATHS['mobio_speaker']['mobile1-male']          = ('gmm',  'isv_u20',  'jfa_uv5', 'ivec400_cosine', 'ivec400_plda_fg50')


def plot_mobio_scatters(pdf, impostors, real_accesses, xlabel = 'x scores', ylabel = 'y scores'):
  """Plots the distribution of durations"""
  figure = mpl.figure()
  # because of the large number of samples, we plot only each 10th sample (or 5th or so...)
  imp_range = range(0, impostors.shape[0], 10)
  racc_range = range(0, real_accesses.shape[0], 10)

  mpl.plot(impostors[imp_range,0], impostors[imp_range,1], 'rs', label = 'impostors', alpha = 0.5)
  mpl.plot(real_accesses[racc_range,0], real_accesses[racc_range,1], 'g^', label = 'real accesses') # alpha = 0.2
  mpl.xlabel(xlabel)
  mpl.ylabel(ylabel)
  legend_handle = mpl.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, prop={'size':12}, mode="expand", ncol=4)
  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

def parse_scores(filename):
  f = bob.measure.load.four_column(filename)
  impostors = {}
  real_accesses = {}
  for l in f:
    identifier = l[0] + ' ' + l[2]
    if l[0] == l[1]:
      real_accesses[identifier] = float(l[3])
    else:
      impostors[identifier] = float(l[3])
  rea = [real_accesses[k] for k in sorted(real_accesses.iterkeys())]
  imp = [impostors[k] for k in sorted(impostors.iterkeys())]
  return numpy.array(rea), numpy.array(imp)

def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = DEFAULT_PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, nargs = '+', help = "Select one (or more) databases that you want to consider (choices among the two supported ones)")
  parser.add_argument('-o', '--output', default = 'mobio_scatters.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args
 

def main(command_line_options = None):
  """Computes and plots the distribution."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  databases = args.databases
  protocols = args.protocols
  results_dir = args.results_directory

  norm = 'ztnorm'
  if 'mobio_speaker' in databases:
    for protocol in protocols:
      paths = DEFAULT_PATHS['mobio_speaker'][protocol]
      for comb in COMBIS:
        filenames = []
        for c in comb:
          a = ALGORITHMS.index(c)
          alg_dir = paths[a]
          filenames.append(os.path.join(results_dir, 'mobio_speaker', alg_dir, 'scores', protocol, norm, 'scores-eval'))
        racc = []
        imp = []
        for f in filenames:
          racc_, imp_ = parse_scores(f)
          racc.append(racc_)
          imp.append(imp_)
        imp = numpy.vstack(imp).transpose(1,0)
        racc = numpy.vstack(racc).transpose(1,0)
        plot_mobio_scatters(pdf, imp, racc, comb[0] + ' scores', comb[1] + ' scores')

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
