.. vim: set fileencoding=utf-8 :
.. Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
.. Sat Nov 30 19:17:13 CET 2013

Running the bimodal recognition experiments
===========================================

This process is split into two different steps::

   1. Generation of raw scores from images (and annotations) of the databases

   2. Generation of plots from these raw scores

Generation of raw scores
------------------------

After downloading the database, the annotations and setting up the configuration files 
`mobio_female.py <file:../xbob/thesis/elshafey2014/database/mobio_female.py>`_,
`mobio_male.py <file:../xbob/thesis/elshafey2014/database/mobio_male.py>`_,
`female.py <file:../xbob/thesis/elshafey2014/configurations/audio/mobio/female.py>`_ and
`male.py <file:../xbob/thesis/elshafey2014/configurations/audio/mobio/male.py>`_,
you are able to run the following set of scripts::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # Speaker
   $ ./bin/mfcc_vad_mod4hz.py -d xbob/thesis/elshafey2014/configurations/audio/mobio/male.py -b mfcc -T ${MYTEMPDIR}/mobio_speaker
   $ ./bin/mfcc_vad_mod4hz.py -d xbob/thesis/elshafey2014/configurations/audio/mobio/female.py -b mfcc -T ${MYTEMPDIR}/mobio_speaker

   $ for proto in laptop_mobile1 laptop1 mobile1 ; do
       for g in male female ; do
         p=${proto}-${g}
        
         ./bin/gmm.py -d mobio-${g} -b gmm -P $p -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/mobio_speaker/mfcc/features -t default-gmm

         for u in 200 100 50 20 10 5 2; do
           ./bin/isv.py -d mobio-${g} -b isv_u${u} -P $p -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/mobio_speaker/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})" 
         done

         for u in 50 40 30 20 10 5 2; do
           ./bin/jfa.py -d mobio-${g} -b jfa_uv${u} -P $p -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/mobio_speaker/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
         done

         ./bin/ivector.py -d mobio-${g} -b ivec400 -P $p -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker --gmm-directory ${MYTEMPDIR}/mobio_speaker/gmm
         ./bin/cosine_distance.py -d mobio-${g} --features-directory ${MYTEMPDIR}/mobio_speaker/ivec400/wccn_projected_ivector -P $p -b ivec400_cosine -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker --groups dev eval --zt-norm --grid grid
         for f in 50 40 30 20 10 5 2; do
           ./bin/plda.py -d mobio-${g} -P $p -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/mobio_speaker/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/mobio_speaker -U ${MYRESDIR}/mobio_speaker -- --imports xbob.thesis.elshafey2014
         done
       done
     done


   $ # Face
   $ for proto in laptop_mobile1 laptop1 mobile1 ; do
       for g in male female ; do
         p=${proto}-${g}
         ./bin/dct.py -d mobio-${g} -b dct -P $p -T ${MYTEMPDIR}/mobio_face --groups dev eval

         ./bin/gmm.py -d mobio-${g} -b gmm -P $p -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/mobio_face/dct/features -t default-gmm

         for u in 200 100 50 20 10 5 2; do
           ./bin/isv.py -d mobio-${g} -b isv_u${u} -P $p -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/mobio_face/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
         done

         for u in 50 40 30 20 10 5 2; do
           ./bin/jfa.py -d mobio-${g} -b jfa_uv${u} -P $p -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/mobio_face/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014" --grid grid-16G
         done

         ./bin/ivector.py -d mobio-${g} -b ivec400 -P $p -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face --gmm-directory ${MYTEMPDIR}/mobio_face/gmm
         ./bin/cosine_distance.py -d mobio-${g} --features-directory ${MYTEMPDIR}/mobio_face/ivec400/wccn_projected_ivector -P $p -b ivec400_cosine -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face --groups dev eval --zt-norm --grid grid
         for f in 50 40 30 20 10 5 2; do
           ./bin/plda.py -d mobio-${g} -P $p -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/mobio_face/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/mobio_face -U ${MYRESDIR}/mobio_face -- --imports xbob.thesis.elshafey2014
         done
       done
     done


Once face and speaker recognition experiments are completed, you are able 
to perform the bimodal fusion as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # Fusion
   $ ./bin/mobio_fusion.py -r ${MYRESDIR}


Plotting
--------

Once all the scores have been generated, the plots on MOBIO reported in the thesis can be obtained as follows.

Figure 7.3 requires the features and that the NIST SRE12 experiments are also completed. 
Once done, it can be generated by::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/plot_speech_duration.py -t ${MYTEMPDIR} 
   $ xdg-open mobio_speech_duration_probes.pdf


The values of Table 7.2 and 7.3 are obtained as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/mobio_hter.py -r ${MYRESDIR}
     ...


Figure 7.4 and 7.5 are obtained as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/plot_mobio_det.py -r ${MYRESDIR}
   $ xdg-open mobio_det.pdf 


The values of Table 7.4 are obtained as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/mobio_common_errors.py -r ${MYRESDIR}
     ...


Figure 7.6 is obtained as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/plot_mobio_scatters.py -r ${MYRESDIR}
   $ xdg-open mobio_scatters.pdf 


Figure 7.7 is obtained as follows, but requires the features to be computed::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/plot_mobio_hter_by_duration.py -r ${MYRESDIR} -t ${MYTEMPDIR}
   $ xdg-open mobio_hter_by_duration.pdf


Figure 7.8 is obtained as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/plot_mobio_hter.py -r ${MYRESDIR}
   $ xdg-open mobio_hter.pdf

