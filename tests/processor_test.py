# -*- coding: utf-8 -*-
from unittest import TestCase
from processor import WaitProcessor


class WaitProcessTest(TestCase):
    def test_singleton(self):
        a = WaitProcessor()
        b = WaitProcessor()
        self.assertEqual(id(a), id(b))
