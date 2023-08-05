file2py
=======

.. image:: https://travis-ci.org/kAlmAcetA/file2py.png?branch=master   :target: https://travis-ci.org/kAlmAcetA/file2py
   image alt

Introduction
============

Introduction **file2py** is a module that helps to handle of conversion
binary (as well as text) files to python's source file. Simply embed it
base64. Supports adding/deleting files, templates that facilitate the
further use. It comes with command line tool ``file2py`` and predefined
*templates* like qt, pyside, pyqt.

Installation
============

You can use pip:

::

    sudo pip install file2py

or directly from Github

::

    sudo pip install git+https://github.com/kAlmAcetA/file2py.git

or manually

::

    git clone https://github.com/kAlmAcetA/file2py.git
    cd file2py
    python setup.py install

Usage
=====

Generating
----------

To convert file to py simply specified target file with **-f** option
and files to add:

::

    file2py -f my_first.py some.jpg some.png

There is alias image2py which do the pretty mch the same:

::

    image2py -f my_second.py some.jpg some.png

If target file exists and it is result of file2py, all converted files
will be appended, otherwise an error will occur.

::

    image2py -f my_first.py some_other_file.jpg

    **Warning**: Files with the same name will be overwritten, instead
    of append.

By default ``BasicTemplate`` will be used. With **-t** option you can
choose one of:

-  pyside (add imports and function helpers PySide)
-  pyqt (add imports and function helpers PyQt4)
-  qt (combined two above with fallbacks)
-  basic

For example:

::

    image2py -t qt -f icons.py small.png, mini.ico

Using results
-------------

::

    image2py -f my_imgs.py one.jpg two.png three.gif

.. code:: python

    >>> import my_imgs
    >>> dir(my_imgs)
    ['__builtins__', '__doc__', '__file__', '__name__', '__package__', 'base64', 'data', 'get_data', 'get_decoded', 'list_files', 'template']
    >>> my_imgs.list_files()
    ['one.jpg', 'three.gif', 'two.png']
    >>> my_imgs.get_data('one.jpg') #get file's data (base64 encoded)
    # some base64 data
    >>> my_imgs.get_encoded('one.jpg') #get file's data (raw, base64 decoded)
    # some raw data
    >>> my_imgs.template #holds used template
    'BasicTemplate'
    >>> my_imgs.data #holds data dict

    {'one.jpg': 'base64 data', 'three.gif': 'base64 data', 'two.png': 'base64 data'}

Qt, PySide, PyQt templates provide additional functions:

-  ``getAsQByteArray(filename)`` returns data as QtCore.QByteArray
   object
-  ``getAsQPixmap(filename)`` returns data as QtGui.QPixmap object
-  ``getAsQIcon(filename)`` returns data as QtGui.QIcon object
-  ``getAsQImage(filename)`` returns data as QtGui.QImage object

file2py as a module
===================

**file2py** provide two objects:

1. ``Converter``
2. ``templates`` (submodule contaning ``BasicTemplate``, ``QtTemplate``, ...)

All templates should should extend ``BasicTemplate``. For more information see docstrings:). 

Contributing
============

1. Fork https://github.com/kAlmAcetA/file2py
2. Improve
3. Pull request

Todo
====

* more tests
* more templates
* add *delete* to command line tool


License
=======

MIT
