# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC


from abc import ABCMeta


class StorageManager(metaclass=ABCMeta):
    """This is the interface that must be implemented by any Storage manager
    for a particular storage approach. It provides the signatures of the methods
    for string and retrieving data."""

    _headers: dict[str, str]

    def __init__(self, **params: object) -> None:
        """Storage manager constructor."""
        for key in params:
            setattr(self, key, params[key])

        self._headers = {
            "User-Agent": "Identifier Manager / OpenCitations Indexes "
            "(http://opencitations.net; mailto:contact@opencitations.net)"
        }

    def set_value(self, id: str, value: bool) -> None:
        pass

    def set_full_value(self, id: str, value: dict[str, str | bool | object]) -> None:
        pass

    def get_value(self, id: str) -> bool | None:
        pass

    def set_multi_value(self, list_of_tuples: list[tuple[str, bool]]) -> None:
        pass

    def delete_storage(self) -> None:
        pass

    def store_file(self) -> None:
        pass

    def get_all_keys(self) -> list[str]:
        return []

