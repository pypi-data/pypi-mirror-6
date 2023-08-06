Installation instructions for Ragout
====================================


Availability
------------
Ragout is tested under Mac Os and Linux. While it *should* work
under Windows, we do not provide official support yet.


Build requirements
------------------
* Python 2.7 (with developer headers)
* C++ compiler with C++0x support (GCC 4.6+ or proper version of Clang)
* Cmake (for building Sibelia)
* Some standard POSIX utilities, such as *wget* or *tar*


Runtime depenencies
-------------------

* Python 2.7
* biopython [http://biopython.org]
* networkx 1.8+ [http://networkx.github.io]
* Sibelia [https://github.com/bioinf/Sibelia]


You can install Ragout as a Python package, which is recommended.
Alternatively, you can build and run it from a source directory.

Buildng Ragout requires Python headers, which are distributed
separate from the main package in some OS. For instance, Ubuntu
users should check that package "python-dev" is installed.


Installation from PyPI
----------------------

The easies way to install Ragout is to use Python package index database:

	pip install ragout

Note, that this may require superuser privileges:

	sudo pip install ragout

If you do not have *pip* installed, you can install it from here:
http://www.pip-installer.org/ 


Package installation (recommended)
----------------------------------

To install Ragout as a Python package, run:

	[sudo] python2.7 setup.py install

If you don't have permission to install software on your system, you can 
install into another directory using the --user, --prefix, or --home flags to setup.py.

	python2.7 setup.py install --user
	or
	python2.7 setup.py install --prefix=~/.local
	or
	python2.7 setup.py install --home=~

If you didn't install in the standard Python site-packages directory you will 
need to set your PYTHONPATH variable to the alternate location. 
See http://docs.python.org/2/install/index.html#search-path for further details.

After installation with custom prefix you may need to add the corresponding 
"bin" directory to your executable path (to run Ragout from any working directory). 
For example, if your prefix was "~/.local", run:

	export PATH=$PATH:~/.local/bin

setup.py script also will install all necessary Python dependencies, if neded.
After installation process you can test your installation by running:

	run-ragout --help

If it works, you can try Ragout on the provided examples (refer to USAGE.md for this)


Using without installation
--------------------------

To build Ragout inside the source directory, run:

	python2.7 setup.py inplace

In this case, you should manually install all dependencies using *pip*
or your OS-specific package manager:

	pip install biopython networkx
	or
	sudo apt-get install biopython networkx


Sibelia
-------

Ragout requires Sibelia for synteny block decomposition.
To instal it, run:

	[sudo] scripts/install-sibelia.py [--prefix=your_prefix]

Or, if you have installed Ragout with *pip* and do not have
"scripts" directory:

	curl <path> -o - | [sudo] python2.7 [- --prefix=your_prefix]

Do not forget that "your_prefix/bin" folder also should be in your PATH.
Alternatively, you can set SIBELIA_INSTALL variable to directory
containing *Sibelia* excecutable.