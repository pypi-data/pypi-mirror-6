This package contains the actdiag Sphinx extension.

.. _Sphinx: http://sphinx.pocoo.org/
.. _actdiag: http://blockdiag.com/en/actdiag/

This extension enable you to insert activity diagrams in your Sphinx document.
Following code is sample::

   .. actdiag::

      diagram {
        A -> B -> C -> D;

        lane {
          A; B;
        }
        lane {
          C; D;
        }
      }


This module needs actdiag_.


