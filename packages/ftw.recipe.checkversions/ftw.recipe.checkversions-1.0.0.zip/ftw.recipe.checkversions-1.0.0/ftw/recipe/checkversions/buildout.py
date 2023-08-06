from ftw.recipe.checkversions.utils import capture_streams
from ftw.recipe.checkversions.utils import chdir
from zc.buildout.buildout import Buildout
from zc.buildout.buildout import _isurl
import os.path
import shutil
import sys
import tempfile


def read_versions(buildout_directory, filename_or_url):
    """Read a buildout configuration from a file or an URL and
    return the version-pinnings from the [versions] section as
    dict.
    """
    with capture_streams(stdout=sys.stderr):
        if _isurl(filename_or_url):
            buildout = load_buildout_from_url(filename_or_url)
        else:
            buildout = load_buildout_from_file(buildout_directory,
                                               filename_or_url)

    return buildout['versions']


def load_buildout_from_url(url):
    """Load a buildout config from an URL.
    """
    tempdir = tempfile.mkdtemp('ftw.recipe.checkversions')
    with chdir(tempdir):
        try:
            path = os.path.join(tempdir, 'temp.cfg')
            with open(path, 'w+') as cfg:
                cfg.write('[buildout]\n')
                cfg.write('extends = %s' % url)
            return Buildout(path, cloptions='', user_defaults=False)

        finally:
            shutil.rmtree(tempdir)


def load_buildout_from_file(buildout_directory, filename):
    """Load a buildout config from a local file.
    """
    with chdir(buildout_directory):
        return Buildout(filename, cloptions='', user_defaults=False)
