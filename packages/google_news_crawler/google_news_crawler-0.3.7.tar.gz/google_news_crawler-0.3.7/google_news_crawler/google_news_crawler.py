#!/usr/bin/env python

"""Google News Crawler

Retrieves news articles from Google News' feed and stores them in
ElasticSearch or on disk.

Usage:
  google_news_crawler --feed=FEED --datastore=DATASTORE [options]

Options:
  -f=FEED, --feed=FEED   Name/url of the Google News feed to crawl
  -d=DS, --datastore=DS  Datastore backend to use, options are: FS, ES
  --log-config=FNAME     YAML file containing the logging configuration
                         [default: logging.yaml]
  --force-download       Download articles even if we already have them
  -h, --help             This help.
  -v, --version          Print version number
"""

from logging.config import dictConfig

import yaml
from docopt import docopt

from . import __version__
from .gnc import GoogleNewsCrawler


def setup_logging(fname):
    with open(fname) as f:
        dictConfig(yaml.load(f))


def main(argv=None):
    if argv is None:
        args = docopt(__doc__, version=__version__)
    else:
        args = docopt(__doc__, version=__version__, argv=argv)

    setup_logging(args['--log-config'])

    feed_name = args['--feed']
    ds_name = args['--datastore']

    force_download = args['--force-download']

    # TODO: DSFactory anyone?
    if ds_name == 'FS':
        from .datastore.fs_datastore import FileSystemDatastore
        output_dir = 'output'
        ds = FileSystemDatastore(output_dir)
    elif ds_name == 'ES':
        from .datastore.es_datastore import ElasticSearchDatastore
        index = 'docdocdocs'
        ds = ElasticSearchDatastore(index, create_index=False)
    else:
        from .datastore import UnknownDatastoreException
        raise UnknownDatastoreException(ds_name)

    crawler = GoogleNewsCrawler(feed_name, ds, force_download=force_download)
    crawler.process_feed()


if __name__ == '__main__':
    main()
