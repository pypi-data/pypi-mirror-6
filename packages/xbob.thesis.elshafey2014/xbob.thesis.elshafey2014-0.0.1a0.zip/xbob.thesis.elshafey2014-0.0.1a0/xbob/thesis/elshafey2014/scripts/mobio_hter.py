#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Mon Jan 13 22:36:35 CET 2014
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

"""This script computes the HTER on MOBIO
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
matplotlib.rc('font', size=10)
matplotlib.rcParams['xtick.major.pad'] = 16 

DATABASES = ('mobio_speaker', 'mobio_face', 'mobio_fusion')
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

SPATHS = {}
SPATHS['GMM'] = ('gmm',)
SPATHS['ISV'] = ('isv_u2', 'isv_u5', 'isv_u10', 'isv_u20', 'isv_u50', 'isv_u100', 'isv_u200')
SPATHS['JFA'] = ('jfa_uv2', 'jfa_uv5', 'jfa_uv10', 'jfa_uv20', 'jfa_uv30', 'jfa_uv40', 'jfa_uv50')
SPATHS['TV-Cosine'] = ('ivec400_cosine',)
SPATHS['TV-PLDA'] = ('ivec400_plda_fg2', 'ivec400_plda_fg5', 'ivec400_plda_fg10', 'ivec400_plda_fg20', 'ivec400_plda_fg30', 'ivec400_plda_fg40', 'ivec400_plda_fg50')


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, nargs = '+', help = "Select one (or more) databases that you want to consider (choices among the two supported ones)")
  parser.add_argument('-p', '--protocols', default = PROTOCOLS, choices = PROTOCOLS, nargs = '+', help = "Select one (or more) protocols that you want to consider (choices among the three supported ones)")
  parser.add_argument('-r', '--results-directory', required = True, help = 'The base directory containing the results (score files).')

  args = parser.parse_args(command_line_options)

  return args
 

def main(command_line_options = None):
  """Computes and plots the distribution."""
  args = parse_command_line(command_line_options)

  results_dir = args.results_directory
  databases = args.databases
  protocols = args.protocols
  eer_d = {}
  hter_d = {}
  for p in protocols:
    eer_d[p] = {}
    hter_d[p] = {}
    for db_m in databases:
      eer_d[p][db_m] = {}
      hter_d[p][db_m] = {}
      for s in SYSTEMS[db_m]:
        eer_d[p][db_m][s] = None
        hter_d[p][db_m][s] = None
      
  for db_m in databases:
    SYSTEM = SYSTEMS[db_m]
    norm = 'ztnorm'

    for p, prot in enumerate(args.protocols):
      PATHS = [path for path in DEFAULT_PATHS[db_m][prot]]
      PATHS.append(LAST_PATHS[db_m])

      eer_s = []
      hter_s = []
      list_systems = []
      for a, algo in enumerate(SYSTEM):
        system = SYSTEM[a]
        list_systems.append(system)

        if a >= len(ALGORITHMS):
          alg = PATHS[a]
          filename_dev = os.path.join(results_dir, DATABASES[-1], alg, 'scores', prot, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, DATABASES[-1], alg, 'scores', prot, norm, 'scores-eval')
        else:
          min_eer = None
          min_path = None
          if db_m != DATABASES[-1]:
            for path in SPATHS[ALGORITHMS[a]]:
              filename_dev = os.path.join(results_dir, db_m, path, 'scores', prot, norm, 'scores-dev')
              filename_eval = os.path.join(results_dir, db_m, path, 'scores', prot, norm, 'scores-eval')
              eer, hter = measure.eer_hter(filename_dev, filename_eval)
              if min_eer == None or min_eer > eer:
                min_eer = eer
                min_path = path
          alg = PATHS[a]
          filename_dev = os.path.join(results_dir, db_m, alg, 'scores', prot, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, db_m, alg, 'scores', prot, norm, 'scores-eval')

        eer, hter = measure.eer_hter(filename_dev, filename_eval)
        eer_d[prot][db_m][system] = eer*100
        hter_d[prot][db_m][system] = hter*100
        eer_s.append(eer*100)
        hter_s.append(hter*100)

  for p in protocols:
    print(p)
    for db_m in databases:
      print("  " + db_m)
      for s in SYSTEMS[db_m]:
        print("    %s %.2f %.2f" % (s, eer_d[p][db_m][s], hter_d[p][db_m][s]))
 

  return 0

if __name__ == "__main__":
  main()
