This package contains the seqdiag Sphinx extension.

.. _Sphinx: http://sphinx.pocoo.org/
.. _seqdiag: http://blockdiag.com/en/seqdiag/

This extension enable you to insert sequence diagrams in your Sphinx document.
Following code is sample::

   .. seqdiag::

      diagram {
        browser => webserver => database;
      }


This module needs seqdiag_.


