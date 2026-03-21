# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from oc_ds_converter.oc_idmanager.oc_data_storage.storage_manager import StorageManager
from oc_ds_converter.datasource.redis import RedisDataSource
import fakeredis

class RedisStorageManager(StorageManager):
    """A concrete implementation of the ``StorageManager`` interface that persistently stores
    the IDs validity values within a REDIS database."""

    def __init__(self,  testing=True, config_filepath: str = 'config.ini', **params) -> None:
        """
        Constructor of the ``RedisStorageManager`` class.

        :param database: The name of the database
        :type info_dir: str
        """
        if testing:
            self.testing = True
            self.PROCESS_redis = fakeredis.FakeStrictRedis()
        else:
            self.testing = False
            self.PROCESS_redis = RedisDataSource("PROCESS-DB", config_filepath)
        super().__init__(**params)


    def set_full_value(self, id_name: str, value: dict) -> None:
        """
        It allows to set the counter value of provenance entities.

        :param value: The new counter value to be set
        :type value: dict
        :param id: The id string with prefix
        :type id: str
        :raises ValueError: if ``value`` is neither 0 nor 1 (0 is False, 1 is True).
        :return: None
        """
        id_name = str(id_name)
        if not isinstance(value, dict):
            raise ValueError("value must be dict")
        if not isinstance(self.get_value(id_name), bool):
            id_val = True if value.get("valid") else False
            self.set_value(id_name, id_val)

    def set_value(self, id: str, value: bool) -> None :
        """
        It allows to set a value for the validity check of an id.

        :param value: validity value for the validated id
        :type value: bool
        :param id: The id string with prefix
        :type id: str
        :raises ValueError: if ``value`` is neither 0 nor 1 (0 is False, 1 is True).
        :return: None
        """
        id_name = str(id)
        if not isinstance(value, bool):
            raise ValueError("value must be int boolean")
        validity = 1 if value else 0
        self.PROCESS_redis.set(id_name, validity)


    def set_multi_value(self, list_of_tuples: list) -> None :
        """
        It allows to set a value for the validity check of an id.

        :param list_of_tuples: a list of tuples of ids and booleans (id, value)
        :type list_of_tuples: list
        :return: None
        """
        redis_dict = dict()
        for t in list_of_tuples:
            if t[1] is True:
                redis_dict[t[0]] = 1
            else:
                redis_dict[t[0]] = 0
        if redis_dict:
            self.PROCESS_redis.mset(redis_dict)


    def get_value(self, id: str):
        """
        It allows to read the value of the identifier.

        :param id: The id name
        :type id: str
        :return: The requested id value (True if valid, False if invalid, None if not found).
        """
        id_name = str(id)
        result = self.PROCESS_redis.get(id_name)
        if result:
            result = int(result.decode("utf-8")) if isinstance(result, bytes) else int(result)
            return True if result == 1 else False
        return None

    def del_value(self, id: str) -> None:
        """
        It allows to delete the identifier from the redis db.

        :param id: The id name
        :type id: str
        :return: None
        """
        self.PROCESS_redis.delete(id)


    def delete_storage(self):
        self.PROCESS_redis.flushdb()

    def get_all_keys(self):
        result = [x for x in self.PROCESS_redis.scan_iter('*')]
        if result:
            if isinstance(result[0], bytes):
                result = {x.decode("utf-8") for x in result}
            else:
                result = set(result)
        else:
            result = set()
        return result