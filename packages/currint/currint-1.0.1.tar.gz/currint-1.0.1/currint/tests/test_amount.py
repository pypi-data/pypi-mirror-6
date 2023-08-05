# encoding: utf8
from __future__ import unicode_literals
from decimal import Decimal
from unittest import TestCase
from ..currency import currencies
from ..amount import Amount


class AmountTests(TestCase):

    def test_equality(self):
        self.assertEqual(
            Amount(currencies["GBP"], 132),
            Amount(currencies["GBP"], 132),
        )
        self.assertNotEqual(
            Amount(currencies["GBP"], 132),
            Amount(currencies["USD"], 132),
        )
        self.assertNotEqual(
            Amount(currencies["GBP"], 132),
            Amount(currencies["GBP"], 99),
        )

    def test_add(self):
        self.assertEqual(
            Amount(currencies["GBP"], 132) + Amount(currencies["GBP"], 100),
            Amount(currencies["GBP"], 232),
        )
        with self.assertRaises(ValueError):
            Amount(currencies["GBP"], 132) + Amount(currencies["USD"], 100)

    def test_subtract(self):
        self.assertEqual(
            Amount(currencies["GBP"], 132) - Amount(currencies["GBP"], 100),
            Amount(currencies["GBP"], 32),
        )
        with self.assertRaises(ValueError):
            Amount(currencies["GBP"], 132) - Amount(currencies["USD"], 100)

    def test_format(self):
        self.assertEqual(
            unicode(Amount(currencies["USD"], 132)),
            "$1.32",
        )
        self.assertEqual(
            unicode(Amount(currencies["GBP"], 132)),
            "£1.32",
        )
        self.assertEqual(
            unicode(Amount(currencies["MRO"], 7)),
            "1.2 MRO",
        )

    def test_apply_factor(self):
        self.assertEqual(
            Amount(currencies["GBP"], 150).apply_factor(2),
            Amount(currencies["GBP"], 300),
        )
        self.assertEqual(
            Amount(currencies["GBP"], 100).apply_factor(Decimal("1.004")),
            Amount(currencies["GBP"], 100),
        )
        self.assertEqual(
            Amount(currencies["GBP"], 100).apply_factor(Decimal("1.005")),
            Amount(currencies["GBP"], 101),
        )
        with self.assertRaises(ValueError):
            Amount(currencies["GBP"], 100).apply_factor(1.005)

    def test_from_code_and_minor(self):
        self.assertEqual(
            Amount.from_code_and_minor("GBP", 300),
            Amount(currencies["GBP"], 300),
        )
        self.assertEqual(
            Amount.from_code_and_minor("gbp", 300),
            Amount(currencies["GBP"], 300),
        )
        with self.assertRaises(ValueError):
            Amount.from_code_and_minor("WAITWHAT", 100)

    def test_from_code_and_major(self):
        self.assertEqual(
            Amount.from_code_and_major("GBP", "3.00"),
            Amount(currencies["GBP"], 300),
        )
        self.assertEqual(
            Amount.from_code_and_major("gbp", ".10"),
            Amount(currencies["GBP"], 10),
        )
        self.assertEqual(
            Amount.from_code_and_major("GBP", 10),
            Amount(currencies["GBP"], 1000),
        )
        self.assertEqual(
            Amount.from_code_and_major("GBP", Decimal("10.01")),
            Amount(currencies["GBP"], 1001),
        )
        with self.assertRaises(ValueError):
            Amount.from_code_and_major("WAITWHAT", 100)
        with self.assertRaises(ValueError):
            Amount.from_code_and_major("GBP", "12.432")
        with self.assertRaises(ValueError):
            Amount.from_code_and_major("GBP", "aaaaaaah")
