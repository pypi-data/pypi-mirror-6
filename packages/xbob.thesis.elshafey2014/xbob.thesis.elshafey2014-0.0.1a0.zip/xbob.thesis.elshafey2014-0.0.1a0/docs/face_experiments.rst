.. vim: set fileencoding=utf-8 :
.. Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
.. Sat Nov 30 19:17:13 CET 2013

Running the face recognition experiments
========================================

This process is split into two different steps::

   1. Generation of raw scores from images (and annotations) of the databases

   2. Generation of plots from these raw scores

.. warning::
  These experiments require a long execution time (several days or weeks) and several Gigabytes of memory.


ARface
------

Generation of raw scores
........................

After downloading the database and setting up the configuration file 
`arface.py <file:../xbob/thesis/elshafey2014/databases/arface.py>`_, 
you should run the following set of scripts.
All the main loops are independent and can be split as different processes 
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # all illumination occlusion occlusion_and_illumination expression

   $ for p in all illumination occlusion occlusion_and_illumination expression ;
   $ do
       ./bin/pca.py -d arface -b pca -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval

       ./bin/dct.py -d arface -b dct -P ${p} -T ${MYTEMPDIR}/arface --groups dev eval
       ./bin/gmm.py -d arface -b gmm -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval --features-directory ${MYTEMPDIR}/arface/dct/features
       for u in 200 100 50 20 10 5 2; do
         ./bin/isv.py -d arface -b isv_u${u} -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval --gmm-directory ${MYTEMPDIR}/arface/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done
       for u in 100 50 20 10 5 2; do 
         ./bin/jfa.py -d arface -b jfa_uv${u} -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval --gmm-directory ${MYTEMPDIR}/arface/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
       done
       ./bin/ivector.py -d arface -b ivec400 -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --gmm-directory ${MYTEMPDIR}/arface/gmm
       ./bin/cosine_distance.py -d arface --features-directory ${MYTEMPDIR}/arface/ivec400/wccn_projected_ivector -P ${p} -b ivec400_cosine -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval
       for f in 50 40 30 20 10 5 2 ; do
         ./bin/plda.py -d arface -P ${p} -b ivec400_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/arface/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface -- --imports xbob.thesis.elshafey2014
       done
       ./bin/sift.py -d arface -b sift -P ${p} -T ${MYTEMPDIR}/arface --groups dev eval
       for f in 50 40 30 20 10 5 2; do
         ./bin/plda.py -d arface -P ${p} -b sift_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/arface/sift/features -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface -- --imports xbob.thesis.elshafey2014
       done

       ./bin/lrpca.py -d arface -b lrpca -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval
       ./bin/ldair.py -d arface -b ldair -P ${p} -T ${MYTEMPDIR}/arface -U ${MYRESDIR}/arface --groups dev eval
     done


Plotting
........

Once all the scores have been generated, Figure 5.11 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_arface.py -r ${MYRESDIR} 
     ...
   $ xdg-open arface.pdf


The AR face scores were also used to generate sample ROC, DET and CMC curves.
Figures 2.2 and 2.3 can be generated as follows::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ plot_example.py -r ${MYRESDIR}
   $ xdg-open example.pdf


BANCA
-----

Generation of raw scores
........................

After downloading the database and setting up the configuration file
`banca.py <file:../xbob/thesis/elshafey2014/databases/banca.py>`_, 
you should run the following set of scripts. 
Experiments are conducted on the protocol P of BANCA.
All the loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/pca.py -d banca -b pca -P P -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm

   $ ./bin/dct.py -d banca -b dct -P P -T ${MYTEMPDIR}/banca --groups dev eval
   $ ./bin/gmm.py -d banca -b gmm -P P -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/banca/dct/features/
   $ for u in 200 100 50 20 10 5 2; do
       ./bin/isv.py -d banca -b isv_u${u} -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/banca/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
     done
   $ for u in 100 50 20 10 5 2; do # values above 30 do not make sense
       ./bin/jfa.py -d banca -b jfa_uv${u} -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/banca/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
     done
   $./bin/ivector.py -d banca -b ivec200 -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --gmm-directory ${MYTEMPDIR}/banca/gmm -t "xbob.thesis.elshafey2014.tools.IVector(number_of_gaussians = 512, subspace_dimension_of_t = 200)" --imports "xbob.thesis.elshafey2014"
   $ ./bin/cosine_distance.py -d banca --features-directory ${MYTEMPDIR}/banca/ivec200/wccn_projected_ivector -P P -b ivec200_cosine -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm
   $ for f in 30 20 10 5 2; do
       ./bin/plda.py -d banca -P P -b ivec200_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/banca/ivec200/wccn_projected_ivector -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/sift.py -d banca -b sift -P P -T ${MYTEMPDIR}/banca --groups dev eval
   $ for f in 30 20 10 5 2; do
       ./bin/plda.py -d banca -P P -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/banca/sift/features -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/lrpca.py -d banca -b lrpca -P P -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm
   $ ./bin/ldair.py -d banca -b ldair -P P -T ${MYTEMPDIR}/banca -U ${MYRESDIR}/banca --groups dev eval --zt-norm


Plotting
........

Once all the scores have been generated, Figure 5.13 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_banca.py -r ${MYRESDIR} 
     ...
   $ xdg-open banca.pdf



CAS-PEAL
--------

Generation of raw scores
........................

After downloading the database and setting up the configuration file
`caspeal.py <file:../xbob/thesis/elshafey2014/databases/caspeal.py>`_, 
you should run the following set of scripts. 
All the main loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # accessory aging background distance expression lighting

   $ for p in accessory aging background distance expression lighting ; do
       ./bin/lrpca.py -d caspeal -b lrpca -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev
       ./bin/pca.py -d caspeal -b pca -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev
       ./bin/dct.py -d caspeal -b dct -P ${p} -T ${MYTEMPDIR}/caspeal --groups dev
       ./bin/gmm.py -d caspeal -b gmm -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev --features-directory ${MYTEMPDIR}/caspeal/dct/features/

       for u in 200 100 50 20 10 5 2; do
         ./bin/isv.py -d caspeal -b isv_u${u} -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev --gmm-directory ${MYTEMPDIR}/caspeal/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done

       for u in 100 50 20 10 5 2; do 
         ./bin/jfa.py -d caspeal -b jfa_uv${u} -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev --gmm-directory ${MYTEMPDIR}/caspeal/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
       done

       ./bin/ivector.py -d caspeal -b ivec400 -P ${p} -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --gmm-directory ${MYTEMPDIR}/caspeal/gmm
       ./bin/cosine_distance.py -d caspeal --features-directory ${MYTEMPDIR}/caspeal/ivec400/wccn_projected_ivector -P ${p} -b ivec400_cosine -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal --groups dev
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d caspeal -P ${p} -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/caspeal/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/caspeal -U ${MYRESDIR}/caspeal -- --imports xbob.thesis.elshafey2014
       done

       ./bin/sift.py -d caspeal -b sift -P ${p} -T ${MYTEMPDIR}/caspeal --groups dev
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d caspeal -P ${p} -b sift_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/caspeal/sift/features/ -T ${MYTEMPDIR}/caspeal/ -U ${MYRESDIR}/caspeal/ -- --imports xbob.thesis.elshafey2014
       done
     done


Plotting
........

Once all the scores have been generated, Figure 5.14 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_caspeal.py -r ${MYRESDIR} 
     ...
   $ xdg-open caspeal.pdf

.. note:: The Tables will be displayed in the output stream of the terminal once the script completed.



FRGC
----

Generation of raw scores
........................

After downloading the database and setting up the configuration file
`frgc.py <file:../xbob/thesis/elshafey2014/databases/frgc.py>`_, 
you should run the following set of scripts. 
All the main loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # 2.0.1 2.0.2 2.0.4

   $ for p in 2.0.1 2.0.2 2.0.4 ; do 
       ./bin/lrpca.py -d frgc -b lrpca -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev
       ./bin/ldair.py -d frgc -b ldair -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev
       ./bin/pca.py -d frgc -b pca -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev
       ./bin/dct.py -d frgc -b dct -P ${p} -T ${MYTEMPDIR}/frgc --groups dev
       #./bin/para_gmm.py -d frgc -b gmm -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev -g para-grid-dct --features-directory ${MYTEMPDIR}/frgc/dct/features/ --skip-preprocessing --skip-extraction
       ./bin/gmm.py -d frgc -b gmm -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev --features-directory ${MYTEMPDIR}/frgc/dct/features/

       for u in 100 ; do
         ./bin/isv.py -d frgc -b isv_u${u} -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev --gmm-directory ${MYTEMPDIR}/frgc/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done

       for u in 50 ; do 
         ./bin/jfa.py -d frgc -b jfa_uv${u} -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev --gmm-directory ${MYTEMPDIR}/frgc/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
       done


       ./bin/ivector.py -d frgc -b ivec400 -P ${p} -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --gmm-directory ${MYTEMPDIR}/frgc/gmm
       ./bin/cosine_distance.py -d frgc -P ${p} --features-directory ${MYTEMPDIR}/frgc/ivec400/wccn_projected_ivector -b ivec400_cosine -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc --groups dev
       for f in 40; do
         ./bin/plda.py -d frgc -P ${p} -b ivec400_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/frgc/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc -- --imports xbob.thesis.elshafey2014
       done

       ./bin/sift.py -d frgc -b sift -P ${p} -T ${MYTEMPDIR}/frgc --groups dev
       for f in 40; do
         ./bin/plda.py -d frgc -P ${p} -b sift_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/frgc/sift/features -T ${MYTEMPDIR}/frgc -U ${MYRESDIR}/frgc -- --imports xbob.thesis.elshafey2014
       done
     done


Plotting
........

Once all the scores have been generated, Figure 5.15 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_frgc.py -r ${MYRESDIR} 
     ...
   $ xdg-open frgc.pdf



GBU
---

Generation of raw scores
........................

After downloading the database and setting up the configuration file
`gbu.py <file:../xbob/thesis/elshafey2014/databases/gbu.py>`_, 
you should run the following set of scripts. 
All the main loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # Good Bad Ugly

   $ for p in Good Bad Ugly ; do
       ./bin/lrpca.py -d gbu -b lrpca -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev
       ./bin/ldair.py -d gbu -b ldair -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev
       ./bin/pca.py -d gbu -b pca -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev
       ./bin/dct.py -d gbu -b dct -P ${p} -T ${MYTEMPDIR}/gbu --groups dev
       ./bin/gmm.py -d gbu -b gmm -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev --features-directory ${MYTEMPDIR}/gbu/dct/features/

       for u in 200 100 50 20 10 5 2; do
         ./bin/isv.py -d gbu -b isv_u${u} -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev --gmm-directory ${MYTEMPDIR}/gbu/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done

       for u in 100 50 20 10 5 2; do 
         ./bin/jfa.py -d gbu -b jfa_uv${u} -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --groups dev --gmm-directory ${MYTEMPDIR}/gbu/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
       done

       ./bin/ivector.py -d gbu -b ivec400 -P ${p} -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu --gmm-directory ${MYTEMPDIR}/gbu/gmm
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d gbu -P ${p} -b ivec400_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/gbu/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu -- --imports xbob.thesis.elshafey2014
       done

       ./bin/sift.py -d gbu -b sift -P ${p} -T ${MYTEMPDIR}/gbu --groups dev
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d gbu -P ${p} -b sift_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/gbu/sift/features -T ${MYTEMPDIR}/gbu -U ${MYRESDIR}/gbu -- --imports xbob.thesis.elshafey2014
       done
     done


Plotting
........

Once all the scores have been generated, Figure 5.16 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_gbu.py -r ${MYRESDIR} 
     ...
   $ xdg-open gbu.pdf



LFW
---

Generation of raw scores
........................

After downloading the database, the annotations [http://www.idiap.ch/resource/biometric/data/LFW-Annotations.tar.gz], 
and setting up the configuration file 
`lfw.py <file:../xbob/thesis/elshafey2014/databases/lfw.py>`_, 
you should run the following set of scripts. 
All the main loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ # view1

   $ ./bin/lrpca.py -d lfw -b lrpca-view1 -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev
   $ ./bin/ldair.py -d lfw -b ldair-view1 -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev
   $ ./bin/pca.py -d lfw -b pca-view1 -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev

   $ ./bin/dct.py -d lfw -b dct -P view1 -T ${MYTEMPDIR}/lfw --groups dev eval
   $ ./bin/gmm.py -d lfw -b gmm -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev --features-directory ${MYTEMPDIR}/lfw/dct/features/
   $ #./bin/para_gmm.py -d lfw -b gmm -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev -g para-grid-dct --features-directory ${MYTEMPDIR}/lfw/dct/features/ --skip-preprocessing --skip-extraction

   $ for u in 200 100 50 20 10 5 2; do
       ./bin/isv.py -d lfw -b isv_u${u} -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev --gmm-directory ${MYTEMPDIR}/lfw-view1/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
     done

   $ for u in 100 50 20 10 5 2; do
       ./bin/jfa.py -d lfw -b jfa_uv${u} -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev --gmm-directory ${MYTEMPDIR}/lfw-view1/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
     done

   $ ./bin/ivector.py -d lfw -b ivec400 -P view1 -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --gmm-directory ${MYTEMPDIR}/lfw-view1/gmm
   $ ./bin/cosine_distance.py -d lfw --features-directory ${MYTEMPDIR}/lfw-view1/ivec400/wccn_projected_ivector -P view1 -b ivec400_cosine -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 --groups dev
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d lfw -P view1 -b ivec400_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfw-view1/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/sift.py -d lfw -b sift -P view1 -T ${MYTEMPDIR}/lfw --groups dev
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d lfw -P view1 -b sift_plda_fg${f} --groups dev -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfw/sift/features -T ${MYTEMPDIR}/lfw-view1 -U ${MYRESDIR}/lfw-view1 -- --imports xbob.thesis.elshafey2014
     done


   $ # 10 folds

   $ for f in `seq 1 10`; do
       ./bin/lrpca.py -d lfw -b lrpca -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval
       ./bin/ldair.py -d lfw -b ldair -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval
       ./bin/pca.py -d lfw -b pca -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval
     done

   $ for f in `seq 1 10`; do 
       ./bin/dct.py -d lfw -b dct -P fold${f} -T ${MYTEMPDIR}/lfw --groups dev eval
       ./bin/gmm.py -d lfw -b gmm -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval --features-directory ${MYTEMPDIR}/lfw/dct/features/
       #./bin/para_gmm.py -d lfw -b gmm -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval -g para-grid-dct --features-directory ${MYTEMPDIR}/lfw/dct/features/ --skip-preprocessing --skip-extraction ;
       for u in 200 100 50 20 10 5 2; do
         ./bin/isv.py -d lfw -b isv_u${u} -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval --gmm-directory ${MYTEMPDIR}/lfw-fold${f}/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
       done

       for u in 100 50 20 10 5 2; do
         ./bin/jfa.py -d lfw -b jfa_uv${u} -P fold${f} -T ${MYTEMPDIR}/lfw-fold${f} -U ${MYRESDIR}/lfw --groups dev eval --gmm-directory ${MYTEMPDIR}/lfw-fold${f}/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
       done
     done

   $ for p in `seq 1 10`; do
       ./bin/ivector.py -d lfw -b ivec400 -P fold${p} -T ${MYTEMPDIR}/lfw-fold${p} -U ${MYRESDIR}/lfw --gmm-directory ${MYTEMPDIR}/lfw-fold${p}/gmm
       ./bin/cosine_distance.py -d lfw --features-directory ${MYTEMPDIR}/lfw-fold${p}/ivec400/wccn_projected_ivector -P fold${p} -b ivec400_cosine -T ${MYTEMPDIR}/lfw-fold${p} -U ${MYRESDIR}/lfw --groups dev eval
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d lfw -P fold${p} -b ivec400_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfw-fold${p}/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/lfw-fold${p} -U ${MYRESDIR}/lfw -- --imports xbob.thesis.elshafey2014
       done
     done

   $ for p in `seq 1 10`; do
       ./bin/sift.py -d lfw -b sift -P fold${f} -T ${MYTEMPDIR}/lfw --groups dev eval
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d lfw -P fold${p} -b sift_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfw/sift/features -T ${MYTEMPDIR}/lfw-fold${p} -U ${MYRESDIR}/lfw -- --imports xbob.thesis.elshafey2014;
       done
     done


Plotting
........

Once all the scores have been generated, Figure 5.17 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_lfw.py -r ${MYRESDIR} 
     ...
   $ xdg-open lfw.pdf


LFW (Identification)
--------------------

Generation of raw scores
........................

After downloading the database, the annotations [http://www.idiap.ch/resource/biometric/data/LFW-Annotations.tar.gz], 
and setting up the configuration file 
`lfwidentification.py <file:../xbob/thesis/elshafey2014/databases/lfwidentification.py>`_, 
you should run the following set of scripts. 
All the loops are independent and can be split as different processes
(Don't forget to set the MYTEMPDIR and MYRESDIR variables within each terminal)::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS

   $ ./bin/pca.py -d lfwidentification -b pca -P P0 -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval

   $ ./bin/dct.py -d lfwidentification -b dct -P P0 -T ${MYTEMPDIR}/lfwidentification --groups dev eval
   $ ./bin/gmm.py -d lfwidentification -b gmm -P P0 -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval --features-directory ${MYTEMPDIR}/lfwidentification/dct/features/
   $ for u in 200 100 50 20 10 5 2; do
       ./bin/isv.py -d lfwidentification -b isv_u${u} -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval --gmm-directory ${MYTEMPDIR}/lfwidentification/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
     done
   $ for u in 100 50 20 10 5 2; do
       ./bin/jfa.py -d lfwidentification -b jfa_uv${u} -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval --gmm-directory ${MYTEMPDIR}/lfwidentification/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
     done
   $./bin/ivector.py -d lfwidentification -b ivec400 -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --gmm-directory ${MYTEMPDIR}/lfwidentification/gmm -t "xbob.thesis.elshafey2014.tools.IVector(number_of_gaussians = 512, subspace_dimension_of_t = 200)" --imports "xbob.thesis.elshafey2014"
   $ ./bin/cosine_distance.py -d lfwidentification --features-directory ${MYTEMPDIR}/lfwidentification/ivec400/wccn_projected_ivector -P P0 -b ivec400_cosine -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d lfwidentification -P P0 -b ivec400_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfwidentification/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/sift.py -d lfwidentification -b sift -P P0 -T ${MYTEMPDIR}/lfwidentification --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d lfwidentification -P P0 -b sift_plda_fg${f} --groups dev eval -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/lfwidentification/sift/features -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/lrpca.py -d lfwidentification -b lrpca -P P0 -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval
   $ ./bin/ldair.py -d lfwidentification -b ldair -P P0 -T ${MYTEMPDIR}/lfwidentification -U ${MYRESDIR}/lfwidentification --groups dev eval


Plotting
........

Once all the scores have been generated, Figure 5.18 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_lfwidentification.py -r ${MYRESDIR} 
     ...
   $ xdg-open lfwidentification.pdf


To get the largest errors performed by the recognition systems, you can use the following scripts::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/tell_error.py -r ${MYRESDIR}

This allows to plot Figure 5.19.


Multi-PIE
---------

Generation of raw scores
........................

After downloading the database, the annotations [see http://www.idiap.ch/resource/biometric/],
and setting up the configuration file 
`multipie.py <file:../xbob/thesis/elshafey2014/databases/multipie.py>`_, 
you should run the following set of scripts::

   $ MYTEMPDIR=YOUR_DIRECTORY_WHERE_TO_PUT_TEMPDATA
   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS


   $ # Illumination 
   $ # M
   $ ./bin/lrpca.py -d multipie -b lrpca -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/ldair.py -d multipie -b ldair -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/pca.py -d multipie -b pca -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/dct.py -d multipie -b dct -P M -T ${MYTEMPDIR}/multipie-I --groups dev eval
   $ ./bin/gmm.py -d multipie -b gmm -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --zt-norm
   $ #./bin/para_gmm.py -d multipie -b gmm -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval -g para-grid-dct --zt-norm --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --skip-preprocessing --skip-extraction

   $ for u in 200 100 50 20 10 5 2; do
       ./bin/isv.py -d multipie -b isv_u${u} -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/multipie-I/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
     done

   $ for u in 100 50 20 10 5 2; do 
       ./bin/jfa.py -d multipie -b jfa_uv${u} -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/multipie/gmm-I -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
     done

   $ ./bin/ivector.py -d multipie -b ivec400 -P M -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --gmm-directory ${MYTEMPDIR}/multipie-I/gmm
   $ ./bin/cosine_distance.py -d multipie --features-directory ${MYTEMPDIR}/multipie-I/ivec400/wccn_projected_ivector -P M -b ivec400_cosine -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P M -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-I/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/sift.py -d multipie -b sift -P M -T ${MYTEMPDIR}/multipie-I --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P M -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-I/sift/features/ -T ${MYTEMPDIR}/multipie-I/ -U ${MYRESDIR}/multipie-I/ -- --imports xbob.thesis.elshafey2014
     done


   $ # U
   $ ./bin/lrpca.py -d multipie -b lrpca -P U -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/ldair.py -d multipie -b ldair -P U -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/pca.py -d multipie -b pca -P U -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/dct.py -d multipie -b dct -P U -T ${MYTEMPDIR}/multipie-I --groups dev eval
   $ ./bin/gmm.py -d multipie -b gmm -P U -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --zt-norm
   $ #./bin/para_gmm.py -d multipie -b gmm -P U -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval -g para-grid-dct --zt-norm --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --skip-preprocessing --skip-extraction

   $ ./bin/sift.py -d multipie -b sift -P U -T ${MYTEMPDIR}/lfw --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P U -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-I/sift/features/ -T ${MYTEMPDIR}/multipie-I/ -U ${MYRESDIR}/multipie-I/ -- --imports xbob.thesis.elshafey2014
     done


   $ # G
   $ ./bin/lrpca.py -d multipie -b lrpca -P G -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/ldair.py -d multipie -b ldair -P G -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/pca.py -d multipie -b pca -P G -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --zt-norm
   $ ./bin/dct.py -d multipie -b dct -P G -T ${MYTEMPDIR}/multipie-I --groups dev eval
   $ ./bin/gmm.py -d multipie -b gmm -P G -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --zt-norm
   $ #./bin/para_gmm.py -d multipie -b gmm -P G -T ${MYTEMPDIR}/multipie-I -U ${MYRESDIR}/multipie-I --groups dev eval -g para-grid-dct --zt-norm --features-directory ${MYTEMPDIR}/multipie-I/dct/features/ --skip-preprocessing --skip-extraction

   $ ./bin/sift.py -d multipie -b sift -P G -T ${MYTEMPDIR}/lfw --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P G -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-I/sift/features/ -T ${MYTEMPDIR}/multipie-I/ -U ${MYRESDIR}/multipie-I/ -- --imports xbob.thesis.elshafey2014
     done


   $ # Pose
   $ # P
   $ ./bin/pca.py -d multipie-frontal -b pca -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm -- --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation
   $ ./bin/pca.py -d multipie-left -p left-tan-triggs -b pca -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm -- --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation
   $ ./bin/pca.py -d multipie-right -p right-tan-triggs -b pca -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm -- --skip-projector-training --skip-projection --skip-enroller-training --skip-enrollment --skip-score-computation --skip-concatenation

   $ ./bin/pca.py -d multipie-pose -b pca -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm -- --skip-preprocessing

   $ ./bin/lrpca.py -d multipie-frontal -b lrpca -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm
   $ ./bin/ldair.py -d multipie-frontal -b ldair -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm

   $ for p in P190 P041 P050 P051 P130 P140 P080; do
       ./bin/lrpca.py -d multipie-frontal -b lrpca -P $p -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm
     done
   $ for p in P190 P041 P050 P051 P130 P140 P080; do
       ./bin/ldair.py -d multipie-frontal -b ldair -P $p -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm
     done

   $ ./bin/dct.py -d multipie-frontal -b dct -P P -T ${MYTEMPDIR}/multipie-P --groups dev eval
   $ ./bin/dct.py -d multipie-left -p left-tan-triggs -b dct -P P -T ${MYTEMPDIR}/multipie-P --groups dev eval
   $ ./bin/dct.py -d multipie-right -p right-tan-triggs -b dct -P P -T ${MYTEMPDIR}/multipie-P --groups dev eval
   $ ./bin/gmm.py -d multipie-pose -b gmm -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --features-directory ${MYTEMPDIR}/multipie-P/dct/features/ --zt-norm
   $ #./bin/para_gmm.py -d multipie-pose -b gmm -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval -g para-grid-dct --zt-norm --features-directory ${MYTEMPDIR}/multipie-P/dct/features/ --skip-preprocessing --skip-extraction

   $ ./bin/ivector.py -d multipie-pose -b ivec400 -P P -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --gmm-directory ${MYTEMPDIR}/multipie-P/gmm
   $ ./bin/cosine_distance.py -d multipie-pose --features-directory ${MYTEMPDIR}/multipie-P/ivec400/wccn_projected_ivector -P P -b ivec400_cosine -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P --groups dev eval --zt-norm
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie-pose -P P -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-P/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P -- --imports xbob.thesis.elshafey2014
     done

   $ for p in P190 P041 P050 P051 P130 P140 P080; do
       ./bin/sift.py -d multipie-frontal -b sift -P $p -T ${MYTEMPDIR}/multipie-P --groups dev eval
       for f in 60 50 40 30 20 10 5 2; do
         ./bin/plda.py -d multipie-frontal -P ${p} -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-P/sift/features -T ${MYTEMPDIR}/multipie-P -U ${MYRESDIR}/multipie-P -- --imports xbob.thesis.elshafey2014
       done
     done


   $ # Expression 
   $ # E
   $ ./bin/lrpca.py -d multipie -b lrpca -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm
   $ ./bin/ldair.py -d multipie -b ldair -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm
   $ ./bin/pca.py -d multipie -b pca -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm
   $ ./bin/dct.py -d multipie -b dct -P E -T ${MYTEMPDIR}/multipie-E --groups dev eval
   $ ./bin/gmm.py -d multipie -b gmm -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm --features-directory ${MYTEMPDIR}/multipie-E/dct/features/

   $ for u in 200 100 50 20 10 5 2; do
       ./bin/isv.py -d multipie -b isv_u${u} -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/multipie-E/gmm -t "facereclib.tools.ISV(number_of_gaussians=512, subspace_dimension_of_u=${u})"
     done

   $ for u in 100 50 20 10 5 2; do 
       ./bin/jfa.py -d multipie -b jfa_uv${u} -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm --gmm-directory ${MYTEMPDIR}/multipie-E/gmm -t "xbob.thesis.elshafey2014.tools.JFA(number_of_gaussians=512, subspace_dimension_of_u=${u}, subspace_dimension_of_v=${u})" --imports "xbob.thesis.elshafey2014"
    done

   $ ./bin/ivector.py -d multipie -b ivec400 -P E -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --gmm-directory ${MYTEMPDIR}/multipie-E/gmm
   $ ./bin/cosine_distance.py -d multipie --features-directory ${MYTEMPDIR}/multipie-E/ivec400/wccn_projected_ivector -P E -b ivec400_cosine -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E --groups dev eval --zt-norm
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P E -b ivec400_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = None, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-E/ivec400/wccn_projected_ivector -T ${MYTEMPDIR}/multipie-E -U ${MYRESDIR}/multipie-E -- --imports xbob.thesis.elshafey2014
     done

   $ ./bin/sift.py -d multipie -b sift -P E -T ${MYTEMPDIR}/multipie-E --groups dev eval
   $ for f in 60 50 40 30 20 10 5 2; do
       ./bin/plda.py -d multipie -P E -b sift_plda_fg${f} --groups dev eval --zt-norm -t "xbob.thesis.elshafey2014.tools.MyPLDA(subspace_dimension_pca = 200, subspace_dimension_of_f = ${f}, subspace_dimension_of_g = ${f})" --features-directory ${MYTEMPDIR}/multipie-E/sift/features/ -T ${MYTEMPDIR}/multipie-E/ -U ${MYRESDIR}/multipie-E/ -- --imports xbob.thesis.elshafey2014
     done


Plotting
........

Once all the scores have been generated, Figure 5.10 and 5.12 reported in the thesis can be obtained by using::

   $ MYRESDIR=YOUR_DIRECTORY_WHERE_TO_PUT_RESULTS
   $ ./bin/plot_multipie.py -r ${MYRESDIR} 
     ...
   $ xdg-open multipie.pdf

.. note:: The Tables will be displayed in the output stream of the terminal once the script completed.
