# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC


import json
import unittest
from os import makedirs
from os.path import exists, join

from oc_ds_converter.oc_idmanager.issn import ISSNManager


class issnIdentifierManagerTest(unittest.TestCase):
    """This class aim at testing identifiers manager."""

    def setUp(self):
        if not exists("tmp"):
            makedirs("tmp")

        self.test_dir = join("test", "data")
        self.test_json_path = join(self.test_dir, "glob.json")
        with open(self.test_json_path, encoding="utf-8") as fp:
            self.data = json.load(fp)

        self.valid_issn_1 = "2376-5992"
        self.valid_issn_2 = "1474-175X"
        self.invalid_issn_1 = "2376-599C"
        self.invalid_issn_2 = "2376-5995"
        self.invalid_issn_3 = "2376-599"


    def test_issn_normalise(self):
        im = ISSNManager()
        self.assertEqual(
            self.valid_issn_1, im.normalise(self.valid_issn_1.replace("-", "  "))
        )
        self.assertEqual(
            self.valid_issn_2, im.normalise(self.valid_issn_2.replace("-", "  "))
        )
        self.assertEqual(
            self.invalid_issn_3, im.normalise(self.invalid_issn_3.replace("-", "  "))
        )

    def test_issn_is_valid(self):
        im = ISSNManager()
        self.assertTrue(im.is_valid(self.valid_issn_1))
        self.assertTrue(im.is_valid(self.valid_issn_2))
        self.assertFalse(im.is_valid(self.invalid_issn_1))
        self.assertFalse(im.is_valid(self.invalid_issn_2))
        self.assertFalse(im.is_valid(self.invalid_issn_3))

        im_file = ISSNManager(self.data)
        self.assertTrue(im_file.normalise(self.valid_issn_1, include_prefix=True) in self.data)
        self.assertTrue(im_file.normalise(self.valid_issn_2, include_prefix=True) in self.data)
        self.assertTrue(im_file.normalise(self.invalid_issn_2, include_prefix=True) in self.data)
        self.assertTrue(im_file.is_valid((im_file.normalise(self.valid_issn_1, include_prefix=True))))
        self.assertTrue(im_file.is_valid((im_file.normalise(self.valid_issn_2, include_prefix=True))))
        self.assertFalse(im_file.is_valid((im_file.normalise(self.invalid_issn_2, include_prefix=True))))
