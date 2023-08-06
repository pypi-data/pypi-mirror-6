.. checklists_scrapers documentation master file, created by
   sphinx-quickstart on Thu Jul  4 08:53:46 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to checklists_scrapers' documentation!
==============================================
Checklists_scrapers is a series of scrapers that can be used to download
records from various on-line databases available for recording bird
observations. While the databases allow records to be exported the scrapers are
designed to create feeds containing the most recently added checklists. The
scrapers all use the same :doc:`format <format>` for the downloaded data so the
aggregated data can easily be analyzed. Scrapers are available for the
following databases:

.. include:: install.rst
.. include:: scraping.rst

.. toctree::
   :maxdepth: 1

   scrapers/ebird
   scrapers/worldbirds

Resources
---------

* The checklists_scrapers project on `Github <http://github.com/StuartMacKay/checklists_scrapers/>`_
* Information on the `Scrapy framework <http://scrapy.org>`_
