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

"""This script generates histograms of speech duration on MOBIO and NIST SRE12
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

DATABASES = ('mobio_speaker', 'nist_sre12')


def compute_speech_duration(probes, directory):
  """Computes the duration of each probe sample"""
  duration = []
  for p in probes:
    # assumes that features were extracted every 10ms -> Division by 100 to get seconds
    duration.append(numpy.sum(bob.io.load(p.make_path(directory = directory, extension = '.hdf5'))) / float(100))
  average = sum(duration) / float(len(duration))
  return duration, average
 

def plot_speech_duration(pdf, duration):
  """Plots the distribution of durations"""
  figure = mpl.figure()
  mpl.hist(duration, bins=100, color='g')
  mpl.xlabel('Duration (in seconds)')
  mpl.ylabel('Number of audio samples')
  pdf.savefig(figure, bbox_inches='tight', pad_inches=0.25)


def parse_command_line(command_line_options):
  """Parse the program options"""

  usage = 'usage: %s [arguments]' % os.path.basename(sys.argv[0])

  import argparse
  parser = argparse.ArgumentParser(usage=usage, description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # This option is not normally shown to the user...
  parser.add_argument('--self-test', action = 'store_true', help = argparse.SUPPRESS)
  parser.add_argument('-d', '--databases', default = DATABASES, choices = DATABASES, nargs = '+', help = "Select one (or more) databases that you want to consider (choices among the two supported ones)")
  parser.add_argument('-t', '--temp-directory', required = True, help = 'The base directory containing the \'temporary\' data (features).')
  parser.add_argument('-o', '--output', default = 'mobio_speech_duration_probes.pdf', help = "The file to contain the plot")

  args = parser.parse_args(command_line_options)

  return args


def main(command_line_options = None):
  """Computes and plots the distribution."""
  args = parse_command_line(command_line_options)

  # plot the results
  pdf = PdfPages(args.output)

  databases = args.databases
  if 'mobio_speaker' in databases:
    import xbob.db.mobio
    directory = os.path.join(args.temp_directory, 'mobio_speaker', 'mfcc', 'preprocessed')
    db = xbob.db.mobio.Database()
    probes = db.objects(purposes='probe')
    duration, average = compute_speech_duration(probes, directory)
    plot_speech_duration(pdf, duration)
    print("Average duration of the samples on MOBIO: %.2f seconds" % average)

  if 'nist_sre12' in databases:
    import xbob.db.nist_sre12
    directory = os.path.join(args.temp_directory, 'nist_sre12', 'mfcc', 'preprocessed')
    db = xbob.db.nist_sre12.Database()
    probes = db.objects(purposes='probe', groups='eval')
    duration, average = compute_speech_duration(probes, directory)
    plot_speech_duration(pdf, duration)
    print("Average duration of the samples on NIST SRE12: %.2f seconds" % average)
   
  pdf.close()
  return 0

if __name__ == "__main__":
  main()
