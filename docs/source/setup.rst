
=================
Environment Setup
=================

In order to use Py4Syn there are some prerequisites. Here are the list and a basic guide to help you to setup the environment to run you scripts using Py4Syn.

To execute the next steps be sure to have a login with administrator rights in your machine.

This assumes you're running Red Hat Enterprise Linux in your machine, for other distributions please check the correct/equivalent packages to install.


First of all let's switch to super user::
    
   sudo su

Python 3.x Installation
~~~~~~~~~~~~~~~~~~~~~~~

In order to install Python there are some required packages that will be installed with the following commands::

    yum groupinstall "Development tools"
    yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel xz libpng-devel
    
Now we need to add a line at the end of `ld.so.conf` file and run `ldconfig`::

    echo "/usr/local/lib" >> /etc/ld.so.conf
    /sbin/ldconfig
    
Download the lastest Python version, in this case it's Python 3.4.1, using this `link (Python 3.4.1 Download) <https://www.python.org/ftp/python/3.4.1/Python-3.4.1.tar.xz>`_.

Extract the downloaded file with::

    tar xf Python-3.4.1.tar.xz
    
Enter the extracted folder and run the following commands::

    cd Python-3.4.1
    ./configure
    make && make altinstall
    
After the installation finish include the new Python in the `root user` path with::

    export PATH=$PATH:/usr/local/bin
    

Freetype2 Installation
~~~~~~~~~~~~~~~~~~~~~~

To install most of the Python libraries Freetype2 is needed. Follow the next steps to correctly install Freetype2 in your computer.

Download the lastest version, using this `link (Freetype 2.4.0) <http://download.savannah.gnu.org/releases/freetype/freetype-2.4.0.tar.gz>`_.

Extract the downloaded file with::

    tar -xzvf freetype-2.4.0.tar.gz
    
Enter the extracted folder and run the commands bellow to install::

    cd freetype-2.4.0
    ./configure
    make
    make install

SetupTools and Pip Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SetupTools and Pip are the most used Python tools to install packages and libraries.

Download the `ez_setup` script from this `link <https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py>`_ or use this `internal link <http://intranet.lnls.br/grupos/sol/py4syn/install/ez_setup.py>`_.

Run the script to install `easy_install`::

    python3.4 ez_setup.py
    
And finally install `pip`::

    easy_install-3.4 pip
    
Enabling the EPEL Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to install some of the packages below you will need to enable the EPEL repository.

Installing in Red Hat Enterprise Linux 6 - 64 Bits::
   
   ## RHEL/CentOS 6 64-Bit ##
   wget http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
   rpm -ivh epel-release-6-8.noarch.rpm

Installing in Red Hat Enterprise Linux 6 - 32 Bits::

   ## RHEL/CentOS 6 32-Bit ##
   wget http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
   rpm -ivh epel-release-6-8.noarch.rpm


Numpy Installation
~~~~~~~~~~~~~~~~~~

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install numpy
    
Matplotlib Installation
~~~~~~~~~~~~~~~~~~~~~~~

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install matplotlib
    
PyEpics Installation
~~~~~~~~~~~~~~~~~~~~

**ATENTION**, PyEpics requires that Epics Base to be correctly installed at your computer and that the environment variable `PYEPICS_LIBCA` is pointing to the correct place.
For informations regarding to Epics Base installation please check `LNLS Wiki - Epics Installation <https://wiki.lnls.br/mediawiki/index.php/SOL:Instala%C3%A7%C3%A3o_da_base_EPICS_Linux>`_

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install pyepics
    
H5PY Installation
~~~~~~~~~~~~~~~~~

Prior to install H5PY some requirements must be filled, please install the required packages with::

    yum install hdf5
    yum install hdf5-devel

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install cython
    pip3.4 install h5py
    
Pillow Installation
~~~~~~~~~~~~~~~~~~~

Pillow is the substitute for PIL (Python Image Library).

To correctly install the lastest version in your Python3.4 environment do::

    easy_install-3.4 Pillow
    
        
Scipy Installation
~~~~~~~~~~~~~~~~~~

Prior to install Scipy some requirements must be filled, please install the required packages with::

    yum install gcc-gfortran
    yum install openblas

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install scipy
    
After install all the dependencies proceed to the `installation guide <installation.html>`_

LMFIT Installation
~~~~~~~~~~~~~~~~~~

Lmfit provides a high-level interface to non-linear optimization and curve fitting problems for Python. 

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install lmfit
    
iPython Installation
~~~~~~~~~~~~~~~~~~~~

Lmfit provides a high-level interface to non-linear optimization and curve fitting problems for Python. 

To correctly install the lastest version in your Python3.4 environment do::

    pip3.4 install ipython
