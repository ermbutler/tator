import logging
import os
import datetime
from copy import deepcopy
from uuid import uuid1
from django.db import connection
import re
import time

logger = logging.getLogger(__name__)

# Indicates what types can mutate into. Maps from type -> to type.
ALLOWED_MUTATIONS = {
    'bool': ['bool', 'enum', 'string'],
    'int': ['int', 'float'],
    'float': ['int', 'float'],
    'enum': ['enum', 'string'],
    'string': ['enum', 'string'],
    'datetime': [ 'string', 'datetime'],
    'geopos': ['geopos'],
    'float_array': ['float_array'],
}

def _get_unique_index_name(entity_type, attribute):
    """ Get a unique index name based on an entity type and supplied attribute """
    type_name_sanitized=entity_type.__class__.__name__.lower()
    entity_name_sanitized=re.sub(r"[^a-zA-Z0-9]","_",entity_type.name).lower()
    attribute_name_sanitized=re.sub(r"[^a-zA-Z0-9]","_",attribute['name']).lower()
    index_name=f"tator_proj_{entity_type.project.id}_{type_name_sanitized}_{entity_name_sanitized}_{attribute_name_sanitized}"
    return index_name

def make_btree_index(entity_type, attribute, psql_type):
    table_name = entity_type._meta.db_table.replace('type','')
    index_name = _get_unique_index_name(entity_type, attribute)
    with connection.cursor() as cursor:
        sql_str=f"""CREATE INDEX CONCURRENTLY {index_name} ON {table_name}
                                 USING btree (CAST(attributes->>'{attribute['name']}' AS {psql_type}))
                                 WHERE project={entity_type.project.id} and meta={entity_type.id}"""
        cursor.execute(sql_str)
        logger.info(sql_str)
def make_bool_index(entity_type, attribute):
    make_btree_index(entity_type, attribute, 'boolean')


def make_int_index(entity_type, attribute):
    make_btree_index(entity_type, attribute, 'integer')

def make_float_index(entity_type, attribute):
    make_btree_index(entity_type, attribute, 'float')

def make_string_index(entity_type, attribute, method='GIN'):
    table_name = entity_type._meta.db_table.replace('type','')
    index_name = _get_unique_index_name(entity_type, attribute)
    with connection.cursor() as cursor:
        sql_str=f"""CREATE INDEX CONCURRENTLY {index_name} ON {table_name}
                                 USING {method} (CAST(attributes->>'{attribute['name']}' AS text) {method.lower()}_trgm_ops)
                                 WHERE project={entity_type.project.id} and meta={entity_type.id}"""
        cursor.execute(sql_str)
        logger.info(sql_str)

def make_datetime_index(entity_type, attribute):
    func_str=f"""CREATE OR REPLACE FUNCTION to_timestamp(text)
                 RETURNS timestamp AS
                $func$
                SELECT CAST($1 as timestamp)
                $func$ LANGUAGE sql IMMUTABLE;"""
    sql_str=f"""CREATE INDEX CONCURRENTLY test ON main_State USING btree (to_timestamp(attributes->>'{attribute['name']}')) WHERE project={entity_type.project.id} AND meta={entity_type.id};"""
    with connection.cursor() as cursor:
        cursor.execute(func_str)
        cursor.execute(sql_str)
        logger.info(sql_str)



def make_geopos_index(entity_type, attribute):
    pass

def make_vector_index(entity_type, attribute):
    pass

class TatorSearch:
    """ Interface for managing psql indices
        There is one index per attribute type.
    """

    index_map = {
        'bool': make_bool_index,
        'int' : make_int_index,
        'float' : make_float_index,
        'enum' : make_string_index,
        'string' : make_string_index,
        'datetime' : make_datetime_index,
        'geopos' : make_geopos_index,
        'float_array' : make_vector_index,
    }

    def list_indices(self, project):
        """ Based on a project id, list all known indices """
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename,indexname,indexdef from pg_indexes where indexname LIKE '{}'".format(f"tator_proj_{project}_%"))
            return cursor.fetchall()

    def delete_project_indices(self, project):
        proj_indices = self.list_indices(project)
        with connection.cursor() as cursor:
            for _,index_name,_ in proj_indices:
                cursor.execute("DROP INDEX CONCURRENTLY IF EXISTS {}".format(index_name))

    def delete_index(self, entity_type, attribute):
        """ Delete the index for a given entity type """
        index_name = _get_unique_index_name(entity_type, attribute)
        with connection.cursor() as cursor:
            cursor.execute("DROP INDEX CONCURRENTLY IF EXISTS {}".format(index_name))

    def is_index_present(self, entity_type, attribute):
        """ Returns true if the index exists for this attribute """
        index_name = _get_unique_index_name(entity_type, attribute)
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename,indexname,indexdef from pg_indexes where indexname = '{}'".format(index_name))
            return bool(cursor.fetchall())

    def create_psql_index(self, entity_type, attribute, flush=False):
        """ Create a psql index for the given attribute """
        index_name = _get_unique_index_name(entity_type, attribute)
        if flush:
            self.delete_index(entity_type, attribute)
        if self.is_index_present(entity_type, attribute):
            logger.info(f"Index '{index_name}' already exists.")
            return False

        index_func = self.index_map.get(attribute['dtype'],None)
        if index_func is None:
            logger.error(f"Index '{index_name}' can't be created with unknown dtype {attribute['dtype']}")
            return False

        index_func(entity_type, attribute)
        return self.is_index_present(entity_type, attribute)

    def create_mapping(self, entity_type, flush=False):
        for attribute in entity_type.attribute_types:
            begin=time.time()
            if self.create_psql_index(entity_type, attribute, flush=flush):
                logger.info(f"Created index {entity_type.name}:{attribute['name']} in {time.time()-begin} seconds.")

    def rename_alias(self, entity_type, related_objects, old_name, new_name):
        """
        Adds an alias corresponding to an attribute type rename. Note that the old alias will still
        exist but can be excluded by specifying fields parameter in query_string queries. Entity
        type should contain an attribute type definition for old_name.

        :param entity_type: *Type object. Should be passed in before updating attribute_type json.
                            Fields attribute_types and attribute_type_uuids will be updated with new
                            name. Entity type will NOT be saved.
        :param old_name: Name of attribute type being mutated.
        :param new_name: New name for the attribute type.
        """
        pass

    def check_mutation(self, entity_type, name, new_attribute_type):
        """
        Checks mutation operation and raises if it is invalid. See `mutate_alias` for argument
        description.
        """
        # Retrieve UUID, raise error if it doesn't exist.
        uuid = entity_type.project.attribute_type_uuids.get(name)
        if uuid is None:
            raise ValueError(f"Could not find attribute name {name} in entity type "
                             f"{type(entity_type).__name__} ID {entity_type.id}")

        # Find old attribute type and create new attribute type.
        for idx, attribute_type in enumerate(entity_type.attribute_types):
            if attribute_type['name'] == name:
                replace_idx = idx
                old_mapping_type = _get_alias_type(attribute_type)
                old_mapping_name = f'{uuid}_{old_mapping_type}'
                old_dtype = attribute_type['dtype']
                break
        else:
            raise ValueError(f"Could not find attribute name {name} in entity type "
                             f"{type(entity_type).__name__} ID {entity_type.id}")

        new_dtype = new_attribute_type["dtype"]
        if new_dtype not in ALLOWED_MUTATIONS[old_dtype]:
            raise RuntimeError(f"Attempted mutation of {name} from {old_dtype} to {new_dtype} is "
                                "not allowed!")

        return uuid, replace_idx, old_mapping_name

    def mutate_alias(self, entity_type, name, new_attribute_type, mod_type, new_style=None):
        """
        Sets alias to new mapping type.

        :param entity_type: *Type object. Should be passed in before updating attribute_type json.
                            Field attribute_types will be updated with new dtype and style. Entity
                            type will not be saved.
        :param name: Name of attribute type being mutated.
        :param new_attribute_type: New attribute type for the attribute being mutated.
        :param mod_type: The type of modification to perform on the attribute: `update` will add
                         missing keys and update values of existing keys; `replace` will replace the
                         definition with `new_attribute_type`, which will result in deletion of
                         existing keys if they are not present in the new definition.
        :param new_style: [Optional] New display style of attribute type. Used to determine if
                          string attributes should be indexed as keyword or text.
        :returns: Entity type with updated attribute_types.
        """
        return entity_type

    def delete_alias(self, entity_type, name):
        """
        Deletes existing alias.

        :param entity_type: *Type object.
        :param name: Name of attribute type being deleted.
        :returns: Entity type with updated attribute_types.
        """
        return entity_type
