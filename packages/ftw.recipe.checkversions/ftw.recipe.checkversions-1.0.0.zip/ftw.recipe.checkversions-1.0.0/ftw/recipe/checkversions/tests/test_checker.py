from ftw.recipe.checkversions.checker import get_version_updates
from ftw.recipe.checkversions.testing import MOCK_PYPI_FIXTURE
from unittest2 import TestCase


class TestGetVersionUpdates(TestCase):
    layer = MOCK_PYPI_FIXTURE

    def test_returns_updated_packages(self):
        self.layer['pypi'] = {'foo': '2.0.0'}
        self.assertEquals(
            {'foo': '2.0.0'},
            get_version_updates({'foo': '1.2.3'}))

    def test_does_not_return_up_to_date_packages(self):
        self.layer['pypi'] = {'foo': '2.0.0'}
        self.assertEquals(
            {},
            get_version_updates({'foo': '2.0.0'}))

    def test_blacklist_is_ignored(self):
        self.layer['pypi'] = {'foo': '2',
                         'bar': '2'}
        self.assertEquals(
            {'foo': '2'},
            get_version_updates({'foo': '1',
                                 'bar': '1'},
                                ['bar']))

    def test_not_found_packages_are_not_included(self):
        self.layer['pypi'] = {'foo': '2'}
        self.assertEquals(
            {'foo': '2'},
            get_version_updates({'foo': '1',
                                 'bar': '1'}))
