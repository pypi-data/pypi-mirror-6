from ftw.recipe.checkversions.testing import RECIPE_FIXTURE
from unittest2 import TestCase
import json
import os
import re


BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = checkversions',
        '',
        '[checkversions]',
        'recipe = ftw.recipe.checkversions'))


def extract_script_arguments(script_path):
    command = 'ftw.recipe.checkversions.command.main'
    with open(script_path) as file_:
        script = file_.read()

    xpr = 'sys\.exit\(%s\(\*\*(.*)\)\)' % re.escape(command)
    match = re.search(xpr, script, re.DOTALL)
    assert match, 'Could not find command call in script %s \n %s' % (
        script_path, xpr)
    kwargs = match.group(1).replace("'", '"')
    return json.loads(kwargs)


class TestRecipe(TestCase):

    layer = RECIPE_FIXTURE

    def setUp(self):
        self.__dict__.update(self.layer['buildout'])
        self.maxDiff = None

    def test_installing_recipe(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        output = self.system(self.buildout).strip()
        self.assertRegexpMatches(output, r'^Installing checkversions')
        self.assertRegexpMatches(output,
                                 r'Generated script.*bin/checkversions')

    def test_recipe_creates_script(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        expected = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertTrue(os.path.exists(expected),
                        'Missing executable %s' % expected)

    def test_script_is_executable(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertTrue(os.access(path, os.X_OK),
                        '%s should be executable' % path)

    def test_passes_buildout_directory_to_command(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset(
            {'buildout_dir': self.sample_buildout},
            extract_script_arguments(script_path))

    def test_passes_versions_argument_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    BUILDOUT_CONFIG,
                    'versions = versions.cfg')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset({'versions': 'versions.cfg'},
                                      extract_script_arguments(script_path))

    def test_versions_defaults_to_versions_cfg(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset({'versions': 'versions.cfg'},
                                      extract_script_arguments(script_path))

    def test_passes_blacklists_argument_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    BUILDOUT_CONFIG,
                    'blacklists =',
                    '  blacklist1.cfg'
                    '  blacklist2.cfg')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset(
            {'blacklists': ["blacklist1.cfg", "blacklist2.cfg"]},
            extract_script_arguments(script_path))

    def test_blacklists_defaults_to_empty_list(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset(
            {'blacklists': []},
            extract_script_arguments(script_path))

    def test_passes_blacklist_packages_argument_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    BUILDOUT_CONFIG,
                    'blacklist-packages =',
                    '  foo'
                    '  bar')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset(
            {'blacklist_packages': ["foo", "bar"]},
            extract_script_arguments(script_path))

    def test_blacklist_packages_defaults_to_empty_list(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'checkversions')
        self.assertDictContainsSubset(
            {'blacklist_packages': []},
            extract_script_arguments(script_path))
