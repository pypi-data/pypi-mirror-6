pybtsync
========

tl;dr: A Python module for the BitTorrent Sync API.

This module enables the use of the BitTorrent Sync API through Python. Long term objective it to provide different levels of wrapping to the API. Currently the module only behaves as a thin library with added nicities (see `documentation <http://pybtsync.readthedocs.org/>`_)

BitTorrent Sync
---------------

`BitTorrent Sync <http://www.bittorrent.com/sync>`_  by `BitTorrent, Inc <http://www.bittorrent.com/>`_ is a proprietary peer-to-peer file synchronization tool available for Windows, Mac, Linux, Android, iOS and BSD. It can sync files between devices on a local network, or between remote devices over the Internet via secure, distributed P2P technology. [1]_


Documentation
=============

`Read the Docs <http://pybtsync.readthedocs.org/>`_


Dependencies
============

Below is the list of software which this 

- `BitTorrent sync API key <http://www.bittorrent.com/sync/developers>`_ - `Proprietary TOS <http://www.bittorrent.com/legal/eula>`_
- `Python (2 or 3) <http://www.python.org/download/>`_  - `GPL compatible <http://docs.python.org/3.3/license.html>`_
- `Python request module <http://docs.python-requests.org/en/latest/>`_ - `Apache 2.0 <https://github.com/kennethreitz/requests/blob/master/LICENSE>`_



Installation
============

PyPI
---------

Using the python package manager is the easiest way to get the module going:

::

   > pip install pybtsync
   
::

   > easy_install pybtsync
   



Trunk
---------

To get the latest code you can clone this Github repository and run the setup script manually.

::

   > git clone https://github.com/tiagomacarios/pybtsync.git
   > cd pybtsync
   > python setup.py



References
==========

.. [1] http://en.wikipedia.org/wiki/BitTorrent_Sync