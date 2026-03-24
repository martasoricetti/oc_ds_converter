# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC


from __future__ import annotations

from json import loads
from time import sleep

from bs4 import BeautifulSoup
from requests import ReadTimeout, get
from requests.exceptions import ConnectionError


def call_api(
    url: str, headers: dict[str, str], r_format: str = "json"
) -> dict[str, object] | BeautifulSoup | None:
    tentative = 3
    while tentative:
        tentative -= 1
        try:
            r = get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                r.encoding = "utf-8"
                if r_format == "json":
                    return loads(r.text)  # type: ignore[no-any-return]
                return BeautifulSoup(r.text, "xml")
            if r.status_code == 404:
                return None
        except ReadTimeout:
            pass
        except ConnectionError:
            sleep(5)
    return None


def extract_info(
    api_response: dict[str, object],
    choose_api: str | None = None,
    orcid_doi_filepath: str = "",
) -> dict[str, bool | object]:
    from oc_ds_converter.oc_idmanager.metadata_manager import MetadataManager

    info_dict: dict[str, bool | object] = {"valid": True}
    metadata_manager = MetadataManager(
        metadata_provider=choose_api,  # type: ignore[arg-type]
        api_response=api_response,  # type: ignore[arg-type]
        orcid_doi_filepath=orcid_doi_filepath,
    )
    metadata = metadata_manager.extract_metadata()
    if metadata:
        info_dict.update(metadata)
    return info_dict