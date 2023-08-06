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

"""This script generates histograms of speech duration
"""

import bob
import numpy
import os
import sys

from ..utils import measure

import matplotlib
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=18)
matplotlib.rcParams['xtick.major.pad'] = 14

DATABASES = ('mobio_speaker', 'mobio_face', 'mobio_fusion')
DEFAULT_PROTOCOLS = ('mobile1-male', 'laptop1-male', 'laptop_mobile1-male')
PROTOCOLS = ('mobile1-female', 'mobile1-male', 'laptop1-female', 'laptop1-male', 'laptop_mobile1-female', 'laptop_mobile1-male')
NORMS = ('nonorm', 'ztnorm')

ALGORITHMS = ('GMM', 'ISV', 'JFA', 'TV-Cosine', 'TV-PLDA')
SYSTEMS = {}
SYSTEMS['mobio_face']    = ('F-GMM', 'F-ISV', 'F-JFA', 'F-TV-Cosine', 'F-TV-PLDA', 'F-ALL')
SYSTEMS['mobio_speaker'] = ('S-GMM', 'S-ISV', 'S-JFA', 'S-TV-Cosine', 'S-TV-PLDA', 'S-ALL')
SYSTEMS['mobio_fusion'] = ('B-GMM', 'B-ISV', 'B-JFA', 'B-TV-Cosine', 'B-TV-PLDA', 'B-ALL')

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


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, nargs = '+', help = "Select one (or more) databases that you want to consider (choices among the two supported ones)")
  parser.add_argument('-p', '--protocols', default = DEFAULT_PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-o', '--output', default = 'mobio_hter.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args
 

def main(command_line_options = None):
  """Computes and plots the distribution."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)
  
  results_dir = args.results_directory
  databases = args.databases

  hter_all = {}
  list_systems_all = {}
  mycolors = ['r','g','b', 'c', 'm', 'y']
  for p, prot in enumerate(args.protocols):

    eer_s = []
    hter_s = []
    list_systems_s = []

    for db_m in databases:
      SYSTEM = SYSTEMS[db_m]
      norm = 'ztnorm'

      PATHS = [path for path in DEFAULT_PATHS[db_m][prot]]
      PATHS.append(LAST_PATHS[db_m])

      for a, algo in enumerate(SYSTEM):
        alg = PATHS[a]
        system = SYSTEM[a]
        list_systems_s.append(system)

        if a >= len(ALGORITHMS):
          filename_dev = os.path.join(results_dir, DATABASES[-1], alg, 'scores', prot, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, DATABASES[-1], alg, 'scores', prot, norm, 'scores-eval')
        else:
          filename_dev = os.path.join(results_dir, db_m, alg, 'scores', prot, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, db_m, alg, 'scores', prot, norm, 'scores-eval')

        eer, hter = measure.eer_hter(filename_dev, filename_eval)
        eer_s.append(eer*100)
        hter_s.append(hter*100)

    hter_all[prot] = hter_s
    list_systems_all[prot] = list_systems_s


  figure = mpl.figure(figsize=(15,6))

  pos_x_labels = []
  #ind = numpy.arange(18)   # the x locations for the groups
  ind = []
  v = 0
  for i in range(3):
    for j in range(6):
      ind.append(7*i + j)
  ind = numpy.array(ind)
  width = 0.2      # the width of the bars: can also be len(x) sequence
  pos = 0

  for p, prot in enumerate(args.protocols):
    color = mycolors[p]
    hter_p = hter_all[prot]
    pos_full = mpl.bar(ind+pos, hter_p, width=width, color=color)
    pos += width
    pos_x_labels.append(pos_full[0])

  list_systems_p = list_systems_all[prot]
  figure.autofmt_xdate()
  mpl.ylabel('HTER (\%)')
  mpl.xticks(ind+2*width, list_systems_p)
  mpl.xlim([-0.5,20.5])
  mpl.yticks(numpy.arange(0,25,2.5))

  protocols = [p.replace('_', '-') for p in args.protocols]
  legend_handle = mpl.legend(pos_x_labels, protocols, prop={'size':16})
  mpl.grid(True, color=(0.3,0.3,0.3))

  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
