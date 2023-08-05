##########
blogtopoid
##########

Contents:

.. toctree::
   :maxdepth: 2

   manual
   templates
   api

Quickstart
==========

Install blogtopoid and dependencies::

    python setup.py install

chdir to an empty directory and run::

    blogtopoid --quickstart

This will query for configuration options,
and deploy an example post and basic templates.

Edit the templates to your liking, write real
posts, and run::

    blogtopoid

``outputdir/`` now contains the generated HTML.
Put all files into a web accessible directory.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

