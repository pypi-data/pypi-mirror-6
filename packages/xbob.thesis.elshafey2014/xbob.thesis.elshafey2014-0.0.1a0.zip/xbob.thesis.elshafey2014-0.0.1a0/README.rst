Experiments of Laurent El Shafey's Ph.D. Thesis
===============================================

This package contains scripts to reproduce the experiments of my Ph.D. thesis at Ecole Polytechnique Fédérale de Lausanne (EPFL).
It was developed when I was working in the `Biometrics group <http://www.idiap.ch/~marcel/professional/Research_Team.html>`_ at the `Idiap Research Institute <http://www.idiap.ch>`_::

  @phdthesis{ElShafey_EPFL2014,
    title = {Scalable Probabilistic Models for Face and Speaker Recognition},
    author = {Laurent El Shafey},
    month = {April},
    year = {2014},
    school = {Ecole Polytechnique F{\'e}d{\'e}rale de Lausanne (EPFL)},
    url = {http://publications.idiap.ch/index.php/publications/show/2830},
  }

In particular, this package provides instructions to combine code (see Bob_, which contains the implementations of machine learning algorithms and signal processing tools) and data to generate the plots depicted in my thesis.


Installation
------------

To download the xbob.thesis.elshafey2014 package, please go to http://pypi.python.org/pypi/xbob.thesis.elshafey2014, click on the **download** button and extract the .zip file to a folder of your choice.

The xbob.thesis.elshafey2014 is a satellite package of the free signal processing and machine learning library Bob_, and some of its algorithms rely on the `CSU Face Recognition Resources`_.
These two dependencies have to be downloaded manually, as explained in the following.


Bob
...

You will need a copy of Bob in version 1.2.2 to run the algorithms.
Please download Bob_ from its webpage.
After downloading, you should go to the console and write::

  $ python bootstrap.py
  $ bin/buildout

This will download all required dependencies and install them locally.
If you don't want all the database packages to be downloaded, please remove the xbob.db.[database] lines from the ``eggs`` section of the file **buildout.cfg** in the main directory before calling the three commands above.


The CSU Face Recognition Resources
..................................

Two open source face recognition algorithms are provided by the `CSU Face Recognition Resources`_, namely the LRPCA and the LDA-IR (a.k.a. CohortLDA) algorithm.
For these algorithms, optional wrapper classes are provided in the xfacereclib.extension.CSU_ satellite package.
By default, this package is disabled.
To enable them, please call::

  $ bin/buildout -c buildout-with-csu.cfg

after downloading and patching the CSU resources, and updating the ``sources-dir`` in the **buildout-with-csu.cfg** file -- as explained in xfacereclib.extension.CSU_.


Databases
.........

Experiments are conducted on several databases.
They should be downloaded and extracted manually to be able to reproduce the plots.

- BANCA [http://www.ee.surrey.ac.uk/CVSSP/banca]
- AR face database [http://www2.ece.ohio-state.edu/~aleix/ARdatabase.html]
- Face Recognition Grand Challenge version 2 [http://www.nist.gov/itl/iad/ig/frgc.cfm]
- The Good, The Bad and the Ugly [http://www.nist.gov/itl/iad/ig/focs.cfm]
- Labeled Faces in the Wild [http://vis-www.cs.umass.edu/lfw] (images aligned with funneling [http://vis-www.cs.umass.edu/lfw/lfw-funneled.tgz] and annotations [http://www.idiap.ch/resource/biometric/data/LFW-Annotations.tar.gz])
- Multi-PIE [http://www.multipie.org]
- MOBIO  [http://www.idiap.ch/dataset/mobio] (images, audio data and image annotations)
- CAS-PEAL [http://www.jdl.ac.cn/peal/index.html]
- NIST Speaker Recognition Evaluation 2012 [http://www.nist.gov/itl/iad/mig/sre12.cfm] (Additional data distributed by `LDC <https://www.ldc.upenn.edu/>`_ are required for training and development purposes [see https://pypi.python.org/pypi/xbob.db.nist_sre12 to preprocess the data])

Once you have installed the databases, you should set the path to raw data into some configuration files.
For instance, for running experiments on the BANCA database, you should set the variable 'banca_directory'
in the file `banca.py <file:xbob/thesis/elshafey2014/databases/banca.py>`_ to your directory that 
contains the images of this database.
This is explained in more details in the complete documentation.


Running experiments
-------------------

If you have set up everything mentioned above, you are ready to run the recognition experiments.

This process is split into two different steps::

   1. Generation of raw scores from raw data (image/audio files [and possibly annotations]) of the databases

   2. Generation of plots from these raw scores

There is a single exception with the plots generated on the M-iris synthetic dataset.
In this case, the experiments does not require any external data and can be reproduced in one step.
In practice, the first step has high computational requirements, which depend on the database considered.


Read further
------------

There are several file links in the documentation, which won't work in the online documentation.
To generate the documentation locally, type::

  $ bin/sphinx-build docs sphinx
  $ firefox sphinx/index.html

and read further instructions on how to use this package.


Cite our paper
--------------

If you use this package in any of your experiments, please cite the following paper::

  @phdthesis{ElShafey_EPFL2014,
    title = {Scalable Probabilistic Models for Face and Speaker Recognition},
    author = {Laurent El Shafey},
    month = {April},
    year = {2014},
    school = {Ecole Polytechnique F{\'e}d{\'e}rale de Lausanne (EPFL)},
    url = {http://publications.idiap.ch/index.php/publications/show/2830},
  }


Problems
--------

In case of problems, please contact me (Laurent El Shafey).

If you are facing technical issues to be able to run the scripts 
of this package, you can send a message on the `Bob's mailing list
<https://groups.google.com/forum/#!forum/bob-devel>`_.

Please follow `these guidelines 
<http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/TicketReportingDev.html>`_
when (or even better before) reporting any bug.


.. _bob: http://www.idiap.ch/software/bob
.. _csu face recognition resources: http://www.cs.colostate.edu/facerec
.. _xfacereclib.extension.csu: http://pypi.python.org/pypi/xfacereclib.extension.CSU

