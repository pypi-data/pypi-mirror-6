=====================================
Score Calibration in Face Recognition
=====================================

This package provides the source code to run the experiments published in the paper `Score Calibration in Face Recognition <http://publications.idiap.ch/index.php/publications/show/2708>`_.
It relies on the FaceRecLib_ to execute the face recognition experiments, and on Bob_ to compute the calibration experiments.

.. note::
  Currently, this package only works in Unix-like environments and under MacOS.
  Due to limitations of the Bob_ library, MS Windows operating systems are not supported.
  We are working on a port of Bob_ for MS Windows, but it might take a while.
  In the meanwhile you could use our VirtualBox_ images that can be downloaded `here <http://www.idiap.ch/software/bob/images>`_.


Installation
============
The installation of this package relies on the `BuildOut <http://www.buildout.org>`_ system. By default, the command line sequence::

  $ ./python bootstrap.py
  $ ./bin/buildout

should download and install all requirements, including the FaceRecLib_, the database interfaces `xbob.db.scface <http://pypi.python.org/pypi/xbob.db.scface>`_, `xbob.db.mobio <http://pypi.python.org/pypi/xbob.db.mobio>`_ and all their required packages.
There are a few exceptions, which are not automatically downloaded:


Bob
---
The face recognition experiments rely on the open source signal-processing and machine learning toolbox Bob_.
To install Bob_, please visit http://www.idiap.ch/software/bob and follow the installation instructions.
Please verify that you have at least version 1.2.0 of Bob installed.
If you have installed Bob in a non-standard directory, please open the buildout.cfg file from the base directory and set the ``prefixes`` directory accordingly.

.. note::
  The experiments that we report in the Paper_ were generated with Bob version 1.2.1 and FaceRecLib_ version 1.2.1.
  If you use different versions of either of these packages, the results might differ slightly.
  For example, we are aware that, due to some initialization differences, the results using Bob 1.2.0 and 1.2.1 are not identical, but similar.


Image Databases
---------------
The experiments are run on external image databases.
We do not provide the images from the databases themselves.
Hence, please contact the database owners to obtain a copy of the images.
The two databases used in our experiments can be downloaded here:

- SCface [``scface``]: http://www.scface.org
- MOBIO [``mobio``]: http://www.idiap.ch/dataset/mobio

.. note::
  For the MOBIO database, you need to sign the EULA to get access to the data -- the process is explained under the above MOBIO link.
  After signing the EULA, please download the image files **IMAGES_PNG.tar.gz** and the annotation files **IMAGE_ANNOTATIONS.tar.gz** and extract the archives into directories of your choice.

Important!
''''''''''
After downloading the databases, you will need to tell our software, where it can find them by changing the **configuration files**.
In particular, please update the ``scface_directory`` in **xfacereclib/paper/IET2014/database_scface.py**, as well as ``mobio_image_directory`` and ``mobio_annotation_directory`` in **xfacereclib/paper/IET2014/database_mobio.py**.
Please let all other configuration parameters unchanged as this might influence the face recognition experiments and, hence, the reproducibility of the results.

Getting help
------------
In case anything goes wrong, please feel free to open a new ticket in our GitLab_ page, or send an email to manuel.guenther@idiap.ch.


Recreating the results of the Paper_
====================================

After successfully setting up the databases, you are now able to run the face recognition and calibration experiments as explained in the Paper_.

The experiment configuration
----------------------------
The face recognition experiment are run using the FaceRecLib_, but for convenience there exists a wrapper script that set up the right parametrization for the call to the FaceRecLib_.
The configuration files that are used by the FaceRecLib_, which contain all the parameters of the experiments, can be found in the **xfacereclib/paper/IET2014/** directory.
Particularly, the **xfacereclib/paper/IET2014/dct_mobio.py** and **xfacereclib/paper/IET2014/isv_mobio.py** files contain the configuration for the DCT block features and the ISV algorithm as described in the Paper_.
Accordingly,

Running the experiments
-----------------------
This script can be found in ``bin/iet2014_face_recog.py``.
It requires some command line options, which you can list using ``./bin/iet2014_face_recog.py --help``.
Usually, the command line options have a long version (starting with ``--``) and a shortcut (starting with a single ``-``), here we use only the long versions:

- ``--temp-directory``: Specify a directory where temporary files will be stored (default: ``temp``). This directory can be deleted after all experiments ran successfully.
- ``--result-directory``: Specify a directory where final result files will be stored (default: ``results``). This directory is required to evaluate the experiments.
- ``--databases``: Specify a list of databases that you want your experiments to run on. Possible values are ``scface`` and ``mobio``. By default, experiments on both databases are executed.
- ``--protocols``: Specify a list of protocols that you want to run. Possible values are ``combined``, ``close``, ``medium`` and ``far`` for database ``scface``, and ``male`` and ``female`` for ``mobio``. By default, all protocols are used.
- ``--combined-zt-norm``: Execute the face recognition experiments on the SCface database with combined ZT-norm cohort.
- ``--verbose``: Print out additional information or debug information during the execution of the experiments. The ``--verbose`` option can be used several times, increasing the level to Warning (1), Info (2) and Debug (3). By default, only Error (0) messages are printed.
- ``--dry-run``: Use this option to print the calls to the FaceRecLib_ without executing them.

Additionally, you can pass options directly to the FaceRecLib_, but you should do that with care.
Simply use ``--`` to separate options to the ``bin/iet2014_face_recog.py`` from options to the FaceRecLib_.
For example, the ``--force`` option might be of interest.
See ``./bin/faceverify.py --help`` for a complete list of options.

It is advisable to use the ``--dry-run`` option before actually running the experiments, just to see that everything is correct.
Also, the Info (2) verbosity level prints useful information, e.g., by adding the ``--verbose --verbose`` (or shortly ``-vv``) on the command line.
A commonly used command line sequence to execute the face recognition algorithm on both databases could be:

1. Run the experiments on the MOBIO database::

    $ ./bin/iet2014_face_recog.py -vv --databases mobio

2. Run the experiments on the SCface database, using protocol-specific files for the ZT-norm::

    $ ./bin/iet2014_face_recog.py -vv --databases scface

3. Run the experiments on the SCface database, using files from all distance conditions for the ZT-norm::

    $ ./bin/iet2014_face_recog.py -vv --databases scface --combined-zt-norm --protocols close medium far

.. note::
  All output directories of the scripts will be automatically generated if they do not exist yet.

.. warning::
  The execution of the script may take a long time and require large amounts of memory -- especially on the MOBIO database.
  Nevertheless, the scripts are set up such that they re-use all parts of the experiments as far as this is possible.



Evaluating the experiments
--------------------------
After all experiments have finished successfully, the resulting score files can be evaluated.
For this, the ``bin/iec2014_evaluate.py`` script can be used to create the Tables 3, 4, 5 and 6 of the Paper_, simply by writing LaTeX-compatible files that can later be interpreted to generate the tables.

Generating output files
'''''''''''''''''''''''

Also, all information are written to console (when using the ``-vvv`` option to enable debug information), including:

1. The :math:`C^{\mathrm{min}}_{\mathrm{ver}}` of the development set, the :math:`C^{\mathrm{min}}_{\mathrm{ver}}` of the evaluation set and the :math:`C_{\mathrm{ver}}` of the evaluation set based on the optimal threshold on the development set.

2. The :math:`C_{\mathrm{frr}}` on both development and evaluation set, using the threshold defined at ``FAR=1%`` of the development set.

3. The :math:`C_{\mathrm{ver}}` on the development and evaluation set, when applying threshold :math:`\theta_0=0` (mainly useful for calibrated scores).

4. The :math:`C_{\mathrm{cllr}}` performance on the development and the evaluation set.

5. The :math:`C^{\mathrm{min}}_{\mathrm{cllr}}` performance on the development and the evaluation set.

All these numbers are computed with and without ZT score normalization, and before and after score calibration.

To run the script, some command line parameters can be specified, see ``./bin/iec2014_evaluate.py --help``:

- ``--result-directory``: Specify the directory where final result files are stored (default: ``results``). This should be the same directory as passed to the `bin/iec2014_execute.py`` script.
- ``--databases``: Specify a list of databases that you want evaluate. Possible values are ``scface`` and ``mobio``. By default, both databases are evaluated.
- ``--protocols``: Specify a list of protocols that you want to evaluate. Possible values are ``combined``, ``close``, ``medium`` and ``far`` for database ``scface``, and ``male`` and ``female`` for ``mobio``. By default, all protocols are used.
- ``--combined-zt-norm``: Evaluate the face recognition experiments on the SCface database with combined ZT-norm cohort.
- ``--combined-threshold``: Evaluate the face recognition experiments on the SCface database by computing the threshold on the combined development set.
- ``--latex-directory``: The directory, where the final score files will be placed into, by default this directory is ``latex``.

Again, the most usual way to compute the resulting tables could be:

1. Evaluate experiments on MOBIO::

    $ bin/iet2014_evaluate.py -vvv --database mobio

2. Evaluate experiments on SCface with distance-dependent ZT-norm::

    $ bin/iet2014_evaluate.py -vvv --database scface

3. Evaluate experiments on SCface with distance-independent ZT-norm::

    $ bin/iet2014_evaluate.py -vvv --database scface --combined-zt-norm --protocols close medium far

4. Evaluate experiments on SCface with distance-independent threshold (will mainly change the :math:`C_{\mathrm{ver}}` of the evaluation set)::

    $ bin/iet2014_evaluate.py -vvv --database scface --combined-threshold --protocols close medium far

5. The experiments to compare linear calibration with categorical calibration as given in Table 7 of the Paper_ are run using the ``bin/iet2014_categorical.py`` script::

    $ bin/iet2014_categorical.py -vvv


Generate the LaTeX tables
'''''''''''''''''''''''''

Finally, the LaTeX tables can be regenerated by defining the accordant ``\Result`` and ``\ResultAtZero`` LaTeX macros and include the resulting files.
E.g., to create Table 3 of the Paper_, define::

  \newcommand\ResultIII[2]{\\}
  \newcommand\ResultII[9]{#1\,\% \ResultIII}
  \newcommand\Result[9]{#1\,\% & #4\,\% & #2\,\% & #3\,\% & #5\,\% & #6\,\% & #9\,\% & #7\,\% & #8\,\% &\ResultII}
  \newcommand\ResultAtZero[8]{}

set up your ``tabular`` environment with 10 columns and input at according places::

  \input{latex/mobio_male}
  \input{latex/mobio_female}
  \input{latex/scface_close}
  \input{latex/scface_medium}
  \input{latex/scface_far}
  \input{latex/scface_combined}

Accordingly, the other tables can be generated from files:

- Table 4a):  ``latex/scface_close-zt.tex``, ``latex/scface_medium-zt.tex`` and ``latex/scface_far-zt.tex``
- Table 4b):  ``latex/scface_close-thres.tex``, ``latex/scface_medium-thres.tex`` and ``latex/scface_far-thres.tex``
- Tables 5 and 6: ``latex/mobio_male.tex``, ``latex/mobio_female.tex``, ``latex/scface_close-zt.tex``, ``latex/scface_medium-zt.tex``, ``latex/scface_far-zt.tex`` and ``latex/scface_combined.tex`` .
- Table 7: ``latex/calibration-none.tex``, ``latex/calibration-linear.tex`` and ``latex/calibration-categorical.tex``


Generate the score distribution plots
'''''''''''''''''''''''''''''''''''''

At the end, also the score distribution plots that are shown in Figures 3 and 4 of the Paper_ can be regenerated.
These plots require the face recognition experiments to have finished, and also the categorical calibration to have run.
Afterwards, the script ``bin/iet2014_plot.py`` can be executed.
Again, the script has a list of command line options:

- ``--result-directory``: Specify the directory where final result files are stored (default: ``results``). This should be the same directory as passed to the `bin/iec2014_execute.py`` script.
- ``--figure``: Specify, which figure you want to create. Possible values are 3 and 4.
- ``--output-file``: Specify the file, where the plots should be written to. By default, this is ``Figure_3.pdf`` or ``Figure_4.pdf`` for ``--figure 3`` or  ``--figure 4``, respectively.

Hence, running::

  $ ./bin/iet2014_plot.py -vv --figure 3
  $ ./bin/iet2014_plot.py -vv --figure 4

should be sufficient to generate the plots.


.. _paper: http://publications.idiap.ch/index.php/publications/show/2708
.. _idiap: http://www.idiap.ch
.. _bob: http://www.idiap.ch/software/bob
.. _facereclib: http://pypi.python.org/pypi/facereclib
.. _gitlab: http://gitlab.idiap.ch/manuel.guenther/xfacereclib-paper-iet2014
.. _virtualbox: http://www.virtualbox.org


