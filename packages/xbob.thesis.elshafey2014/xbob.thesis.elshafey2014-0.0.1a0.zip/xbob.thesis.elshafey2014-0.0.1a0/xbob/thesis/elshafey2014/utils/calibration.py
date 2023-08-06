#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Wed Jan  8 16:53:45 CET 2014
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bob
import numpy
import os

def train_llr(score_inputs):
  """Trains a Linear Logistic Regression Model"""
  # read data
  n_systems = len(score_inputs)
  for i in range(n_systems):
    if not os.path.isfile(score_inputs[i]): raise IOError("The score file '%s' does not exist" % score_inputs[i])
  # pythonic way: create inline dictionary "{...}", index with desired value "[...]", execute function "(...)"
  data = []
  for i in range(n_systems):
    data.append(bob.measure.load.split_four_column(score_inputs[i]))

  data_neg = numpy.vstack([data[k][0] for k in range(n_systems)]).T.copy()
  data_pos = numpy.vstack([data[k][1] for k in range(n_systems)]).T.copy()
  trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
  return trainer.train(data_neg, data_pos)


def fuse(machine, score_inputs, score_output):
  """Fuse scores using a Linear Logistic Regression Model"""
  n_systems = len(score_inputs)
  data = []
  for i in range(n_systems):
    if not os.path.isfile(score_inputs[i]): raise IOError("The score file '%s' does not exist" % score_inputs[i])
  for i in range(n_systems):
    data.append(bob.measure.load.four_column(score_inputs[i]))
  n_data = len(data[0])
  outf = open(score_output, 'w')
  for k in range(n_data):
    scores = numpy.array([[v[k][-1] for v in data]], dtype=numpy.float64)
    s_fused = machine.forward(scores)[0,0]
    line = " ".join(data[0][k][0:-1]) + " " + str(s_fused) + "\n"
    outf.write(line)

def score_list_to_matrix(data):
  """Converts a list of scores (m models and n test segments) as tuples
  into a m by n matrix """
  model_ids_ = list(set(e[0] for e in data))
  model_ids = {}
  for i, el in enumerate(model_ids_):
    model_ids[el] = i
  del model_ids_
  test_ids_ = list(set(e[2] for e in data))
  test_ids = {}
  for i, el in enumerate(test_ids_):
    test_ids[el] = i
  del test_ids_
  datam = numpy.ndarray(shape=(len(model_ids), len(test_ids)), dtype=numpy.float64)
  assert( len(data) == len(model_ids) * len(test_ids) )
  for e in data:
    i = model_ids[e[0]]
    j = test_ids[e[2]]
    datam[i,j] = e[3]
  return datam, model_ids, test_ids

def matrix_to_score_list(data, datam, model_ids, test_ids, output_file):
  """Saves a list of scores from a matrix of scores"""
  # create output file
  output = open(output_file, 'w')
  for e in data:
    # Get the score from the matrix
    i = model_ids[e[0]]
    j = test_ids[e[2]]
    # write the score to file, using the reference client id, probe id and probe name
    output.write("%s %s %s %f\n" % (e[0] , e[1], e[2], datam[i,j]))

def compound_llr(simple_llr, prior=None):
  """Converts simple log-likelihood ratios (LLRs) into compound LLRs .
  This is a python port of the matlab code provided here:
  https://sites.google.com/site/bosaristoolkit/sre12
  The code is as 'well' documented as in the original function...

  simple_llr
    A m by n matrix of (classic) simple LLRs, for m different target speakers
    and n test speech segments. The numerator hypothesis is that the test 
    segment is from the target speaker and the denominator that it is from a 
    completely unknown speaker. 

  prior
    A m or (m+1) vector of prior probabilities over speakers. Must sum to 1. 
    If component m+1 is present, it refers to the class of all unknown 
    speakers. The other m components refer to the speakers associated with 
    the m rows of simple_llr.
      - For SRE'12 'known' test condition, a reasonable value is: 
          prior = ones(1,m)/m
      - For SRE'12 'core/extended' test condition, a reasonable value is: 
          prior = [ones(1,m)/m,1]/2
      - For SRE'12 'unknown' test condition, it is:
          prior =  [zeros(1,m)/m,1]
        But in this case, compoundLLR = simpleLLR, so don't bother
        calling this code.
  """

  if not prior:
    m = simple_llr.shape[0]
    prior = numpy.ones(shape=(m+1,), dtype=numpy.float64)
    prior[0:m] = 1. / m
    prior /= 2.

  assert prior.shape[0] == simple_llr.shape[0] or prior.shape[0] == simple_llr.shape[0]+1

  log_prior =  numpy.maximum(-500*numpy.ones(prior.shape[0]), numpy.log(prior))
  N = simple_llr.shape[0]
  T = simple_llr.shape[1]
  if (prior.shape[0] == N+1):
    log_post = numpy.vstack((simple_llr, numpy.zeros((1,T))))
  else:
    log_post = simple_llr

  log_post += log_prior.reshape((log_prior.shape[0],1)) 

  # log sum exp2
  B = numpy.ones(shape=log_post.shape, dtype=numpy.float64)
  smax = numpy.max(log_post, axis=0)
  ii = numpy.argmax(log_post, axis=0)
  for it in range(ii.shape[0]):
    B[ii[it],it] = 0.
  rest = numpy.log1p(numpy.sum(numpy.exp(log_post - smax) * B, axis=0))
  del B
  del ii

  log_post -= smax
  del smax
  log_post -= rest
  del rest

  large = numpy.array(log_post > -1.)
  comp_llr = numpy.zeros(log_post.shape, numpy.float64)
  comp_llr = numpy.where(large, -numpy.log(numpy.expm1(-log_post)), log_post - numpy.log(1-numpy.exp(log_post)) )
  del large
  del log_post

  if (prior.shape[0] == N+1):
    prior = prior[0:N]
    log_prior = log_prior[0:N]
    comp_llr = comp_llr[0:N,:]

  comp_llr = comp_llr - log_prior.reshape((log_prior.shape[0],1)) + numpy.log1p( -prior.reshape((prior.shape[0],1)) )
  return comp_llr


def compound_llr_files(filename_simp, filename_comp):
  """Converts simple LLR into compound LLR from raw score files"""
    # read data
  if not os.path.isfile(filename_simp): raise IOError("The given score file does not exist")
  data = bob.measure.load.four_column(filename_simp)
  # Converts simple llr scores into a matrix of simple llr scores
  simple_llrs, model_ids, test_ids = score_list_to_matrix(data)
  # Compute compound llr
  compound_llrs = compound_llr(simple_llrs)
  # Save to output
  matrix_to_score_list(data, compound_llrs, model_ids, test_ids, filename_comp)


def nist_sre_dcf(negatives, positives, ptarget, normalize=False):
  """Decision cost function DCF (port from bosaris fast_actDCF)"""
  if (type(ptarget) != type(numpy.array([]))): ptarget = numpy.array(ptarget, dtype=numpy.float)
  
  plo = numpy.log(ptarget) - numpy.log(1-ptarget)
  t = positives.shape[0]
  n = negatives.shape[0]
  d = ptarget.shape[0]

  plos = numpy.hstack((-plo, positives))
  ii = numpy.argsort(plos)
  r = numpy.zeros(shape=(t+d,), dtype=numpy.int)
  r[ii] = range(0,t+d)
  pmiss = (numpy.array(r[0:d], dtype=numpy.float) - range(d-1,-1,-1))/ t

  plos = numpy.hstack((-plo, negatives))
  ii = numpy.argsort(plos)
  r = numpy.zeros(shape=(n+d,), dtype=numpy.int)
  r[ii] = range(0,n+d)
  pfa = (n - numpy.array(r[0:d], dtype=numpy.float) + range(d-1,-1,-1)) / n

  dcf = ptarget * pmiss + (1-ptarget) * pfa
  if normalize: dcf /= min(ptarget, 1-ptarget)

  return dcf, pmiss, pfa


def nist_sre12_cprimary(negatives, positives, normalize=True):
  """Cost function cprimary for NIST SRE12"""
  ptarget = numpy.array([0.001, 0.01])
  dcf, pmiss, pfa = nist_sre_dcf(negatives, positives, ptarget)
  cprimary = (ptarget * pmiss + (1-ptarget) * pfa) 
  if normalize: cprimary /= numpy.minimum(ptarget, 1-ptarget)
  return numpy.mean(cprimary)


