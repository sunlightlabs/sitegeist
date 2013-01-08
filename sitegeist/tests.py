from decimal import Decimal
import unittest

from sitegeist import formatting, utils

class FormattersTestCase(unittest.TestCase):

    def test_dec2pct(self):

        d = Decimal("0.232385436346")
        s = formatting.dec2pct(d)
        self.assertEqual(s, "23.24%")

        d = Decimal("23.3023234235")
        s = formatting.dec2pct(d, raw=True)
        self.assertEqual(s, "23.30%")

    def test_dec2num(self):

        d = Decimal("23.235235")
        s = formatting.dec2num(d)
        self.assertEqual(s, "23.24")

        d = Decimal("23456.308")
        s = formatting.dec2num(d)
        self.assertEqual(s, "23,456.31")

        s = formatting.dec2num(d, whole=True)
        self.assertEqual(s, "23,456")

    def test_dec2curr(self):

        d = Decimal("23.8424")
        s = formatting.dec2curr(d)
        self.assertEqual(s, "$23.84")

        d = Decimal("2384.24")
        s = formatting.dec2curr(d)
        self.assertEqual(s, "$2,384.24")


class UtilsTestCase(unittest.TestCase):

    def test_age2ym(self):

        age = Decimal("31.4")
        (years, months) = utils.age2ym(age)
        self.assertEqual(years, 31)
        self.assertEqual(months, 4)

        age = Decimal("31.95")
        (years, months) = utils.age2ym(age)
        self.assertEqual(years, 31)
        self.assertEqual(months, 11)

        age = Decimal("40.0")
        (years, months) = utils.age2ym(age)
        self.assertEqual(years, 40)
        self.assertEqual(months, 0)


if __name__ == '__main__':
    unittest.main()
