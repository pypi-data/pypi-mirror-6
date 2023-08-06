from ftw.recipe.checkversions.progresslogger import ProgressLogger
from ftw.recipe.checkversions.pypi import get_newest_release
import sys


def get_version_updates(versions, blacklist=()):
    """Checks all packages in current_versions for newer releases and returns
    a new dict with all updated packages, ignoring those listed
    in the blacklist.
    """

    versions = [(pkg, vers) for (pkg, vers) in versions.items()
                if pkg not in blacklist]

    updates = {}
    for package, version in ProgressLogger(versions, sys.stderr):
        newest = get_newest_release(package)
        if newest is None:
            continue

        if version != newest:
            updates[package] = newest

    return updates
