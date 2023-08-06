import json
import logging
from urlparse import urljoin

import requests
from elasticmodels import settings
from pyelasticsearch import ElasticSearch


logger = logging.getLogger(__name__)


class Indexer(object):
    """
    This class functions to generate ES compatible mappings

    USAGE:
    1. Call Indexer.generate_index(MODEL) (per resource)
        >> settings.ELASTICSEARCH_TO_INDEX (list) should contain them all
    2. Call self.create_indexes() to send everything to ES
    """

    def __init__(self, *args, **kwargs):
        """
        1. Sets up the connection
        2. Contains the field mapping
        3. Sets empty list that will receive the indexes
        """
        self.connection = ElasticSearch(settings.ELASTICSEARCH_HOST)

        # The mapping for django fields to ES
        self.fields = {
            'AutoField': 'long',
            'BigIntegerField': 'long',
            'BinaryField': 'sring',
            'BooleanField': 'boolean',
            'CharField': 'string',
            'CommaSeparatedIntegerField': 'string',
            'DateField': 'date',
            'DateTimeField': 'date',
            'DecimalField': 'string',
            'EmailField': 'string',
            'FileField': 'string',
            'FileField': 'string',
            'FilePathField': 'string',
            'FloatField': 'float',
            'FloatField': 'float',
            'ForeignKey': 'string',
            'ImageField': 'string',
            'IntegerField': 'integer',
            'NullBooleanField': 'string',
            'PositiveIntegerField': 'long',
            'PositiveSmallIntegerField': 'integer',
            'SlugField': 'string',
            'SmallIntegerField': 'integer',
            'TextField': 'string',
            'TimeField': 'time',
            'URLField': 'string',
        }
        self.indexes = []  # Contains all the indexes

    def map_django_to_es_property(self, field_type):
        """
        Tries to match the given field type to a field type supported
        by ES

        Args:
            field_type: string - The Django field type to match
        Returns:
            string - The corresponding field type in ES
        """
        try:
            mapped = self.fields[field_type]
        except KeyError:
            raise KeyError('Invalid field type: {0}'.format(field_type))
        return mapped

    def generate_index(self, resource):
        """
        Generates the mapping DICT and appends it to self.indexes

        Args:
            resource: django.db.models.base.ModelBase - Resource to generate an
                                                        index for
        """
        fields = resource._meta.fields
        index = {
            resource.__name__.lower(): {"properties": {}}
        }

        properties = index[resource.__name__.lower()]['properties']

        for item in fields:
            # If an item is found in the CUSTOM_TYPES dict
            #   >> Use that property instead of trying to map it
            if item.name in settings.ELASTICSEARCH_CUSTOM_TYPES:
                es_property = settings.ELASTICSEARCH_CUSTOM_TYPES[item.name]
            else:
                # Map the given item to a property dict
                field_type = self.map_django_to_es_property(
                    resource._meta.get_field(item.name).get_internal_type())
                es_property = {'type': field_type}

            properties.update({
                item.name: es_property,
            })

        # Custom fields that are not present on the model can be added via
        # the ELASTICSEARCH_NON_MODEL_FIELDS list
        #   >> EXAMPLE LIST ITEM:
        #       {'snippet': {'type': 'string'}}
        for item in settings.ELASTICSEARCH_NON_MODEL_FIELDS:
            properties.update(item)
        self.indexes.append(index)

    def create_indexes(self, delete=True):
        """
        Sends the indexes in self.indexes to ES

        Args:
            delete: boolean - If delete is set to True, we wipe the current
                              index. Else, we try to merge the index
        """
        for index in self.indexes:
            try:
                mapping = self.connection.get_mapping(index.keys()[0])

                # Send delete as False if you want to try and merge the
                # index
                if mapping and delete:
                    self.delete_index(index.keys()[0])
            except Exception as e:
                logger.debug(
                    'An error occurred whilst retrieving/deleting a mapping')
                logger.exception(e)

            data = {
                    "mappings": {index.keys()[0]: index}
            }
            requests.put(
                urljoin(settings.ELASTICSEARCH_HOST, index.keys()[0]),
                data=json.dumps(data)
            )

    def delete_index(self, resource):
        """
        Deletes the given resource mapping / data

        Args:
            resource: django.db.models.base.ModelBase - The given resource to
                                                        remove the given
                                                        mapping and data
        """
        return requests.delete(
            urljoin(settings.ELASTICSEARCH_HOST, resource))

