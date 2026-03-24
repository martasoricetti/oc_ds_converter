# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import os.path
import pathlib
import sqlite3

from oc_ds_converter.oc_idmanager.oc_data_storage.storage_manager import StorageManager


class SqliteStorageManager(StorageManager):
    """A concrete implementation of the ``StorageManager`` interface that persistently stores
    the IDs validity values within a SQLite database."""

    con: sqlite3.Connection
    cur: sqlite3.Cursor
    storage_filepath: str

    def __init__(self, database: str | None = None, **params: object) -> None:
        """
        Constructor of the ``SqliteStorageManager`` class.

        :param database: The name of the database
        :type info_dir: str
        """
        super().__init__(**params)
        sqlite3.threadsafety = 3
        if database and os.path.exists(database):
            self.con = sqlite3.connect(database=database)
            self.storage_filepath = database
        elif database and not os.path.exists(database):
            if not os.path.exists(os.path.abspath(os.path.join(database, os.pardir))):
                pathlib.Path(os.path.abspath(os.path.join(database, os.pardir))).mkdir(parents=True, exist_ok=True)
            self.con = sqlite3.connect(database=database)
            self.storage_filepath = database
        else:
            new_path_dir = os.path.join(os.getcwd(), "storage")
            if not os.path.exists(new_path_dir):
                os.makedirs(new_path_dir)
            new_path_db = os.path.join(new_path_dir, "id_valid_dict.db")
            self.con = sqlite3.connect(database=new_path_db)
            self.storage_filepath = new_path_db

        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS info(
            id TEXT PRIMARY KEY,
            value INTEGER)""")

    def set_full_value(self, id: str, value: dict[str, str | bool | object]) -> None:
        """
        It allows to set the counter value of provenance entities.

        :param value: The new counter value to be set
        :type value: dict
        :param id: The id string with prefix
        :type id: str
        :raises ValueError: if ``value`` is neither 0 nor 1 (0 is False, 1 is True).
        :return: None
        """
        id_name = str(id)
        if not isinstance(value, dict):
            raise ValueError("value must be dict")
        if not isinstance(self.get_value(id_name), bool):
            valid = value.get("valid")
            if isinstance(valid, bool):
                self.set_value(id_name, valid)

    def set_value(self, id: str, value: bool) -> None:
        """
        It allows to set a value for the validity check of an id.

        :param value: The new counter value to be set
        :type value: bool
        :param id: The id string with prefix
        :type id: str
        :raises ValueError: if ``value`` is neither 0 nor 1 (0 is False, 1 is True).
        :return: None
        """
        id_name = str(id)
        if not isinstance(value, bool):
            raise ValueError("value must be boolean")
        validity = 1 if value else 0
        id_val = (id_name, validity)
        self.cur.execute("INSERT OR REPLACE INTO info VALUES (?,?)", id_val)
        self.con.commit()

    def set_multi_value(self, list_of_tuples: list[tuple[str, bool]]) -> None:
        """
        It allows to set a value for the validity check of an id.

        :param value: The new counter value to be set
        :type value: bool
        :param id: The id string with prefix
        :type id: str
        :raises ValueError: if ``value`` is neither 0 nor 1 (0 is False, 1 is True).
        :return: None
        """
        sqlite_list_copy: list[tuple[str, int]] = []
        for t in list_of_tuples:
            if t[1] is True:
                sqlite_list_copy.append((t[0], 1))
            else:
                sqlite_list_copy.append((t[0], 0))
        self.cur.executemany("INSERT OR REPLACE INTO info VALUES (?,?)", sqlite_list_copy)
        self.con.commit()

    def get_value(self, id: str) -> bool | None:
        """
        It allows to read the value of the identifier.

        :param id: The id name
        :type id: str
        :return: The requested id value (True if valid, False if invalid, None if not found).
        """
        id_name = str(id)
        result = self.cur.execute(f"SELECT value FROM info WHERE id='{id_name}'")
        rows = result.fetchall()
        if len(rows) == 1:
            value = rows[0][0]
            return value == 1
        elif len(rows) == 0:
            return None
        else:
            raise Exception("There is more than one counter for this id. The database is broken")

    def delete_storage(self) -> None:
        if os.path.exists(self.storage_filepath):
            try:
                self.con.close()
                os.remove(self.storage_filepath)
            except Exception:
                os.remove(self.storage_filepath)

    def get_all_keys(self) -> list[str]:
        ids = [row[0] for row in self.cur.execute("SELECT id FROM info")]
        return ids
