from mocker import ANY
from mocker import Mocker
from mocker import expect
from pkg_resources import get_distribution
from plone.testing import Layer
import os
import shutil
import tempfile
import zc.buildout.easy_install
import zc.buildout.testing


def resolve_dependencies(pkg_name, result=None):
    if result is None:
        result = set()

    if pkg_name in ('setuptools', 'zc.buildout'):
        return result

    result.add(pkg_name)
    for pkg in get_distribution(pkg_name).requires():
        resolve_dependencies(pkg.project_name, result)

    return result


class RecipeLayer(Layer):

    @property
    def globs(self):
        # globs is required for zc.buildout.testing setup / tear down
        if 'buildout' not in self:
            self['buildout'] = {}
        return self['buildout']

    def testSetUp(self):
        zc.buildout.testing.buildoutSetUp(self)
        for pkgname in resolve_dependencies('ftw.recipe.checkversions'):
            zc.buildout.testing.install_develop(pkgname, self)

    def testTearDown(self):
        zc.buildout.testing.buildoutTearDown(self)
        pypi_url = 'http://pypi.python.org/simple'
        zc.buildout.easy_install.default_index_url = pypi_url
        os.environ['buildout-testing-index-url'] = pypi_url
        zc.buildout.easy_install._indexes = {}


RECIPE_FIXTURE = RecipeLayer()


class MockPypiLayer(Layer):

    def testSetUp(self):
        self['pypi'] = {'foo': '2',
                        'bar': '2'}

        self['mocker'] = mocker = Mocker()
        fetcher = mocker.replace(
            'ftw.recipe.checkversions.pypi.get_newest_release')
        expect(fetcher(ANY)).call(self.fetcher).count(0, None)
        mocker.replay()

    def testTearDown(self):
        mocker = self['mocker']
        mocker.restore()
        mocker.verify()

    def fetcher(self, package):
        return self['pypi'].get(package, None)


MOCK_PYPI_FIXTURE = MockPypiLayer()


class TempDirectory(Layer):

    def testSetUp(self):
        self['tempdir'] = tempfile.mkdtemp('ftw.recipe.checkversions')

    def testTearDown(self):
        shutil.rmtree(self['tempdir'])


TEMP_DIRECTORY_FIXTURE = TempDirectory()
