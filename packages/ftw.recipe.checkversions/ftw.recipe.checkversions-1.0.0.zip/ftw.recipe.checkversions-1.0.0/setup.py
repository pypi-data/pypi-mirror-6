import os
from setuptools import setup, find_packages


version = '1.0.0'


tests_require = [
    'mocker',
    'plone.testing',
    'unittest2',
    ]


setup(name='ftw.recipe.checkversions',
      version=version,
      description='Buildout recipe for finding new package versions.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw recipe checkversions buildout',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.recipe.checkversions',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.recipe'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points = {
        'zc.buildout': [
            'default = ftw.recipe.checkversions.recipe:Recipe'],
        'console_scripts': [
            'checkversions = ftw.recipe.checkversions.command:main']
        },
      )
