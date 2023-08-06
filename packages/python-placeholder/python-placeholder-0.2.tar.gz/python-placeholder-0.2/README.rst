*Simple module for creating placeholder images*


install by 

::

	$ pip install python-placeholder


Example:
=========

.. code:: python

        from placeholder import PlaceHolderImage
        img = PlaceHolderImage(width = 300, height = 200, path = 'placeholder.png')
        img.save_image()



Known bugs:
============

- if you do not provide absolute path to font to PlaceHolderImage the default font used will have very small size.

- if you get something like The _imagingft C module is not installed, look here https://stackoverflow.com/questions/4011705/python-the-imagingft-c-module-is-not-installed

Run tests:
==========

You can run the testsuite with the following command::

    python -m unittest tests

Or use tox_ to test against all supported python versions.

.. _tox: https://testrun.org/tox/latest/
