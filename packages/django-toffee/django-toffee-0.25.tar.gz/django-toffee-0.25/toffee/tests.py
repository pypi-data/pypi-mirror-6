from django.test import TestCase
import unittest
from utils import Header


class HeaderClassTests(unittest.TestCase):
    def test_emptyMetasTest(self):
        my_header = Header("bingorabbit")
        metas = {"author": "bingorabbit"}
        my_header.add_meta(metas)
        self.assertEqual(my_header.metas, metas)