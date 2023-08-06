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

import numpy, numpy.random
import bob

import matplotlib
import matplotlib.pyplot as mpl
# Enable latex in legends/captions
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
# increase the default font size
matplotlib.rc('font', size=16)
matplotlib.rcParams['xtick.major.pad'] = 16 


TRAINING_CLASSES = ('Mersicolor', 'Mseudacorus', 'Mirginica')
ENROLLMENT_CLASS = 'Metosa'
CLASSES = TRAINING_CLASSES + (ENROLLMENT_CLASS,) # 'Mibirica'

CLIST = ('g', 'k', 'r', 'b') # #FFFF00: yellow
COLORS = {}
for ci, cl in enumerate(CLASSES):
  COLORS[cl] = CLIST[ci]
COLORS['comp'] = ('c', 'm')
COLORS['compline'] = ('c', 'm')
COLORS['test'] = '#FF6600' # orange

MARKERS = {}
for cl in CLASSES:
  MARKERS[cl] = 'o'
MARKERS['initmean'] = 's'
MARKERS['ubmmean'] = 'D'
MARKERS['gmmmean'] = 'd'
MARKERS['gmmmean2'] = 'x'
MARKERS['test'] = 'v'
MARKERS['compline'] = '+'

MARKERSIZES = {}
MARKER_BIGSIZE = 10
MARKERSIZES['initmean'] = MARKER_BIGSIZE
MARKERSIZES['ubmmean'] = MARKER_BIGSIZE
MARKERSIZES['gmmmean'] = MARKER_BIGSIZE
MARKERSIZES['gmmmean2'] = MARKER_BIGSIZE
MARKERSIZES['test'] = MARKER_BIGSIZE
MARKERSIZES['compline'] = 5

LINESTYLES = {}
for cl in CLASSES:
  LINESTYLES[cl] = 'None'
LINESTYLES['comp'] = 'None'
LINESTYLES['compline'] = '-'

DATASET_SEED = 3


def rand_in_ellipse(n, a=2, b=1, offset_ang=1, offset_x=0, offset_y=0):
  res = numpy.ndarray(shape=(n,2), dtype=numpy.float64)
  cos_ang = numpy.cos(offset_ang)
  sin_ang = numpy.sin(offset_ang)
  for k in range(n):
    angle = 2*numpy.pi*numpy.random.random_sample()
    r1 = numpy.random.random_sample()
    r2 = numpy.random.random_sample()
    res[k,0] = offset_x + a * r1 * numpy.cos(angle) * cos_ang - b * r1 *  numpy.sin(angle) * sin_ang
    res[k,1] = offset_y + a * r2 * numpy.cos(angle) * sin_ang + b * r2 *  numpy.sin(angle) * cos_ang
  return res 


def miris():
  numpy.random.seed(DATASET_SEED)
  data = {}
  data['Metosa'] = rand_in_ellipse(50, 1, 0.2, 2, 0, 0)
  data['Mersicolor'] = rand_in_ellipse(50, 1, 0.2, 2, 1, 1)
  data['Mseudacorus'] = rand_in_ellipse(50, 1, 0.2, 2, 1.5, 1.5)
  data['Mirginica'] = rand_in_ellipse(50, 1, 0.2, 2, 2, 2)
  return data


def _plot_miris_content(data, title, list_classes):
  """Plots data from the M-iris dataset in the current figure."""
  mpl.title(title)
  mpl.xlabel(r'x_1')
  mpl.ylabel(r'x_2')
  mpl.axis([-1,3,-1,3])
  for cl in list_classes:
    mpl.plot(data[cl][:,0], data[cl][:,1], marker=MARKERS[cl], color=COLORS[cl], linestyle=LINESTYLES[cl])


def plot_miris(pdf):
  """Plots the whole M-iris dataset and saves it into the pdf"""
  data = miris()
  figure = mpl.figure()
  _plot_miris_content(data, 'Miris dataset', CLASSES)
  mpl.legend(CLASSES, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def _ubm_training_init():
  """Initializes a UBM GMM with predefined means and a ML trainer"""
  ubm = bob.machine.GMMMachine(2,2)
  ubm.means = numpy.array([[0.5,0.5],[2.5,2.5]]) # Initial means
  ml_trainer = bob.trainer.ML_GMMTrainer(True, True, True, 1e-6)
  ml_trainer.ml_trainer = 1e-10
  ml_trainer.max_iterations = 10
  return (ubm, ml_trainer)

def _plot_mean(mean_x, mean_y, plot_style, ind):
  mpl.plot(mean_x, mean_y, marker=MARKERS[plot_style], color=COLORS['comp'][ind], linestyle=LINESTYLES['comp'], markersize=MARKERSIZES[plot_style])

def _plot_means(ubm, plot_style):
  for ind in range(0,2):
    _plot_mean(ubm.means[ind,0], ubm.means[ind,1], plot_style, ind)

def _plot_line(px, py, ind):
  mpl.plot(px, py, marker=MARKERS['compline'], color=COLORS['compline'][ind], linestyle=LINESTYLES['compline'], markersize=MARKERSIZES['compline'], linewidth=1)

def _plot_arrow(sx, sy, lx, ly, text, ox=0., oy=0., color='k'):
  mpl.arrow(sx, sy, lx, ly, fc=color, ec=color, head_width=0.05, head_length=0.1, zorder=1000 )
  mpl.text(sx+lx+ox, sy+ly+oy, text, fontsize=15)


def plot_miris_ml(pdf):
  """Plots the ML training applied to the M-iris dataset and saves it into the pdf"""
  data = miris()
  # Initialize ML training
  ubm, ml_trainer = _ubm_training_init()
  # Initialize figure
  figure = mpl.figure()
  # Plot training data
  _plot_miris_content(data, 'GMM Training (ML) (GMM with 2 Gaussians)', TRAINING_CLASSES)
  # Training data
  training_data = numpy.vstack([data[cl] for cl in TRAINING_CLASSES])
  # Initial means
  ml_trainer.initialize(ubm, training_data)
  _plot_means(ubm, 'initmean')
  # Loop and plot means
  old_means = ubm.means
  for k in range(10):
    ml_trainer.e_step(ubm, training_data)
    ml_trainer.m_step(ubm, training_data)
    if k % 1 == 0:
      for ind in range(0,2):
        px = numpy.array([old_means[ind,0], ubm.means[ind,0]])
        py = numpy.array([old_means[ind,1], ubm.means[ind,1]])
        _plot_line(px, py, ind)
      old_means = ubm.means
  ml_trainer.finalize(ubm, training_data)
  # Plot legend
  lg = TRAINING_CLASSES + ('Initial mean 1', 'Initial mean 2', 'UBM mean 1', 'UBM mean 2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def _train_ubm(data):
  """Trains a UBM GMM with predefined means"""
  ubm, ml_trainer = _ubm_training_init()
  training_data = numpy.vstack([data[cl] for cl in TRAINING_CLASSES])
  ml_trainer.train(ubm, training_data)
  return ubm

def plot_miris_map(pdf):
  """Plots the MAP adaptation applied to the M-iris dataset and saves into the pdf"""
  data = miris()

  ubm = _train_ubm(data)
  gmm = bob.machine.GMMMachine(2,2)

  # MAP 1
  relevance_factor = 2
  map_trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, False, False, 1e-6)
  map_trainer.set_prior_gmm(ubm)
  map_trainer.train(gmm, data['Metosa'].copy())

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'MAP on Metosa', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot GMM Means
  _plot_means(gmm, 'gmmmean')
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', 'GMM mean 1', 'GMM mean 2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)

  # MAP 2
  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'MAP on Metosa - Impact of the relevance factor', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  old_means = ubm.means.copy()
  k = 0
  for relevance_factor in [1 * l for l in range(1,16)]:
    map_trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, False, False, 1e-6)
    map_trainer.set_prior_gmm(ubm)
    if k != 0:
      old_means = gmm.means.copy()
    map_trainer.train(gmm, data[ENROLLMENT_CLASS].copy())
    if k != 0:
      for ind in range(0,2):
        px = numpy.array([old_means[ind,0], gmm.means[ind,0]])
        py = numpy.array([old_means[ind,1], gmm.means[ind,1]])
        _plot_line(px, py, ind)
    else:
      _plot_means(gmm, 'gmmmean')
    k += 1
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2',  r'GMM mean 1 ($\tau = 1$)', r'GMM mean 2 ($\tau=1$)', 'GMM mean 1', 'GMM mean 2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)

  # MAP 3
  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'MAP on Metosa - Impact of the number of adaptation samples', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  old_means = ubm.means.copy()
  relevance_factor = 2.
  map_trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, False, False, 1e-6)
  map_trainer.set_prior_gmm(ubm)
  k = 0
  for n_samples in range(5,51,5): #range(10,51,10):
    if k != 0:
      old_means = gmm.means.copy()
    map_trainer.train(gmm, data['Metosa'][0:n_samples,:].copy())
    if k != 0:
      for ind in range(0,2):
        px = numpy.array([old_means[ind,0], gmm.means[ind,0]])
        py = numpy.array([old_means[ind,1], gmm.means[ind,1]])
        _plot_line(px, py, ind)
    else:
      _plot_means(gmm, 'gmmmean')
    k += 1
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', r'GMM mean 1 ($n_s = 5$)', r'GMM mean 2 ($n_s = 5$)', 'GMM mean 1', 'GMM mean 2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def plot_miris_isv(pdf):
  """Plots ISV applied to the M-iris dataset and saves into the pdf"""
  data = miris()

  ubm = _train_ubm(data)
  gmm = bob.machine.GMMMachine(2,2)
  
  isvbase = bob.machine.ISVBase(ubm, 1)
  isvtrainer = bob.trainer.ISVTrainer(100, 1.) 
 

  # 1/ ISV Training
  isv_training_data = []
  for c in TRAINING_CLASSES:
    data_c = data[c]
    samples_c = []
    g = 5
    for k in range(data_c.shape[0]/g):
      gs = bob.machine.GMMStats(2,2)
      sample = data_c[g*k:g*(k+1),:].copy()
      ubm.acc_statistics(sample, gs) 
      samples_c.append(gs)
    isv_training_data.append(samples_c)

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'ISV Training (GMM with 2 Gaussians)', TRAINING_CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Train ISV
  isvtrainer.train(isvbase, isv_training_data)
  u0 = isvbase.u[0:2,0] #/ numpy.linalg.norm(isvbase.u[0:2,0])
  u1 = isvbase.u[2:4,0] #/ numpy.linalg.norm(isvbase.u[2:4,0])
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  # Plot legend
  lg = TRAINING_CLASSES + ('UBM mean 1', 'UBM mean 2', 'U_1', 'U_2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


  # 2/ ISV Enrollment
  isvmachine = bob.machine.ISVMachine(isvbase)
  isv_enrol_data = []
  data_c = data[ENROLLMENT_CLASS]
  g = 5
  for k in range(data_c.shape[0]/g):
    gs = bob.machine.GMMStats(2,2)
    sample = data_c[g*k:g*(k+1),:].copy()
    ubm.acc_statistics(sample, gs)
    isv_enrol_data.append(gs)
  # Enroll ISV
  isvtrainer.enrol(isvmachine, isv_enrol_data, 1)
  v_metosa = ubm.means.reshape(4,) + isvbase.d * isvmachine.z

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'ISV Enrollment (GMM with 2 Gaussians)', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  for ind in range(0,2):
    _plot_mean(v_metosa[2*ind], v_metosa[2*ind+1], 'gmmmean', ind)
  # Plot legend
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', 'ISV mean 1', 'ISV mean 2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


  # 3/ ISV Probing
  sample = numpy.array([0.5,-0.75])
  gs = bob.machine.GMMStats(2,2)
  ubm.acc_statistics(sample, gs)
  ux = numpy.zeros((4,), numpy.float64)
  isvmachine.estimate_ux(gs, ux)

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'ISV Test (GMM with 2 Gaussians)', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  for ind in range(0,2):
    _plot_mean(v_metosa[2*ind], v_metosa[2*ind+1], 'gmmmean', ind)
  # Plot test
  mpl.plot(sample[0], sample[1], marker=MARKERS['test'], color=COLORS['test'], linestyle=LINESTYLES['comp'], markersize=MARKERSIZES['test'])
  _plot_arrow(v_metosa[0], v_metosa[1], ux[0], ux[1], '', color=COLORS['test'])
  _plot_arrow(v_metosa[2], v_metosa[3], ux[2], ux[3], '', color=COLORS['test'])
  # Plot legend
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', 'ISV mean 1', 'ISV mean 2', 'test sample')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def plot_miris_jfa(pdf):
  """Plots JFA applied to the M-iris dataset and saves into the pdf"""
  data = miris()

  ubm = _train_ubm(data)
  gmm = bob.machine.GMMMachine(2,2)
  
  jfabase = bob.machine.JFABase(ubm, 1, 1)
  jfatrainer = bob.trainer.JFATrainer(100) 
  
  # 1/ JFA Training
  jfa_training_data = []
  for c in TRAINING_CLASSES:
    data_c = data[c]
    samples_c = []
    g = 5
    for k in range(data_c.shape[0]/g):
      gs = bob.machine.GMMStats(2,2)
      sample = data_c[g*k:g*(k+1),:].copy()
      ubm.acc_statistics(sample, gs) 
      samples_c.append(gs)
    jfa_training_data.append(samples_c)

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'JFA Training (GMM with 2 Gaussians)', TRAINING_CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Train JFA
  jfatrainer.train(jfabase, jfa_training_data)
  u0 = jfabase.u[0:2,0] #/ numpy.linalg.norm(jfabase.u[0:2,0])
  u1 = jfabase.u[2:4,0] #/ numpy.linalg.norm(jfabase.u[2:4,0])
  v0 = jfabase.v[0:2,0] #/ numpy.linalg.norm(jfabase.v[0:2,0])
  v1 = jfabase.v[2:4,0] #/ numpy.linalg.norm(jfabase.v[2:4,0])
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], v0[0], v0[1], r'$\mathbf{V}_1$', ox=0., oy=0.1)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], v1[0], v1[1], r'$\mathbf{V}_2$', ox=0., oy=0.1)
  # Plot legend
  lg = TRAINING_CLASSES + ('UBM mean 1', 'UBM mean 2', 'U_1', 'U_2', 'V_1', 'V_2')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


  # 2/ JFA Enrollment
  figure = mpl.figure()
  jfamachine = bob.machine.JFAMachine(jfabase)
  jfa_enrol_data = []
  data_c = data['Metosa']
  g = 5
  for k in range(data_c.shape[0]/g):
    gs = bob.machine.GMMStats(2,2)
    sample = data_c[g*k:g*(k+1),:].copy()
    ubm.acc_statistics(sample, gs)
    jfa_enrol_data.append(gs)
  # Enroll JFA
  jfatrainer.enrol(jfamachine, jfa_enrol_data, 10)
  v_metosa = ubm.means.reshape(4,) + jfabase.v.reshape(4,) * jfamachine.y + jfabase.d * jfamachine.z 
  v_metosa2 = ubm.means.reshape(4,) + jfabase.v.reshape(4,) * jfamachine.y 

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'JFA Enrollment (GMM with 2 Gaussians)', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], v0[0], v0[1], r'$\mathbf{V}_1$', ox=0., oy=0.1)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], v1[0], v1[1], r'$\mathbf{V}_2$', ox=0., oy=0.1)
  # Plot metosa
  for ind in range(0,2):
    _plot_mean(v_metosa[2*ind], v_metosa[2*ind+1], 'gmmmean', ind)
    _plot_mean(v_metosa2[2*ind], v_metosa2[2*ind+1], 'gmmmean2', ind)
  # Plot legend
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', 'JFA mean 1', 'JFA mean 2',  r'JFA ($\mathbf{m}+\mathbf{V_1}\mathbf{y}$)', r'JFA ($\mathbf{m}+\mathbf{V_2}\mathbf{y}$)')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


  # 3/ JFA Probing
  sample = numpy.array([0.5,-0.75])
  gs = bob.machine.GMMStats(2,2)
  ubm.acc_statistics(sample, gs)
  ux = numpy.zeros((4,), numpy.float64)
  jfamachine.estimate_ux(gs, ux)

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'JFA Test (GMM with 2 Gaussians)', CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], u0[0], u0[1], r'$\mathbf{U}_1$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], u1[0], u1[1], r'$\mathbf{U}_2$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], v0[0], v0[1], r'$\mathbf{V}_1$', ox=0., oy=0.1)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], v1[0], v1[1], r'$\mathbf{V}_2$', ox=0., oy=0.1)
  # JFA Test
  for ind in range(0,2):
    _plot_mean(v_metosa[2*ind], v_metosa[2*ind+1], 'gmmmean', ind)
  mpl.plot(sample[0], sample[1], marker=MARKERS['test'], color=COLORS['test'], linestyle=LINESTYLES['comp'], markersize=MARKERSIZES['test'])
  _plot_arrow(v_metosa[0], v_metosa[1], ux[0], ux[1], '', color=COLORS['test'])
  _plot_arrow(v_metosa[2], v_metosa[3], ux[2], ux[3], '', color=COLORS['test'])
  # Plot legend
  lg = CLASSES + ('UBM mean 1', 'UBM mean 2', 'JFA mean 1', 'JFA mean 2', 'test sample')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def plot_miris_tv(pdf):
  ### Maximum Likelihood
  data = miris()

  ubm = _train_ubm(data)
  gmm = bob.machine.GMMMachine(2,2)
  
  ivecmachine = bob.machine.IVectorMachine(ubm, 2)
  ivectrainer = bob.trainer.IVectorTrainer(True, 0.001, 100)
  
  # TV Training
  ivec_training_data = []
  for c in TRAINING_CLASSES:
    data_c = data[c]
    g = 5
    for k in range(data_c.shape[0]/g):
      gs = bob.machine.GMMStats(2,2)
      sample = data_c[g*k:g*(k+1),:].copy()
      ubm.acc_statistics(sample, gs) 
      ivec_training_data.append(gs)

  ivectrainer.train(ivecmachine, ivec_training_data)
  t0 = ivecmachine.t[0:2,0] #/ numpy.linalg.norm(isvbase.u[0:2,0])
  t1 = ivecmachine.t[2:4,0] #/ numpy.linalg.norm(isvbase.u[2:4,0])
  t2 = ivecmachine.t[0:2,1] #/ numpy.linalg.norm(isvbase.u[0:2,0])
  t3 = ivecmachine.t[2:4,1] #/ numpy.linalg.norm(isvbase.u[0:2,0])

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'TV Training (GMM with 2 Gaussians)', TRAINING_CLASSES)
  # Plot UBM Means
  _plot_means(ubm, 'ubmmean')
  # Plot arrows
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], t0[0], t0[1], r'$\mathbf{T}_{1a}$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], t1[0], t1[1], r'$\mathbf{T}_{2a}$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[0,0], ubm.means[0,1], t2[0], t2[1], r'$\mathbf{T}_{1b}$', ox=0., oy=-0.3)
  _plot_arrow(ubm.means[1,0], ubm.means[1,1], t3[0], t3[1], r'$\mathbf{T}_{2b}$', ox=0.1, oy=0.)
  # Plot legend
  lg = TRAINING_CLASSES + ('UBM mean 1', 'UBM mean 2', r'T_1a', r'T_2a', r'T_1b', r'T_2b')
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)


def plot_miris_plda(pdf):
  """Plots PLDA training applied to the M-iris dataset and saves into the pdf"""
  data = miris()

  # Initialize PLDA
  pldabase = bob.machine.PLDABase(2, 1, 1)
  pldatrainer = bob.trainer.PLDATrainer(100)

  # Train PLDA
  plda_training_data = []
  for c in TRAINING_CLASSES:
    plda_training_data.append(data[c])
  pldatrainer.train(pldabase, plda_training_data)
  f0 = pldabase.f[0:2,0] / numpy.linalg.norm(pldabase.f[0:2,0])
  g0 = pldabase.g[0:2,0] / numpy.linalg.norm(pldabase.g[0:2,0])

  figure = mpl.figure()
  # Plot data
  _plot_miris_content(data, 'PLDA Training', TRAINING_CLASSES)
  # Plot mean
  _plot_mean(pldabase.mu[0], pldabase.mu[1], 'ubmmean', 0)
  # Plot arrows
  _plot_arrow(pldabase.mu[0], pldabase.mu[1], f0[0], f0[1], r'$\mathbf{F}_1$', 0.1, 0.)
  _plot_arrow(pldabase.mu[0], pldabase.mu[1], g0[0], g0[1], r'$\mathbf{G}_1$', 0., -0.3)
  # Plot legend
  lg = TRAINING_CLASSES + (r'PLDA mean $\mathbf{\mu}$',)
  mpl.legend(lg, loc=2, prop={'size': 12}, numpoints=1)
  pdf.savefig(figure)
 
