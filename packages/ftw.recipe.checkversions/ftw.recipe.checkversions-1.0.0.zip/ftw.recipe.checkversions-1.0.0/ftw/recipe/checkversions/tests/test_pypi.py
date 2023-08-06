from ftw.recipe.checkversions.pypi import get_newest_release
from unittest2 import TestCase


class TestGetNewestRelease(TestCase):

    def test_get_newest_package_vesion_from_pypi(self):
        self.assertEquals('0.1', get_newest_release('foobar2'))
