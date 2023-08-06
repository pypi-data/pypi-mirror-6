from ftw.recipe.checkversions.buildout import read_versions
from ftw.recipe.checkversions.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.checkversions.tests import fshelpers
from unittest2 import TestCase


TEST_VERSIONS_URL = 'https://raw.githubusercontent.com/4teamwork/' + \
    'ftw-buildouts/master/test-versions.cfg'


class TestBuildout(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_versions_from_local_file(self):
        fshelpers.create_structure(self.tempdir, {
                'versions.cfg': '\n'.join((
                        '[versions]',
                        'foo = 1.0.0',
                        'bar = 1.2.0'))})

        self.assertEquals(
            {'foo': '1.0.0',
             'bar': '1.2.0'},
            read_versions(self.tempdir, 'versions.cfg'))

    def test_versions_from_local_file_with_extends(self):
        fshelpers.create_structure(self.tempdir, {
                'versions.cfg': '\n'.join((
                        '[versions]',
                        'foo = 1.0.0',
                        'bar = 1.2.0')),

                'buildout.cfg': '\n'.join((
                        '[buildout]',
                        'extends = versions.cfg'))})

        self.assertEquals(
            {'foo': '1.0.0',
             'bar': '1.2.0'},
            read_versions(self.tempdir, 'buildout.cfg'))

    def test_versions_from_URL(self):
        self.assertDictContainsSubset(
            {'setuptools': '',
             'distribute': ''},
            read_versions(self.tempdir, TEST_VERSIONS_URL))

    def test_versions_from_file_extending_URL(self):
        fshelpers.create_structure(self.tempdir, {
                'versions.cfg': '\n'.join((
                        '[buildout]\n',
                        'extends = %s' % TEST_VERSIONS_URL))})

        self.assertDictContainsSubset(
            {'setuptools': '',
             'distribute': ''},
            read_versions(self.tempdir, 'versions.cfg'))
