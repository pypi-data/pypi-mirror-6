import logging
import json
from pkg_resources import resource_string

from elasticsearch import Elasticsearch

from base_datastore import BaseDatastore


LOG = logging.getLogger(__name__)


class ElasticSearchDatastore(BaseDatastore):
    """Elasticsearch backend"""
    def __init__(self, index, hosts=None, doc_type='gnc_rss',
                 create_index=False):
        if hosts is None:
            hosts = [{'host': 'localhost', 'port': 9200}]
        elif isinstance(hosts, str):
            host_parts = zip(('host', 'port'), hosts.split(':'))
            hsh = {k: v for k, v in host_parts}
            hosts = [hsh]

        self.es = Elasticsearch(hosts)
        self.index = index
        self.doc_type = doc_type
        if create_index:
            self.es.indices.create(self.index)

    def contains(self, url):
        return self.es.exists(self.index, url, self.doc_type)

    def store(self, data, url, **kwargs):
        document = {
            'url': url,
            'raw': data
        }

        document.update(kwargs)

        self.es.index(self.index, self.doc_type, document, url)
