from ftw.recipe.checkversions.buildout import read_versions
from ftw.recipe.checkversions.checker import get_version_updates
import sys


def main(buildout_dir, versions, blacklists, blacklist_packages):
    current_versions = read_versions(buildout_dir, versions)
    blacklist = dict()
    for file_or_url in blacklists:
        blacklist.update(read_versions(buildout_dir, file_or_url))

    blacklist = blacklist.keys() + list(blacklist_packages)
    updates = get_version_updates(current_versions, blacklist)

    print >>sys.stderr, ''
    print '[versions]'
    for package, version in sorted(updates.items()):
        print package, '=', version
