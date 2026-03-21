# SPDX-FileCopyrightText: 2023-2024 Arcangelo Massari <arcangelo.massari@unibo.it>
# SPDX-FileCopyrightText: 2024 Arianna Moretti <arianna.moretti4@unibo.it>
#
# SPDX-License-Identifier: ISC


import re
from re import match, sub

from oc_ds_converter.oc_idmanager.base import IdentifierManager


class ISSNManager(IdentifierManager):
    """This class implements an identifier manager for issn identifier"""

    def __init__(self, data={}):
        """ISSN manager constructor."""
        super(ISSNManager, self).__init__()
        self._p = "issn:"
        self._data = data

    def is_valid(self, id_string, get_extra_info=False):
        issn = self.normalise(id_string, include_prefix=True)
        if issn is None:
            return False
        else:
            if issn not in self._data or self._data[issn] is None:
                self._data[issn] = {"valid":self.check_digit(issn) and self.syntax_ok(issn)}
                return (
                    self.syntax_ok(issn)
                    and self.check_digit(issn)
                )
            return self._data[issn].get("valid")

    def normalise(self, id_string, include_prefix=False):
        try:
            issn_string = sub("[^X0-9]", "", id_string.upper())
            return "%s%s-%s" % (
                self._p if include_prefix else "",
                issn_string[:4],
                issn_string[4:8],
            )
        except:  # Any error in processing the ISSN will return None
            return None

    def syntax_ok(self, id_string):
        if not id_string.startswith(self._p):
            id_string = self._p+id_string
        return True if match("^issn:[0-9]{4}-[0-9]{3}[0-9X]$", id_string, re.IGNORECASE) else False

    def check_digit(self,issn):
        if issn.startswith(self._p):
            spl = issn.find(self._p) + len(self._p)
            issn = issn[spl:]
        issn = issn.replace('-', '')
        if len(issn) != 8:
            return False
        ss = sum([int(digit) * f for digit, f in zip(issn, range(8, 1, -1))])
        _, mod = divmod(ss, 11)
        checkdigit = 0 if mod == 0 else 11 - mod
        if checkdigit == 10:
            checkdigit = 'X'
        return '{}'.format(checkdigit) == issn[7]
