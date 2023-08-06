This package contains the blockdiag Sphinx extension.

.. _Sphinx: http://sphinx.pocoo.org/
.. _blockdiag: http://blockdiag.com/en/blockdiag/

This extension enable you to insert block diagrams in your Sphinx document.
Following code is sample::

   .. blockdiag::

      diagram {
        A -> B -> C;
             B -> D;
      }


This module needs blockdiag_.


