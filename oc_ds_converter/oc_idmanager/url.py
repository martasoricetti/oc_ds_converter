# SPDX-FileCopyrightText: 2023-2024 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC


import urllib.parse
from time import sleep

import validators
from oc_ds_converter.oc_idmanager import *
from oc_ds_converter.oc_idmanager.base import IdentifierManager
from requests import ReadTimeout, get
from requests.exceptions import ConnectionError


class URLManager(IdentifierManager):
    """This class implements an identifier manager for url identifier"""

    def __init__(self, data={}, use_api_service=True):
        """URL manager constructor."""
        super(URLManager, self).__init__()
        self._use_api_service = use_api_service
        self._p = "url:"
        self._data = data
        self._scheme_https = "https://"
        self._scheme_http = "http://"

    def is_valid(self, url, get_extra_info=False):
        url = self.normalise(url, include_prefix=True)
        if url is None:
            return False
        else:
            if url not in self._data or self._data[url] is None:
                if get_extra_info:
                    info = self.exists(url, get_extra_info=True)
                    self._data[url] = info[1]
                    return (info[0] and self.syntax_ok(url)), info[1]
                self._data[url] = dict()
                self._data[url]["valid"] = True if (self.syntax_ok(url) and self.exists(url)) else False
                return self._data[url].get("valid")

            if get_extra_info:
                return self._data[url].get("valid"), self._data[url]
            return self._data[url].get("valid")

    def normalise(self, id_string, include_prefix=False):
        id_string = str(id_string)
        url_string = id_string.strip()
        if url_string.startswith(self._p):
            url_string = url_string[len(self._p):]
        if url_string.endswith("/"):
            url_string = url_string[:-1]
        if url_string.startswith("https://"):
            url_string = url_string[len("https://"):]
        elif url_string.startswith("http://"):
            url_string = url_string[len("http://"):]
        if url_string.startswith("www."):
            url_string = url_string[len("www."):]
        try:
            url_string = urllib.parse.quote(url_string, safe="%/:=&?~#+!$,;'@()*[]")
            return "%s%s" % (self._p if include_prefix else "", url_string)
        except:
            # Any error in processing the URL will return None
            return None

    def syntax_ok(self, id_string):
        if id_string.startswith(self._p):
            id_string = id_string[len(self._p):]
        return True if validators.url(self._scheme_https + id_string) else False

    def exists(self, url_full, get_extra_info=False, allow_extra_api=None):
        valid_bool = True
        if self._use_api_service:
            url = self.normalise(url_full)
            if url is not None:
                variations = [
                    f"https://www.{url}",
                    f"https://{url}",
                    f"http://www.{url}",
                    f"http://{url}"
                ]

                for variation in variations:
                    tentative = 3
                    while tentative:
                        tentative -= 1
                        try:
                            r = get(variation,
                                headers=self._headers,
                                timeout=30,
                            )
                            if r.status_code == 200:
                                if get_extra_info:
                                    return True, {"valid": True}
                                return True
                            elif r.status_code == 404:
                                if get_extra_info:
                                    return False, {"valid": False}
                                return False

                        except ReadTimeout:
                            # Do nothing, just try again
                            pass
                        except ConnectionError:
                            # Sleep 5 seconds, then try again
                            sleep(5)

                valid_bool = False

            else:
                if get_extra_info:
                    return False, {"valid": False}
                return False
        if get_extra_info:
            return valid_bool, {"valid": valid_bool}
        return valid_bool

    def extra_info(self, api_response, choose_api=None, info_dict={}):
        result = {}
        result["valid"] = True
        return result
