Download & Install
=========================

Here you'll find all the necessary explanations for installing OpenCobolIDE.


Requirements:
----------------
OpenCobolIDE depends on the following packages

    - Python 2.7 or Python 3
    - PyQt4
    - OpenCobol
    - pyqode.core
    - pyqode.widgets
    - pygments >= 1.6
    - chardet (chardet2 if you are using python3)

Installation
------------------

GNU/Linux
++++++++++

If you are on Ubuntu 13.10 or drivatives, you can use the ppa to easily
install OpenCobolIDE::

    sudo apt-add-repository ppa:open-cobol-ide/stable
    sudo apt-get update
    sudo apt-get install open-cobol-ide

Otherwise you will have to install from source:

1) Install OpenCobol and PyQt4

.. code-block:: bash

    sudo apt-get install python-qt open-cobol

.. note:: If you want to use python 3, you need to install python3-pyqt4
          instead of python-qt.

2) Install OpenCobolIDE

Using pip or easy_install::

    sudo pip install OpenCobolIDE

From source::

    cd /path/to/source
    sudo python setup.py install

.. note:: Replace *python* by *python3* to install OpenCobolIDE for Python 3.


Both methods will install a desktop entry on your system.

An **open-cobol-ide** entry should appear in the development category. If the
entry does not appear, you can always open a terminal and type *open-cobol-ide* to run the IDE.


Windows
++++++++++++

Please use the Windows Installer available `here`_.

.. _`here`: https://github.com/OpenCobolIDE/OpenCobolIDE/releases


.. note:: Installation from source is possible but you need to install all
          requirements yourself and run the OpenCobolIDE.pyw from the *extracted
          archive* or *git repository* without actually installing OpenCobolIDE
          (**do not run** *setup.py install* on windows).