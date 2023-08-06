from StringIO import StringIO
from ftw.recipe.checkversions.command import main
from ftw.recipe.checkversions.testing import MOCK_PYPI_FIXTURE
from ftw.recipe.checkversions.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.checkversions.tests import fshelpers
from ftw.recipe.checkversions.utils import capture_streams
from plone.testing import Layer
from unittest2 import TestCase


VERSIONS_CONFIG = '\n'.join((
        '[buildout]',
        'versions = versions',
        '',
        '[versions]',
        'requests = 2.0.0',
        'setuptools = 0.6c11',
        'zope.component = 4.2.1',
        'zope.interface = 4.1.0',
        'zope.annotation = 4.0.0',
        ))


# The test-versions.cfg contains a pinning for "setuptools", thus using
# it as blacklist should make "setuptools" not appear.
BLACKLIST_URL = 'https://raw.githubusercontent.com/4teamwork/ftw-buildouts/' + \
    'master/test-versions.cfg'


class TestCommand(TestCase):
    layer = Layer(bases=(TEMP_DIRECTORY_FIXTURE, MOCK_PYPI_FIXTURE),
                  name='test_command:TestCommand:layer')

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test(self):
        self.layer['pypi'] = {
            'requests': '2.3.0',
            'setuptools': '0.7',
            'zope.component': '4.2.1',
            'zope.interface': '5.0.0',
            'zope.annotation': '4.2.0'}

        fshelpers.create_structure(self.tempdir, {
                'versions.cfg': VERSIONS_CONFIG})

        output = StringIO()
        with capture_streams(output):
            main(buildout_dir=self.tempdir,
                 versions='versions.cfg',
                 blacklists=(BLACKLIST_URL,),
                 blacklist_packages=('zope.annotation', ))

        self.assertEquals(
            '\n'.join((
                    '[versions]',
                    'requests = 2.3.0',
                    # 'setuptools = 0.6c11',  # blacklisted
                    # 'zope.component = 4.2.1',   # no new version
                    'zope.interface = 5.0.0')),
            output.getvalue().strip())
