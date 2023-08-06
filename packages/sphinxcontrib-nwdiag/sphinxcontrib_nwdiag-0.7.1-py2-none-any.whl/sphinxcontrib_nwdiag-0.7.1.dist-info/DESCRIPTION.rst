This package contains the nwdiag Sphinx extension and rackdiag Sphinx extension.

.. _Sphinx: http://sphinx.pocoo.org/
.. _nwdiag: http://blockdiag.com/en/nwdiag/

This extension enable you to insert network diagrams into your Sphinx document.
Following code is sample::

   .. nwdiag::

      diagram {
        network {
          web01; web02;
        }
        network {
          web01; web02; db01;
        }
      }

And insert rack structure diagrams::

   .. rackdiag::

      diagram {
        rackheight = 12;

        1: UPS [height = 3];
        4: DB Server (Master)
        5: DB Server (Mirror)
        7: Web Server (1)
        8: Web Server (1)
        9: Web Server (1)
        10: LoadBalancer
      }


This module needs nwdiag_.


