#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri Sep 20 15:05:49 CEST 2013
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


from setuptools import setup, find_packages

setup(
    name='xbob.thesis.elshafey2014',
    version='0.0.1a0',
    description='Experiments of Laurent El Shafey\'s Ph.D. thesis',

    url='https://pypi.python.org/pypi/xbob.thesis.elshafey2014',
    license='GPLv3',
    author='Laurent El Shafey',
    author_email='Laurent.El-Shafey@idiap.ch',
    keywords='bob, xbob, face recognition, speaker recognition, bimodal recognition, facereclib, xbob.spkrec, GMM, ISV, JFA, TV, i-vector, PLDA, EPFL, Idiap',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools', # the tool to install dependent packages
      'bob == 1.2.2', # base signal processing/machine learning library
      'facereclib == 1.2.0', # the tool to run face recognition experiments
      'xbob.spkrec', # the tool to run speaker recognition experiments
    ],

    namespace_packages = [
      'xbob',
      'xbob.thesis',
    ],

    entry_points={
      # scripts should be declared using this entry:
      'console_scripts': [
        'lrpca.py                 = xbob.thesis.elshafey2014.scripts.lrpca:main',
        'ldair.py                 = xbob.thesis.elshafey2014.scripts.ldair:main',
        'dct.py                   = xbob.thesis.elshafey2014.scripts.dct:main',
        'mfcc_vad_energy.py       = xbob.thesis.elshafey2014.scripts.mfcc_vad_energy:main',
        'mfcc_vad_mod4hz.py       = xbob.thesis.elshafey2014.scripts.mfcc_vad_mod4hz:main',
        'para_gmm.py              = xbob.thesis.elshafey2014.scripts.para_gmm:main',
        'gmm.py                   = xbob.thesis.elshafey2014.scripts.gmm:main',
        'para_isv.py              = xbob.thesis.elshafey2014.scripts.para_isv:main',
        'isv.py                   = xbob.thesis.elshafey2014.scripts.isv:main',
        'para_jfa.py              = xbob.thesis.elshafey2014.scripts.para_jfa:main',
        'jfa.py                   = xbob.thesis.elshafey2014.scripts.jfa:main',
        'para_ivector.py          = xbob.thesis.elshafey2014.scripts.para_ivector:main',
        'ivector.py               = xbob.thesis.elshafey2014.scripts.ivector:main',
        'pca.py                   = xbob.thesis.elshafey2014.scripts.pca:main',
        'plda.py                  = xbob.thesis.elshafey2014.scripts.plda:main',
        'sift.py                  = xbob.thesis.elshafey2014.scripts.sift:main',
        'cosine_distance.py       = xbob.thesis.elshafey2014.scripts.cosine_distance:main',
        'nist_sre12_postprocess.py = xbob.thesis.elshafey2014.scripts.nist_sre12_postprocess:main',
        'mobio_fusion.py          = xbob.thesis.elshafey2014.scripts.mobio_fusion:main',

        'plot_miris.py            = xbob.thesis.elshafey2014.scripts.plot_miris:main',
        'plot_arface.py           = xbob.thesis.elshafey2014.scripts.plot_arface:main',
        'plot_banca.py            = xbob.thesis.elshafey2014.scripts.plot_banca:main',
        'plot_caspeal.py          = xbob.thesis.elshafey2014.scripts.plot_caspeal:main',
        'plot_example.py          = xbob.thesis.elshafey2014.scripts.plot_example:main',
        'plot_frgc.py             = xbob.thesis.elshafey2014.scripts.plot_frgc:main',
        'plot_gbu.py              = xbob.thesis.elshafey2014.scripts.plot_gbu:main',
        'plot_lfw.py              = xbob.thesis.elshafey2014.scripts.plot_lfw:main',
        'plot_lfwidentification.py = xbob.thesis.elshafey2014.scripts.plot_lfwidentification:main',
        'tell_error.py            = xbob.thesis.elshafey2014.scripts.tell_error:main',
        'plot_multipie.py         = xbob.thesis.elshafey2014.scripts.plot_multipie:main',

        'plot_nist_sre12.py       = xbob.thesis.elshafey2014.scripts.plot_nist_sre12:main',

        'plot_speech_duration.py  = xbob.thesis.elshafey2014.scripts.plot_speech_duration:main',
        'mobio_hter.py            = xbob.thesis.elshafey2014.scripts.mobio_hter:main',
        'plot_mobio_det.py        = xbob.thesis.elshafey2014.scripts.plot_mobio_det:main',
        'plot_mobio_scatters.py   = xbob.thesis.elshafey2014.scripts.plot_mobio_scatters:main',
        'mobio_common_errors.py   = xbob.thesis.elshafey2014.scripts.mobio_common_errors:main',
        'plot_mobio_hter_by_duration.py = xbob.thesis.elshafey2014.scripts.plot_mobio_hter_by_duration:main',
        'plot_mobio_hter.py       = xbob.thesis.elshafey2014.scripts.plot_mobio_hter:main',

        'full_eval.py             = xbob.thesis.elshafey2014.scripts.full_eval:main',
      ],

      # register the particular tools as resources of the FaceRecLib
      'facereclib.database': [
        'arface                   = xbob.thesis.elshafey2014.databases.arface:database',
        'banca                    = xbob.thesis.elshafey2014.databases.banca:database',
        'caspeal                  = xbob.thesis.elshafey2014.databases.caspeal:database',
        'frgc                     = xbob.thesis.elshafey2014.databases.frgc:database',
        'gbu                      = xbob.thesis.elshafey2014.databases.gbu:database',
        'lfw                      = xbob.thesis.elshafey2014.databases.lfw:database',
        'lfwidentification        = xbob.thesis.elshafey2014.databases.lfwidentification:database',
        'mobio-female             = xbob.thesis.elshafey2014.databases.mobio_female:database',
        'mobio-male               = xbob.thesis.elshafey2014.databases.mobio_male:database',
        'multipie                 = xbob.thesis.elshafey2014.databases.multipie:database',
        'multipie-pose            = xbob.thesis.elshafey2014.databases.multipie:database_pose',
        'multipie-frontal         = xbob.thesis.elshafey2014.databases.multipie:database_frontal',
        'multipie-left            = xbob.thesis.elshafey2014.databases.multipie:database_left',
        'multipie-right           = xbob.thesis.elshafey2014.databases.multipie:database_right',
        'multipie-P19_0           = xbob.thesis.elshafey2014.databases.multipie:database_P19_0',
        'multipie-P04_1           = xbob.thesis.elshafey2014.databases.multipie:database_P04_1',
        'multipie-P05_0           = xbob.thesis.elshafey2014.databases.multipie:database_P05_0',
        'multipie-P05_1           = xbob.thesis.elshafey2014.databases.multipie:database_P05_1',
        'multipie-P13_0           = xbob.thesis.elshafey2014.databases.multipie:database_P13_0',
        'multipie-P14_0           = xbob.thesis.elshafey2014.databases.multipie:database_P14_0',
        'multipie-P08_0           = xbob.thesis.elshafey2014.databases.multipie:database_P08_0',
        'multipie-P09_0           = xbob.thesis.elshafey2014.databases.multipie:database_P09_0',
        'multipie-P11_0           = xbob.thesis.elshafey2014.databases.multipie:database_P11_0',
        'multipie-P12_0           = xbob.thesis.elshafey2014.databases.multipie:database_P12_0',
        'multipie-P24_0           = xbob.thesis.elshafey2014.databases.multipie:database_P24_0',
        'multipie-P01_0           = xbob.thesis.elshafey2014.databases.multipie:database_P01_0',
        'multipie-P20_0           = xbob.thesis.elshafey2014.databases.multipie:database_P20_0',
        'nist-sre12-female        = xbob.thesis.elshafey2014.databases.nist_sre12_female:database',
        'nist-sre12-male          = xbob.thesis.elshafey2014.databases.nist_sre12_male:database',
        'nist-sre12-gd-female        = xbob.thesis.elshafey2014.databases.nist_sre12_gd_female:database',
        'nist-sre12-gd-male          = xbob.thesis.elshafey2014.databases.nist_sre12_gd_male:database',
      ],

      # register the preprocessors
      'facereclib.preprocessor': [
        'default-lrpca            = xbob.thesis.elshafey2014.configurations.default:lrpca_preprocessor',
        'default-ldair            = xbob.thesis.elshafey2014.configurations.default:ldair_preprocessor',
        'default-tan-triggs       = xbob.thesis.elshafey2014.configurations.default:tan_triggs_preprocessor',
        'left-tan-triggs          = xbob.thesis.elshafey2014.configurations.default:left_tan_triggs_preprocessor',
        'right-tan-triggs         = xbob.thesis.elshafey2014.configurations.default:right_tan_triggs_preprocessor',
        'default-keypoint         = xbob.thesis.elshafey2014.configurations.default:keypoint_preprocessor',
      ],  

      # register the feature extractors
      'facereclib.feature_extractor': [
        'default-lrpca            = xbob.thesis.elshafey2014.configurations.default:lrpca_feature_extractor',
        'default-ldair            = xbob.thesis.elshafey2014.configurations.default:ldair_feature_extractor',
        'default-dct-blocks       = xbob.thesis.elshafey2014.configurations.default:dct_block_feature_extractor',
        'default-sift             = xbob.thesis.elshafey2014.configurations.default:sift_feature_extractor',
      ],  

      # register the tools
      'facereclib.tool': [
        'default-lrpca            = xbob.thesis.elshafey2014.configurations.default:lrpca_tool',
        'default-ldair            = xbob.thesis.elshafey2014.configurations.default:ldair_tool',
        'default-gmm              = xbob.thesis.elshafey2014.configurations.default:gmm_tool',
        'default-isv              = xbob.thesis.elshafey2014.configurations.default:isv_tool',
        'default-jfa              = xbob.thesis.elshafey2014.configurations.default:jfa_tool',
        'default-ivector          = xbob.thesis.elshafey2014.configurations.default:ivec_tool',
        'default-pca              = xbob.thesis.elshafey2014.configurations.default:pca_tool',
        'default-plda             = xbob.thesis.elshafey2014.configurations.default:plda_tool',
        'default-cosine           = xbob.thesis.elshafey2014.configurations.default:cosine_tool',
      ], 

      # register SGE grid configuration files
      'facereclib.grid': [
        'para-grid                = xbob.thesis.elshafey2014.configurations.grid.para_grid:grid',
        'para-grid-dct            = xbob.thesis.elshafey2014.configurations.grid.para_grid_dct:grid',
        'para-grid-ivector        = xbob.thesis.elshafey2014.configurations.grid.para_grid_ivector:grid',
        'grid-16G                 = xbob.thesis.elshafey2014.configurations.grid.grid_16G:grid',
        'grid-24G                 = xbob.thesis.elshafey2014.configurations.grid.grid_24G:grid',
        'grid-w16G                = xbob.thesis.elshafey2014.configurations.grid.grid_w16G:grid',
        'grid-w24G                = xbob.thesis.elshafey2014.configurations.grid.grid_w24G:grid',
        'grid-w32G                = xbob.thesis.elshafey2014.configurations.grid.grid_w32G:grid',
      ],

    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
)
