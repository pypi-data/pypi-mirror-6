=================================================
 Example of an Article with Reproducible Results
=================================================

This package demonstrates how to provide scripts and source code relying on Bob
for reproducible machine learning experiments. In particular, this document
explains how to produce the Receiver Operating Characteristic (ROC) of our paper.

If you use this package and/or its results, please cite the following
publications:

1. The original paper attached with this satellite package::

    @article{Bob_2013,
      author = {L. El~Shafey AND A. Anjos AND M. G\"unther AND E. Khoury AND I. Chingovska AND F. Moulin AND S. Marcel},
      title = {Bob: A Free Library for Reproducible Machine Learning},
      year = {2013},
    }

2. To use the MNIST database, you should also mention the following paper,
   where it is introduced::

    @article{LeCun_1998,
      author = {Y. LeCun AND L. Bottou AND Y. Bengio AND P. Haffner},
      title = {Gradient-Based Learning Applied to Document Recognition},
      journal = {Proceedings of the IEEE},
      month = {November},
      volume = {86},
      number = {11},
      pages = {2278-2324},
      year = {1998}
    }


This package is built upon two other satellite packages:

1. `xbob.db.mnist <http://pypi.python.org/pypi/xbob.db.mnist>`_ which contains easy accessors
   to the MNIST database

2. `xbob.mlp.lbfgs <http://pypi.python.org/pypi/xbob.mlp.lbfgs>`_ which shows how to extend
   Bob with an additional learning algorithm.

This decomposition in three pieces is performed for clarity and reusability. Data access,
learning algorithm implementation and scripts for generating the plots and evaluating the
performances are, hence, well separated. In addition, anyone could reuse any of these
satellite packages easily for his own work.


Raw data
--------

The data used in the paper is publicly available and can be downloaded and
installed prior to using the scripts provided in this package. Visit
`THE MNIST DATABASE of handwritten digits website <http://yann.lecun.com/exdb/mnist/>`_,
download the four provided .gz files and save them in a directory of your choice, without
extracting the archives. If the path to the downloaded data is not supplied when
running the any of the scripts, this database will be downloaded on the fly in a
temporary directory at **each** script call.

Installation
------------

First, you have to install `Bob <http://www.idiap.ch/software/bob>`_ following the instructions
`there <http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/Installation.html>`_.
Afterward, you need a copy of this package.

.. note::

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/xbob.paper.example
  <http://pypi.python.org/pypi/xbob.paper.example>`_ to download the latest
  stable version of this package.

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package. In both cases, the two
dependences listed above will be automatically downloaded and installed.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install xbob.paper.example

You can also do the same with ``easy_install``::

  $ easy_install xbob.paper.example

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/xbob.paper.example>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::

  $ python bootstrap.py
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob`_, you must make
  sure that the ``bootstrap.py`` script is called with the **same** interpreter
  used to build Bob, or unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 2
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or
  add the line ``prefixes`` to point to the directory where Bob is installed or
  built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build


User Guide
----------

It is assumed you have followed the installation instructions for the package
and got this package installed and optionally the MNIST database downloaded and
uncompressed in a directory. You should have all required utilities sitting
inside a binary directory depending on your installation strategy (utilities
will be inside the ``bin`` directory if you used the buildout option).


Paper Layout: How to Reproduce our Results
==========================================

The paper demonstrates how to use and extend the Bob toolkit by considering two
learning algorithms applied to multilayer perceptrons (MLP). The first one is the
R-prop algorithm, which is already integrated into Bob. The second one relies on
the L-BFGS optimization procedure, and is integrated in a separate satellite
package to demonstrate how the Bob library might be extended. Furthermore, this
satellite package aims at only providing that plug these bricks together to
evaluate algorithms on a specific dataset (MNIST), and to generate plots.
The two learning algorithms mentionned above will be applied to two different multilayer
perceptron architectures. The first one has no hidden layer (linear classifier), whereas
the second one has a hidden layer of 50 nodes.

References:

Algorithm 1 - R-prop::

  @inproceedings{Riedmiller_1993,
    author = {M. Riedmiller AND H. Braun},
    title = {{Direct Adaptive Method for Faster Backpropagation Learning: The {RPROP} Algorithm}},
    pages = {586--591},
    volume = {Proceedings of the IEEE International Conference on Neural Networks},
    year = {1993}
  }

Algorithm 2 - L-BFGS::

  @article{Byrd_1994,
    author = {R. H. Byrd AND J. Nocedal AND R. B. Schnabel},
    title = {Representations of quasi-{N}ewton matrices and their use in limited memory methods},
    issn={0025-5610},
    journal = {Mathematical Programming},
    volume = {63},
    number = {1-3},
    doi = {10.1007/BF01582063},
    publisher = {Springer-Verlag},
    pages = {129-156},
    year = {1994},
  }

Training the four multilayer perceptrons
========================================

Two scripts are provided to learn multilayer perceptrons. One makes use of the
R-prop algorithm, whereas the other one relies on the L-BFGS optimization
technique.

In the paper, the ROC was generated by applying these two learning algorithms
to two different multilayer perceptron architectures as described above.

To run the training process, use the following command::

  $ ./bin/rprop_training.py -d /root/of/database -H 0 -m rprop_H00.hdf5

This will train a multilayer perceptron with 0 hidden nodes (linear classifier),
using 50 iterations of R-Prop, save the resulting multilayer perceptron into
an HDF5 file and finally compute the classification error rate on the test
set of MNIST.

Since the MNIST database used for this example is pretty small, you could also
run this script without specifying the path to the database, which will in this
case be automatically downloaded in a temporary directory before calling the
learning procedure.


Next, you could learn the other three multilayer perceptrons in a completely
similar way, as follows::

  $ ./bin/rprop_training.py -d /root/of/database -H 50 -m rprop_H50.hdf5
  $ ./bin/lbfgs_training.py -d /root/of/database -H  0 -m lbfgs_H00.hdf5
  $ ./bin/lbfgs_training.py -d /root/of/database -H 50 -m lbfgs_H50.hdf5

On a recent workstation (Intel core i7), each (single-thread) script should
complete in less than an hour. If you have a multi-core CPU, you could of
course run the scripts in parallel.


Plotting the ROC for the four systems
=====================================

Once you have learned the multilayer perceptrons, you can easily plot the ROC
using the following command::

  $ ./bin/plot.py -d /root/of/database -m rprop_H00.hdf5 rprop_H50.hdf5 lbfgs_H00.hdf5 lbfgs_H50.hdf5 \
    -l '1-layer MLP (R-prop)' '2-layer MLP (R-prop)' '1-layer MLP (L-BFGS)' '2-layer MLP (L-BFGS)' -o roc.pdf

This will compute the scores on the test set of the MNIST database for each
multilayer perceptron, and plot the performances on a ROC, which is saved as a
pdf file.


Evaluating to get the classification error rate
===============================================

If you have a trained multilayer perceptron, you can easily compute
the classification error rate (CER) using the following command::

  $ ./bin/evaluate.py -d /root/of/database -m MLP_TO_EVALUATE.hdf5

This will return the CER on the test set of the MNIST database.


Getting further
---------------

If you are interested into packaging your own work into your own satellite
package, you could reuse the layout of this package. You can also find more
detailed information in this
`tutorial <http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/OrganizeYourCode.html>`_.

Learning by looking at `other examples <https://github.com/idiap/bob/wiki/Satellite-Packages>`_
is also a good practice.

In case of problem or question, just ask for help to the Bob's **community**
through the `mailing list <https://groups.google.com/forum/#!forum/bob-devel>`_
or the `issue tracker <https://github.com/idiap/bob/issues>`_.
