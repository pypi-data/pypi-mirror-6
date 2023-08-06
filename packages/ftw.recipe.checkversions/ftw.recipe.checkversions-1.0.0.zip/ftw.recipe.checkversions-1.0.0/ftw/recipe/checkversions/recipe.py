from pprint import pformat
from zc.recipe.egg import Egg


class Recipe(Egg):

    def __init__(self, buildout, name, options):
        self.options = options
        name = 'ftw.recipe.checkversions'

        # Only install "bin/masstranslate" script, not other scripts.
        options['scripts'] = 'checkversions'

        blacklists = options.get('blacklists')
        blacklists = blacklists and blacklists.split() or []
        blacklist_packages = options.get('blacklist-packages')
        blacklist_packages = (blacklist_packages and
                              blacklist_packages.split() or [])

        kwargs = {'buildout_dir': buildout['buildout']['directory'],
                  'versions': options.get('versions', 'versions.cfg'),
                  'blacklists': blacklists,
                  'blacklist_packages': blacklist_packages}
        options['arguments'] = '**%s' % pformat(kwargs)

        super(Recipe, self).__init__(buildout, name, options)
