#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Tue Jan 8 13:36:12 CET 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
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

"""This script fuses scores from the MOBIO database in various ways."""

import bob
import os
import sys
import numpy

from ..utils import measure

import matplotlib
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_pdf import PdfPages
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=18)
matplotlib.rcParams['xtick.major.pad'] = 16 


DATABASES = ('mobio_face', 'mobio_speaker', 'mobio_fusion')
DEFAULT_PROTOCOLS = ('mobile1-female', 'mobile1-male')
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
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')
  parser.add_argument('-p', '--protocols', default = DEFAULT_PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, help = 'The base directory containing the results (score files).')
  parser.add_argument('-o', '--output', default = 'mobio_det.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the CMC curve."""
  args = parse_command_line(command_line_options)

  results_dir = args.results_directory
  databases = args.databases
  pdf = PdfPages(args.output)

  # Face systems
  norm = 'ztnorm'
  det_list = [1e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 4e-1, 5e-1]


  for db in databases:
    SYSTEM = SYSTEMS[db]
    for p in args.protocols:
      PATHS = [path for path in DEFAULT_PATHS[db][p]] 
      PATHS.append(LAST_PATHS[db])
      
      figure = mpl.figure()
      list_systems = []
      for a, alg in enumerate(PATHS):
        system = SYSTEM[a]
        list_systems.append(system)

        if a >= len(ALGORITHMS):
          filename_eval = os.path.join(results_dir, DATABASES[-1], alg, 'scores', p, norm, 'scores-eval')
        else:
          filename_eval = os.path.join(results_dir, db, alg, 'scores', p, norm, 'scores-eval')
        neg, pos = bob.measure.load.split_four_column(filename_eval)
        frr, far = bob.measure.det(neg, pos, 1000) # Bob 1.2.x returns this order (more recent version returns far, frr)

        algorithm = '' if a >= len(ALGORITHMS) else ALGORITHMS[a]
        marker = measure.mymarker('SIFT-PLDA') if not algorithm in ALGORITHMS else measure.mymarker(algorithm)
        markersize = 10
        color = measure.mycolor('SIFT-PLDA') if not algorithm in ALGORITHMS else measure.mycolor(algorithm)
        mpl.plot(far, frr, marker, color = color, lw=2, ms=10, mew=2, markevery=20)
        #lw=2, ms=10, mew=1, label=name, markevery=20
     
      ticks = [bob.measure.ppndf(d) for d in det_list]
      labels = [("%.5f" % (d*100)).rstrip('0').rstrip('.') for d in det_list]
      mpl.xticks(ticks, labels)
      mpl.yticks(ticks, labels)
      mpl.axis((ticks[0], ticks[-1], ticks[0], ticks[-1]))

      mpl.xlabel('False Acceptance Rate (\%)')
      mpl.ylabel('False Rejection Rate (\%)')
      mpl.grid(True, color=(0.3,0.3,0.3))
      bbox_anchor_y_2 = (1.08 + 0.05 * ((len(DEFAULT_PATHS[db][p])-1) / 3 + 1))
      legend_handle = mpl.legend(list_systems, ncol=3, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, bbox_anchor_y_2))
   
      pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25, bbox_extra_artists=[legend_handle])

  pdf.close()
  return 0

if __name__ == "__main__":
  main()
