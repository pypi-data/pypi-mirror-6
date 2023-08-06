.. vim: set fileencoding=utf-8 :
.. Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
.. Tue Mar  4 13:58:50 CET 2014

M-iris examples
===============

The M-iris dataset is a synthetic dataset, which aims at highlighting how the algorithms described in my Ph.D. thesis work on a toy example.
It is inspired from the Fisher's iris dataset.

The following script will apply the following techniques to this dataset:

- Gaussian mixture modeling (GMM)
- Inter-session variability modeling (ISV)
- Joint factor analysis (JFA)
- Total variability modeling (TV)
- Probabilistic linear discriminant analysis (PLDA)

It does not require any external data, and should complete in less than a couple of minutes::

  $ ./bin/plot_miris.py
  $ xdg-open miris.pdf

Figures 3.1, 3.2, 3.3, 3.4, 3.5, 3.7, and 4.1 of my thesis correspond to pages extracted from the previously generated pdf file.

