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

"""This script generates HTER plot on MOBIO wrt. speech duration
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
matplotlib.rcParams['xtick.major.pad'] = 16 

DATABASES = ('mobio_speaker',)
DEFAULT_PROTOCOLS = ('mobile1-male',)
PROTOCOLS = ('mobile1-female', 'mobile1-male', 'laptop1-female', 'laptop1-male', 'laptop_mobile1-female', 'laptop_mobile1-male')
NORMS = ('nonorm', 'ztnorm')

ALGORITHMS = ('GMM', 'ISV', 'JFA', 'TV-Cosine', 'TV-PLDA')
SYSTEMS = {}
SYSTEMS['mobio_face']    = ('F-GMM', 'F-ISV', 'F-JFA', 'F-TV-Cosine', 'F-TV-PLDA', 'F-ALL')
SYSTEMS['mobio_speaker'] = ('S-GMM', 'S-ISV', 'S-JFA', 'S-TV-Cosine', 'S-TV-PLDA', 'S-ALL')
SYSTEMS['mobio_fusion'] = ('B-GMM', 'B-ISV', 'B-JFA', 'B-TV-Cosine', 'B-TV-PLDA', 'B-ALL')

DEFAULT_PATHS = {}

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


def get_speech_duration(probes, directory):
  """Computes the duration of each probe sample"""
  duration = {}
  for p in probes:
    # assumes that features were extracted every 10ms -> Division by 100 to get seconds
    duration[p.path] = numpy.sum(bob.io.load(p.make_path(directory = directory, extension = '.hdf5'))) / float(100)
    #duration[p.path] = bob.io.load(p.make_path(directory = directory, extension = '.hdf5')).shape[0] / float(100)
  return duration
 
def get_split_id(duration, d_split):
  split_id = len(d_split)+1
  for i in range(len(d_split)):
    if duration < d_split[i]:
      split_id = i + 1
      break
  return split_id

def parse_scores(filename, duration, d_split):
  f = bob.measure.load.four_column(filename)
  impostors = []
  real_accesses = []
  for i in range(len(d_split)+2):
    impostors.append([])
    real_accesses.append([])
  for l in f:
    score = float(l[3])
    split_id = get_split_id(duration[l[2]], d_split)
    if l[0] == l[1]:
      real_accesses[0].append(score)
      real_accesses[split_id].append(score) 
    else:
      impostors[0].append(score)
      impostors[split_id].append(score) 
  impostors = [numpy.array(e) for e in impostors]
  real_accesses = [numpy.array(e) for e in real_accesses] 
  return impostors, real_accesses

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
  parser.add_argument('-t', '--temp-directory', required = True, help = 'The base directory containing the \'temporary\' data (features).')
  parser.add_argument('-o', '--output', default = 'mobio_hter_by_duration.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args
 

def main(command_line_options = None):
  """Computes and plots the distribution."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)
  
  results_dir = args.results_directory
  databases = args.databases

  if 'mobio_speaker' in databases:
    features_directory = os.path.join(args.temp_directory, 'mobio_speaker', 'mfcc', 'preprocessed')
    import xbob.db.mobio
    db = xbob.db.mobio.Database()
    probes = db.objects(purposes='probe')
    duration = get_speech_duration(probes, features_directory)

    db_s = 'mobio_speaker'
    db_f = 'mobio_fusion'
    SYSTEM = SYSTEMS[db_s]
    norm = 'ztnorm'
    d_split = [4, 8]
    percent = False
    percent_split = []
    for p in args.protocols:
      PATHS = [path for path in DEFAULT_PATHS[db_s][p]]
      PATHS.append(LAST_PATHS[db_s])
      
      figure = mpl.figure()
      list_systems = []
      hter = []
      pos_x_labels = []
      ind = numpy.arange(4)    # the x locations for the groups
      ind[0] = -1
      width = 0.1       # the width of the bars: can also be len(x) sequence
      pos = -3*width/2
      for a, alg in enumerate(PATHS):
        system = SYSTEM[a]
        list_systems.append(system)

        if a >= len(ALGORITHMS):
          filename_dev = os.path.join(results_dir, db_f, alg, 'scores', p, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, db_f, alg, 'scores', p, norm, 'scores-eval')
        else:
          filename_dev = os.path.join(results_dir, db_s, alg, 'scores', p, norm, 'scores-dev')
          filename_eval = os.path.join(results_dir, db_s, alg, 'scores', p, norm, 'scores-eval')

        dev_impostors, dev_real_accesses = parse_scores(filename_dev, duration, d_split)
        eval_impostors, eval_real_accesses = parse_scores(filename_eval, duration, d_split)

        if not percent:
          N_all = eval_impostors[0].shape[0] + eval_real_accesses[0].shape[0] 
          for i in range(1, len(eval_impostors)):
            percent_split.append((eval_impostors[i].shape[0] + eval_real_accesses[i].shape[0]) / float(N_all))
          percent = True

        thres =  bob.measure.eer_threshold(dev_impostors[0], dev_real_accesses[0])
        hter_s = []
        for i in range(len(d_split)+2):
          far, frr = bob.measure.farfrr(eval_impostors[i], eval_real_accesses[i], thres)
          hter_s.append((far+frr) / 2. * 100)
        hter.append(hter_s)

        algorithm = '' if a >= len(ALGORITHMS) else ALGORITHMS[a]
        color = measure.mycolor('SIFT-PLDA') if not algorithm in ALGORITHMS else measure.mycolor(algorithm)
        pos_full = mpl.bar(ind+pos, hter_s, width, color=color)
        pos += width
        pos_x_labels.append(pos_full[0])

      mpl.ylabel('HTER (\%)')
      mpl.xticks(ind+width/2., ('All segments', '[0s-4s]', '[4s-8s]', '[8s-60s]') )
      mpl.yticks(numpy.arange(0,25,2.5))
      mpl.legend(pos_x_labels, list_systems, prop={'size':14})
      mpl.grid(True, color=(0.3,0.3,0.3))

      pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25)

    print percent_split


  pdf.close()
  return 0

if __name__ == "__main__":
  main()
