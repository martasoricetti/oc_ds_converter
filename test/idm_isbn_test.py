# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC


import json
import unittest
from os import makedirs
from os.path import exists, join

from oc_ds_converter.oc_idmanager.isbn import ISBNManager


class issnIdentifierManagerTest(unittest.TestCase):
    """This class aim at testing identifiers manager."""

    def setUp(self):
        if not exists("tmp"):
            makedirs("tmp")

        self.test_dir = join("test", "data")
        self.test_json_path = join(self.test_dir, "glob.json")
        with open(self.test_json_path, encoding="utf-8") as fp:
            self.data = json.load(fp)

        self.valid_isbn_1 = "9780134093413"
        self.valid_isbn_2 = "978-3-16-148410-0"
        self.valid_isbn_3 = "0-19-852663-6"
        self.invalid_isbn_1 = "0-19-850000-6"
        self.invalid_isbn_2 = "978-3-16-148410-99"


    def test_isbn_normalise(self):
        im = ISBNManager()
        self.assertEqual(
            self.valid_isbn_1, im.normalise("978-0-13-409341-3")
        )
        self.assertEqual(
            self.valid_isbn_1, im.normalise("ISBN" + self.valid_isbn_1)
        )
        self.assertEqual(
            im.normalise(self.valid_isbn_2), im.normalise(self.valid_isbn_2.replace("-", "  "))
        )

    def test_isbn_is_valid(self):
        im = ISBNManager()
        self.assertTrue(im.is_valid(self.valid_isbn_1))
        self.assertTrue(im.is_valid(self.valid_isbn_2))
        self.assertTrue(im.is_valid(self.valid_isbn_3))
        self.assertFalse(im.is_valid(self.invalid_isbn_2))
        self.assertFalse(im.is_valid(self.invalid_isbn_1))

        im_file = ISBNManager(self.data)
        self.assertTrue(im_file.normalise(self.valid_isbn_1, include_prefix=True) in self.data)
        self.assertTrue(im_file.normalise(self.valid_isbn_2, include_prefix=True) in self.data)
        self.assertTrue(im_file.normalise(self.invalid_isbn_2, include_prefix=True) in self.data)
        self.assertTrue(im_file.is_valid((im_file.normalise(self.valid_isbn_1, include_prefix=True))))
        self.assertTrue(im_file.is_valid((im_file.normalise(self.valid_isbn_2, include_prefix=True))))
        self.assertFalse(im_file.is_valid((im_file.normalise(self.invalid_isbn_2, include_prefix=True))))
