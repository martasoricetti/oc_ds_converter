# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from abc import ABCMeta, abstractmethod


class DataSource(metaclass=ABCMeta):
    def __init__(self, service: str) -> None:
        self._service = service

    def new(self) -> dict[str, object]:
        return {"date": None, "valid": False, "issn": [], "orcid": []}

    @abstractmethod
    def get(self, resource_id: str) -> object:
        pass

    @abstractmethod
    def mget(self, resources_id: list[str]) -> list[object]:
        pass

    @abstractmethod
    def set(self, resource_id: str, value: object) -> object:
        pass

    @abstractmethod
    def mset(self, resources: dict[str, object]) -> object:
        pass