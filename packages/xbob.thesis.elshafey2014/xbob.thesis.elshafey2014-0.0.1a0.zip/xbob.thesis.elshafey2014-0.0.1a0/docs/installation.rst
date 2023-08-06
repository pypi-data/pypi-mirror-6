.. vim: set fileencoding=utf-8 :
.. Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
.. Wed Apr 17 15:48:58 CEST 2013

Installation
============

To download the xbob.thesis.elshafey2014 package, please go to http://pypi.python.org/pypi/xbob.thesis.elshafey2014, click on the **download** button and extract the .zip file to a folder of your choice.

The xbob.thesis.elshafey2014 is a satellite package of the free signal processing and machine learning library Bob_, and some of its algorithms rely on the `CSU Face Recognition Resources`_.
These two dependencies have to be downloaded manually, as explained in the following.


Bob
---

You will need a copy of Bob in version 1.2.2 to run the algorithms.
Please download Bob_ from its webpage.
If you have installed Bob_ in a non-standard directory, please open the `buildout.cfg <file:../buildout.cfg>`_ file and set the ``prefixes`` directory accordingly.

Once Bob_ is installed, you should go to the console and write::

  $ python bootstrap.py
  $ bin/buildout

This will download all required dependencies and install them locally.
If you don't want all the database packages to be downloaded, please remove the xbob.db.[database] lines from the ``eggs`` section of the file **buildout.cfg** in the main directory before calling the three commands above.


CSU face recognition resources
------------------------------

Due to the fact that the CSU toolkit needs to be patched to work with the `FaceRecLib <http://pypi.python.org/pypi/facereclib>`_, the setup is unfortunately slightly more complicated.
To be able to run the experiments based on the CSU toolkit, i.e., the LDA-IR and the LRPCA algorithms, please download the CSU face recognition resources from http://www.cs.colostate.edu/facerec/.
After unpacking the CSU toolkit, it needs to be patched.
For this reason, please follow the instructions::

  1. Patch the CSU toolkit::

    .. code-block:: sh

      $ python bootstrap.py
      $ bin/buildout -c buildout-before-patch.cfg
      $ bin/patch_CSU.py [YOUR_CSU_SOURCE_DIRECTORY]

  2. Update the *buildout.cfg* file:

    * modify the 'sources-dir = [YOUR_CSU_SOURCE_DIRECTORY]' entry to point to the patched version of the CSU toolkit

.. note::
  The patch file is only valid for the current version of the CSU toolkit (December 2012).
  If you have another version, please contact the maintainer (Manuel Guenther) to get help.

.. note::
  If you want, you can disable these dependencies by updating the buildbout.cfg file.
  You have to comment out the following two eggs: PythonFaceEvaluation and xfacereclib.extension.CSU,
  to comment out the sources-dir and the PythonFaceEvaluation variables.
  Next, you need to run bin/buildout afterwards.


Databases
---------

Experiments are conducted on several databases.
They should be downloaded and extracted manually to be able to reproduce the plots.

- BANCA [http://www.ee.surrey.ac.uk/CVSSP/banca]
- AR face database [http://www2.ece.ohio-state.edu/~aleix/ARdatabase.html]
- Face Recognition Grand Challenge version 2 [http://www.nist.gov/itl/iad/ig/frgc.cfm]
- The Good, The Bad and the Ugly [http://www.nist.gov/itl/iad/ig/focs.cfm]
- Labeled Faces in the Wild [http://vis-www.cs.umass.edu/lfw] (images aligned with funneling [http://vis-www.cs.umass.edu/lfw/lfw-funneled.tgz])
- Multi-PIE [http://www.multipie.org]
- MOBIO  [http://www.idiap.ch/dataset/mobio]
- CAS-PEAL [http://www.jdl.ac.cn/peal/index.html]
- NIST Speaker Recognition Evaluation 2012 [http://www.nist.gov/itl/iad/mig/sre12.cfm] (Additional data distributed by `LDC <https://www.ldc.upenn.edu/>`_ are required for training and development purposes [see https://pypi.python.org/pypi/xbob.db.nist_sre12])

Once you have installed the databases, you should set the path to raw data into some configuration files.
For instance, for running experiments on the BANCA database, you should set the variable 'banca_directory'
in the file `banca.py <file:../xbob/thesis/elshafey2014/databases/banca.py>`_ to your directory that 
contains the images of this database.

You should also download the annotations for the Labeled Faces in the Wild ([http://www.idiap.ch/resource/biometric/data/LFW-Annotations.tar.gz]) and MOBIO ([http://www.idiap.ch/dataset/mobio]) databases.

.. note::
  The GBU database uses the data from the MBGC http://www.nist.gov/itl/iad/ig/mbgc.cfm database of the NIST.
  The directory structure of the MBGC seems to be changed lately.
  We try to keep our GBU database interface up to date.
  If the directory structure of your copy of the database does not coincide with ours, please read the documentation of the `xbob.db.gbu <https://github.com/bioidiap/xbob.db.gbu>`_ to update the database interface.
