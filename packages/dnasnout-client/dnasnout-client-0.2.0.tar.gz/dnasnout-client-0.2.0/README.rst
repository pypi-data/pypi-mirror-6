About
=====

This script comes in support of the submitted paper:

*Low-bandwidth and non-compute intensive remote
identification of microbes from raw sequencing reads*.

- It requires:

    - Python 3.3 (note the ".3")

    - bowtie2 (parameter "-a", try "--help")

- It is self-documented (try "-h" or "--help").

- It is working on FASTQ or gzipped-FASTQ files, possibly on BAM files

Be gentle and please do not hammer the server like there is no tomorrow.

The latest released versions of the package will always be on Pypi.

Usage
=====

This installs as a regular Python package:

  python setup.py install

Development version
-------------------

   The following BASH lines show to install a development version in a virtual
   environment

   .. code:: bash

      # installation directory
      INSTALLDIR_CLIENT=./installclient_dir

      # install
      mkdir -p ${INSTALLDIR_CLIENT}
      # create a virtual environment (Python 3.3)
      # (if 3.3 is the only Python on your system, `pyvenv` will be enough)
      pyvenv-3.3 ${INSTALLDIR_CLIENT}/dnasnoutclient_env

      # use the virtual environment
      source ${INSTALLDIR_CLIENT}/dnasnoutclient_env/bin/activate

      # Install packages
      # bootstrap virtualenv
      wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python
      # install pip
      easy_install pip
      # install dependencies
      #     numpy
      pip install numpy 
      #     bitarray
      pip install bitarray
      #     ngs_plumbing
      pip install https://bitbucket.org/lgautier/ngs_plumbing/get/default.tar.gz
      # install dnasnout-client
      pip install https://bitbucket.org/lgautier/dnasnout-client/get/default.tar.gz
      # installation is complete
      # deactivate the virtualenv
      deactivate


Test the installation
^^^^^^^^^^^^^^^^^^^^^   

   .. code:: bash

      # use the virtual environment
      source ${INSTALLDIR_CLIENT}/dnasnoutclient_env/bin/activate
      cd ${INSTALLDIR_CLIENT}
      # download test data
      wget http://tapir.cbs.dtu.dk/static/iontorrent_head400.fq
      python -m dnasnout_client.console -i iontorrent_head400.fq -d iontorrent_test



The module can be run directly:

  python -m dnasnout_client.console

Help is available with:

  python -m dnasnout_client.console --help


Oh, and here is a screenshot:

.. image:: http://cbs.dtu.dk/~laurent/dnasnout/static/screenshot.png
   :alt: Screenshot
   :align: center

 
