# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to elasticsearch
using the Elasticsearch API

**Backend name:** ``elasticsearch``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``connection_kwargs``
      - ``dict``
      - ``REQUIRED`` Connection kwargs passed to the `elasticsearch client  <https://elasticsearch-py.readthedocs.io/en/latest/api.html#elasticsearch>`_
    * - ``index.name``
      - ``str``
      - ``REQUIRED`` The index to output the content.
    * - ``index.mapping``
      - ``str``
      - Path to a yaml file which defines the mapping for the index
    * - ``namespace``
      - ``str``
      - Can be used by downstream processors to separate outputs to different indices or clusters

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: elasticsearch
              connection_kwargs:
                hosts: ['host1','host2']
              index:
                name: 'assets-2021-06-02'
              namespace: assets
"""
__author__ = 'Richard Smith'
__date__ = '01 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from .base import OutputBackend
from elasticsearch import Elasticsearch
from asset_scanner.core.utils import load_yaml


class ElasticsearchOutputBackend(OutputBackend):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        index_conf = kwargs['index']

        self.es = Elasticsearch(**kwargs['connection_kwargs'])
        self.index_name = index_conf['name']
        self.pipeline_conf = kwargs.get('pipeline', None)

        # Create the index, if it doesn't already exist
        if index_conf.get('mapping'):
            if not self.es.indices.exists(self.index_name):
                mapping = load_yaml(index_conf.get('mapping'))
                self.es.indices.create(self.index_name, body=mapping)

    def export(self, data, **kwargs):

        index_kwargs = {
            'index': self.index_name,
            'id': data['id'],
            'body': {
                'doc': data['body'],
                'doc_as_upsert': True
            }
        }

        self.es.update(**index_kwargs)