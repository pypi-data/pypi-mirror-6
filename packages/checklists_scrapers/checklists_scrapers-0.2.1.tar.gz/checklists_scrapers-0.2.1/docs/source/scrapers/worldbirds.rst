==========
WorldBirds
==========

The scraper for WorldBirds scrapes the web application pages so you need an
account to extract the data. The data is generally available for download but
scraping pages makes it easier to obtain the most recently added checklists.

The scraper is run using the crawl command::

    scrapy crawl worldbirds -a username=<username> -a password=<password> -a country=<iso code>

where:

+----------+-------------------------------------------------------------------+
| username | is the username for your WorldBirds account.                      |
+----------+-------------------------------------------------------------------+
| password | is the password for your WorldBirds account.                      |
+----------+-------------------------------------------------------------------+
| country  | is a two-letter country code (ISO 3166) that is used to identify  |
|          | the database to access, see the list of supported databases       |
|          | below.                                                            |
+----------+-------------------------------------------------------------------+

There is a separate web application for each country in the Worldbirds network
so you will need separate accounts for each geographical region or country you
want to extract data from.

Most of the WorldBirds databases are accessed with a URL that takes the
general form www.worldbirds.org/v3/<country>.php. Exceptions are the databases
for Africa where countries are grouped into regions, e.g. East Africa and those
for Iberia which are hosted at birdlaa5.memset.net/. The country code makes it
easier to specify which database to use.

Supported Databases
===================

The network of databases hosted by WorldBirds covers some 28 geographical
areas and countries. All the databases use the same version of the web
application for access so the scraper should be able to download checklists
from any of them. Databases it has been specifically tested with include:

========   ====  ===
Country    Code  URL
========   ====  ===
Portugal   pt    `<http://birdlaa5.memset.net/worldbirds/portugal.php>`_
========   ====  ===

Resources
---------

Information on WorldBirds can be found at http://www.worldbirds.org/mapportal/worldmap.php

