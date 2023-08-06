Google News Crawler
===================

A utility to fetch news articles from `Google News`_.

GNC retrieves the latest items from the Google News feeds and stores
them in ElasticSearch_ or on disk.

Written by `Isaac Sijaranamual`_ at the University of Amsterdam/ILPS_.

.. _`Google News`: http://news.google.com/
.. _ILPS: http://ilps.science.uva.nl/
.. _ElasticSearch: http://www.elasticsearch.org/
.. _`Isaac Sijaranamual`: mailto:isaacsijaranamual@gmail.com


Installation
------------

Google News Crawler can be installed with ``pip`` as usual::

    pip install google_news_crawler


Usage
-----

Retrieve news items belonging to the 'science/technology' topic for
the region Botswana from Google News, storing the articles in an
ElasticSearch instance::

    google_news_crawler --datastore=ES --feed="http://news.google.com/news?cf=all&ned=en_bw&output=rss&topic=t&sort=newest"

You would typically want to run a command like the one above in a
``crontab`` to periodically fetch all the items::

    # m h  dom mon dow   command
    01-59/10 * * * * google_news_crawler --log-config=/path/to/gnc/logging.yaml --datastore=ES --feed="http://news.google.com/news?cf=all&ned=en_bw&output=rss&topic=t&sort=newest"

The complete list of usage options can be obtained with the ``--help``
argument::

    google_news_crawler --help


Nota Bene
---------

The store-to-disk backend is still available, but has been dropped as
a dependency because of a license incompatibility, since warc_ is
licensed under the GPL (version 2).

.. _warc: https://pypi.python.org/pypi/warc


TODO
----

* general

  * make user-agent configurable
  * expand documentation

* Elasticsearch backend

  * make all ES related settings configurable
  * update metadata for existing documents instead of skipping them
    entirely
  * improve index mapping for the documents


License
-------

Copyright 2013-2014 Isaac Sijaranamual, University of Amsterdam/ILPS

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this Work or Derivative Works except in compliance with
the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.
