===============================================================================
 Complementary Countermeasures for Detecting Scenic Face Spoofing Attacks
===============================================================================

This package combines motion and texture analysis based countermeasures to 2D facial spoofing attacks as described in the paper 'Complementary Countermeasures for Detecting Scenic Face Spoofing Attacks', International Conference on Biometrics, 2013. However, it is possible to fuse scores of any combination of countermeasures using the tools provided by this package.

If you use this package and/or its results, please cite the following
publications:

1. The original paper with the fusion of countermesures explained in details::

    @inproceedings{Komulainen_ICB_2013,
      author = {Komulainen, Jukka and Anjos, Andr{\'{e}} and Marcel, S{\'{e}}bastien and Hadid, Abdenour and Pietik{\"a}inen, Matti},
      month = Jun,
      title = {Complementary Countermeasures for Detecting Scenic Face Spoofing Attacks},
      journal = {International Conference on Biometrics 2013},
      year = {2013},
    }

2. Bob as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
        author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
    }

If you wish to report problems or improvements concerning this code, please
contact the authors of the above mentioned papers.

Raw data
--------

The data used in the paper is provided by two other satellite packges: antispoofing.motion and antispoofing.lbp. These packages should be downloaded and installed **prior** to using the programs described in this package. Visit `the antispoofing.motion <http://pypi.python.org/pypi/antispoofing.motion>`_ and `the antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ pages for more information.

Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.fusion
  <http://pypi.python.org/pypi/antispoofing.fusion>`_ to download the latest
  stable version of this package.

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install antispoofing.fusion

You can also do the same with ``easy_install``::

  $ easy_install antispoofing.fusion

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/antispoofing.fusion>`_ and unpack it in your
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
  inside this package. Because this package makes use of `Bob
  <http://idiap.github.com/bob>`_, you must make sure that the ``bootstrap.py``
  script is called with the **same** interpreter used to build Bob, or
  unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or add the
  line ``prefixes`` to point to the directory where Bob is installed or built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build/lib

User Guide
----------

It is assumed that you have followed the installation instructions for this package and got it installed. Furthermore, we assume that you have installed the two related packages and produced output scores for each frame using both `the antispoofing.motion <http://pypi.python.org/pypi/antispoofing.motion>`_ and `the antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ packages and that these scores sit on the directory ``./scores/``. If not, please create symbolic links to this directory.

Finding Valid Output Scores 
===========================

The previously generated outputs do not contain a valid score for each video frame. The motion based countermeasure needs 20 video frames for analyzing the motion correlation between the face and the background, i.e. the method cannot produce scores for the first 19 frames. On the other hand, the LBP based countermeasure is able to produce an valid output score when a face is successfully detected and the face size is above 50x50 pixels. 

Therefore, the frames, in which the both countermeasures have valid score (i.e. not NaN value), must be found before performing the fusion at score level. This process is performed using the script ``./bin/find_valid_frames.py`` and by giving the locations of all used output scores, e.g.:: 

  $ ./bin/find_valid_frames.py -s scores/motion_lda scores/lbp_lda -e replay

Combining the Valid Output Scores
=================================

The script ``fuse_scores.py`` performs the fusion of the any countermeasures at score level using some of the two different methods: sum of scores or logistic linear regression (LLR) with the selected score normalization scheme: minmax, zscore or without any normalization, e.g.:: 

  $ ./bin/fuse_scores.py -s scores/motion_lda scores/lbp_lda -f SUM -n ZNorm -o scores/lda_sum_z
  $ ./bin/fuse_scores.py -s scores/motion_lda scores/lbp_lda -f LLR -n None -o scores/lda_llr_raw

Analyzing the Results of Fusion at Frame-level
==============================================

The performance of the individual countermeasures and their fusion can be dumped in to a file ``./results/frame_based/results.txt`` using the script ``frame_by_frame_analysis.py``::

  $ ./bin/frame_by_frame_analysis.py -s scores/motion_lda scores/lbp_lda -f scores/lda_sum_z scores/lda_llr_raw -e replay
  
The ``results.txt`` shows the performance of each method at frame-level.

Running the Time Analysis
=========================

The time analysis is the end of the processing chain, it fuses the scores of instantaneous scores for each method to give out a better estimation of attacks and real-accesses. To use it::

  $ ./bin/time_analysis.py -s scores/motion_lda scores/lbp_lda -f scores/lda_sum_z scores/lda_llr_raw -e replay
  
The time evolution for each method can be found in directory ``./results/evolution/``. The folder also contains a PDF file in which you can find all methods in same figure.

Mutual Error Analysis
=====================

The script ``venn.py`` performs mutual error analysis on the given countermeasures and outputs the results into a file ``./results/Venn&scatter/Venn.txt``::

  $ ./bin/venn.py -s scores/motion_lda scores/lbp_lda -e replay 


Problems
--------

In case of problems, please contact any of the authors of the paper.
