.. vim: set fileencoding=utf-8 :
.. Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
.. Sat Nov 30 19:17:13 CET 2013

Running the speaker recognition experiments
===========================================

This process is split into two different steps::

   1. Generation of raw scores from images (and annotations) of the databases

   2. Generation of plots from these raw scores

.. warning::
  These experiments (step 1.) require a long execution time (several days or weeks) and several Gigabytes of memory.


Generating raw scores
---------------------

After downloading the database, you should preprocess the data as described 
`here <https://pypi.python.org/pypi/xbob.db.nist_sre12>`_.

.. note:: In our experiments, we used the noisy data instead of the speech enhanced (denoised) data.
  Furthermore, the results of your experiments will be better if you use the correctly preprocessed data.

Next, you should set up the configuration files
`female.py <file:../xbob/thesis/elshafey2014/configurations/audio/nist_sre12/female.py>`_ and
`male.py <file:../xbob/thesis/elshafey2014/configurations/audio/nist_sre12/male.py>`_,
before being able to run the following set of scripts.


Feature extraction
..................

The extraction of the features is performed as follows::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA

   $ ./bin/mfcc_vad_energy.py -d xbob/thesis/elshafey2014/configurations/audio/nist_sre12/male.py -b mfcc -T ${MYTEMPDIR}/nist_sre12
   $ ./bin/mfcc_vad_energy.py -d xbob/thesis/elshafey2014/configurations/audio/nist_sre12/female.py -b mfcc -T ${MYTEMPDIR}/nist_sre12


GMM
...

The GMM toolchain is launched as follows::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/gmm.py -d nist-sre12-female -b gmm -T ${MYTEMPDIR}/nist_sre12 -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/nist_sre12/mfcc/features
   $ ./bin/gmm.py -d nist-sre12-male -b gmm -T ${MYTEMPDIR}/nist_sre12 -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/nist_sre12/mfcc/features


.. note:: A parallelized implementation for the GMM training was used in practice, as follows::

   $ ./bin/para_gmm.py -d nist-sre12-female -b gmm -T ${MYTEMPDIR}/nist_sre12 -U ${MYRESDIR}/nist_sre12 --groups 'dev' 'eval' --zt-norm  --skip-preprocessing --skip-extractor-training --skip-extraction --features-directory ${MYTEMPDIR}/nist_sre12/mfcc -t default-gmm -l 3000 --grid xbob/thesis/elshafey2014/configurations/grid/para_grid_gmm1024.py
   $ ./bin/para_gmm.py -d nist-sre12-male -b gmm -T ${MYTEMPDIR}/nist_sre12 -U ${MYRESDIR}/nist_sre12 --groups 'dev' 'eval' --zt-norm  --skip-preprocessing --skip-extractor-training --skip-extraction --features-directory ${MYTEMPDIR}/nist_sre12/mfcc -t default-gmm -l 3000 --grid xbob/thesis/elshafey2014/configurations/grid/para_grid_gmm1024.py


The UBM GMM experiments must be completed before running any of the following scripts.


ISV
...

The ISV toolchain is launched as follows::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ for u in 200 ; do
       for g in male female ; do 
         ./bin/isv.py -d nist-sre12-gd-${g} -b isv_u${u} -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done
     done


Note: A parallelized implementation for the ISV training was used in practice, as follows::

   $ for u in 200 ; do
       for g in male female ; do 
         ./bin/para_isv.py -d nist-sre12-gd-${g} -b isv_u${u} -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})" --grid para-grid-ivector
       done
     done


JFA
...

The JFA toolchain is launched as follows::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ for u in 100 50 ; do
       for g in female male ; do 
         ./bin/jfa.py -d nist-sre12-gd-${g} -b jfa_uv${u} -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014" 
       done
     done


Note: A parallelized implementation for the ISV training was used in practice, as follows::

   $ for u in 100 50 ; do
       for g in male female ; do 
         ./bin/para_jfa.py -d nist-sre12-gd-${g} -b jfa_uv${u} -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"  --grid para-grid-ivector
       done
     done


I-Vector
........

The I-Vector toolchain is launched as follows::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ for g in male female ; do
       ./bin/ivector.py -d nist-sre12-gd-${g} -b ivec400 -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm
     done

   $ for g in female male ; do
       ./bin/cosine_distance.py -d nist-sre12-gd-${g} --features-directory ${MYTEMPDIR}/nist_sre12_${g}/ivec400/wccn_projected_ivector -b ivec400_cosine -T ${MYTEMPDIR}/nist_sre12_${g} -b ivec400_cosine -U ${MYRESDIR}/nist_sre12 --groups dev eval --zt-norm 
       for f in 100 50; do
         ./bin/plda.py -d nist-sre12-gd-${g} -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/nist_sre12_${g}/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 -- --imports xbob.thesis.elshafey2014
       done
     done


Note: A parallelized implementation for the ISV training was used in practice, as follows::

   $ for g in male female ; do 
       ./bin/para_ivector.py -d nist-sre12-gd-${g} -b ivec400 -T ${MYTEMPDIR}/nist_sre12_${g} -U ${MYRESDIR}/nist_sre12 --gmm-directory ${MYTEMPDIR}/nist_sre12/gmm -t "xbob.thesis.elshafey2014.tools.IVector(number_of_gaussians = 512, subspace_dimension_of_t = 400)" --imports "xbob.thesis.elshafey2014" --grid para-grid-ivector
     done


Calibration and compound LLRs
.............................

Once the scores for all the systems have been generated, the following script will calibrate the LLR scores and converts them into compound LLRs::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/nist_sre12_postprocess.py -r ${MYRESDIR}



Plotting
--------

Once all the scores have been generated and calibrated, Figure 6.3 and 6.4 reported in the thesis can be obtained using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_nistsre12.py -r ${MYRESDIR} 
     ...
   $ xdg-open nist_sre12.pdf

