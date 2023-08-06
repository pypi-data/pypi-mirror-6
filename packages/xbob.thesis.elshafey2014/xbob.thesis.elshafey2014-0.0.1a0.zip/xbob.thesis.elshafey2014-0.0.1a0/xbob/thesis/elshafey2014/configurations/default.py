#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sat Nov 23 16:51:32 CET 2013
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


import facereclib
import facerec2010
import xfacereclib.CSU.PythonFaceEvaluation
import pyvision
import scipy.spatial

from .. import tools as mytools

BEST_IMAGE_RESOLUTION = (80, 64)
BEST_EYE_POSITIONS = {'reye': (16, 15), 'leye' : (16, 48)}
BEST_LEFT_PROFILE_EYE_POSITIONS =  {'eye' : (16, 25), 'mouth': (52, 25)}
BEST_RIGHT_PROFILE_EYE_POSITIONS = {'eye' : (16, 38), 'mouth': (52, 38)}


# Preprocessing:
tan_triggs_preprocessor = facereclib.preprocessing.TanTriggs(
    # face cropping parameters
    cropped_image_size = BEST_IMAGE_RESOLUTION,
    cropped_positions = BEST_EYE_POSITIONS
    # Tan&Triggs parameters are the default ones
)

left_tan_triggs_preprocessor = facereclib.preprocessing.TanTriggs(
    # face cropping parameters
    cropped_image_size = BEST_IMAGE_RESOLUTION,
    cropped_positions = BEST_LEFT_PROFILE_EYE_POSITIONS
    # Tan&Triggs parameters are the default ones
)

right_tan_triggs_preprocessor = facereclib.preprocessing.TanTriggs(
    # face cropping parameters
    cropped_image_size = BEST_IMAGE_RESOLUTION,
    cropped_positions = BEST_RIGHT_PROFILE_EYE_POSITIONS
    # Tan&Triggs parameters are the default ones
)

# Cropping
K_CROPPED_IMAGE_HEIGHT = 200
K_CROPPED_IMAGE_WIDTH  = 200

# eye positions for frontal images
K_RIGHT_EYE_POS = (49, 74)
K_LEFT_EYE_POS  = (49,124)

# eye and mouth position for profile images
# (only appropriate for left profile images; change them for right profiles)
K_EYE_POS = (16, 20)
K_MOUTH_POS = (52, 20)

K_MOUTH_L = 0.891206278045033
K_EYE_NOSE_Y = 0.668364812848271
K_OUTER_EYE_D = 1.479967422
K_INNER_EYE_D = 0.51218784
K_EYE_MOUTH_Y = 0.9956389228141739

# define the preprocessor
keypoint_preprocessor = facereclib.preprocessing.Keypoints(
    cropped_image_size = (K_CROPPED_IMAGE_HEIGHT, K_CROPPED_IMAGE_WIDTH),
    cropped_positions = {'leye' : K_LEFT_EYE_POS, 'reye' : K_RIGHT_EYE_POS, 'eye' : K_EYE_POS, 'mouth' : K_MOUTH_POS},
    crop_image = True,
    fixed_annotations = {'reyeo': [0.,-K_OUTER_EYE_D/2.], 'reyei': [0.,-K_INNER_EYE_D/2.], 'leyei': [0.,K_INNER_EYE_D/2.], 'leyeo': [0.,K_OUTER_EYE_D/2.], 'nose': [K_EYE_NOSE_Y,0.], 'mouthr': [K_EYE_MOUTH_Y,-K_MOUTH_L/2.], 'mouthl': [K_EYE_MOUTH_Y,K_MOUTH_L/2.]},
    cropped_domain_annotations = True,
    relative_annotations = True,
    use_eye_corners = False,
)

# Feature extraction
dct_block_feature_extractor = facereclib.features.DCTBlocks(
    # block setup
    block_size = 12,
    block_overlap = 11,
    # coefficients
    number_of_dct_coefficients = 45
)

sift_feature_extractor = facereclib.features.SIFTBobKeypoints(
    sigmas = [1.75, 3.06, 9.38], 
    height = 200,
    width = 200,
    n_octaves = 5,
    n_scales = 3,
    octave_min = 0,
    sigma_n = 0.5,
    sigma0 = 1.6,
    contrast_thres = 0.03,
    edge_thres = 10.,
    norm_thres = 0.2,
    kernel_radius_factor = 4.,
    set_sigma0_no_init_smoothing = True,
)

# Classification algorithms
gmm_tool = facereclib.tools.UBMGMM(
    # GMM parameters
    k_means_training_iterations = 50, # Maximum number of iterations for K-Means
    gmm_training_iterations = 50,     # Maximum number of iterations for ML GMM Training
    training_threshold = 0.,          # Threshold to end the ML training (Do not stop using this criterium)
    number_of_gaussians = 512,
    relevance_factor = 4.,
    gmm_enroll_iterations = 1,
)

isv_tool = facereclib.tools.ISV(
    # GMM parameters
    number_of_gaussians = 512,
    # ISV parameters
    subspace_dimension_of_u = 200
)

jfa_tool = mytools.JFA(
    # GMM parameters
    number_of_gaussians = 512,
    # ISV parameters
    subspace_dimension_of_u = 10,
    subspace_dimension_of_v = 5
)

ivec_tool = mytools.IVector(
    # GMM parameters
    number_of_gaussians = 512,
    # ISV parameters
    subspace_dimension_of_t = 400,
)

pca_tool = facereclib.tools.PCA(
    # PCA parameters
    subspace_dimension = 1.,
    # Scoring
    distance_function = scipy.spatial.distance.cosine,
    is_distance_function = True,
    multiple_model_scoring = 'max',
    multiple_probe_scoring = 'max'
)

plda_tool = mytools.MyPLDA(
    subspace_dimension_pca = 200, # PCA dimension prior to PLDA
    subspace_dimension_of_f = 16, # Size of subspace F
    subspace_dimension_of_g = 16 # Size of subspace G
)

cosine_tool = mytools.Distance(
    distance_function = scipy.spatial.distance.cosine,
    is_distance_function = True,
    multiple_model_scoring = 'max',
    multiple_probe_scoring = 'average',
)



##############################################################################
###########################  LRPCA  ##########################################
LRPCA_IMAGE_RESOLUTION = (80, 80)
LRPCA_EYE_POSITIONS = {'reye': (26, 20), 'leye' : (26, 60)}

# LRPCA tuning as defaulted by facerec2010
import copy
LRPCA_TUNING = copy.deepcopy(facerec2010.baseline.lrpca.GBU_TUNING)

lrpca_preprocessor = xfacereclib.CSU.PythonFaceEvaluation.lrpca.ImageCrop(
    # tuning parameters (whatever this is...)
    TUNING = LRPCA_TUNING
)

lrpca_feature_extractor = xfacereclib.CSU.PythonFaceEvaluation.lrpca.Features(
    # tuning parameters (whatever this is...)
    TUNING = LRPCA_TUNING
)

lrpca_tool = xfacereclib.CSU.PythonFaceEvaluation.lrpca.Tool(
    # tuning parameters (whatever this is...)
    TUNING = LRPCA_TUNING
)

##############################################################################
###########################  LDA-IR  #########################################

# LDA-IR tuning as defaulted by facerec2010
LDAIR_REGION_ARGS = copy.deepcopy(facerec2010.baseline.lda.CohortLDA_REGIONS)
LDAIR_REGION_KEYWORDS = copy.deepcopy(facerec2010.baseline.lda.CohortLDA_KEYWORDS)
# we just disable the cohort normalization
for kwargs in LDAIR_REGION_ARGS:
  kwargs['cohort_adjust'] = False

ldair_preprocessor = xfacereclib.CSU.PythonFaceEvaluation.ldair.ImageCrop(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS
)

ldair_feature_extractor = xfacereclib.CSU.PythonFaceEvaluation.ldair.Features(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS
)

ldair_tool = xfacereclib.CSU.PythonFaceEvaluation.ldair.Tool(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS
)

