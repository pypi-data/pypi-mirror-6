import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('zc', 'zodbrecipes', 'zeo.txt')
    + '\n' +
    'Download\n'
    '**********************\n'
    )

open('doc.txt', 'w').write(long_description)

tests_require = [
    'zdaemon',
    'ZEO',
    'zope.event',
    'zope.testing',
    'zope.proxy',
    'zodbpickle',
    ]

name = "zc.zodbrecipes"
setup(
    name = name,
    version='2.0.0',
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipes for ZODB",
    license = "ZPL 2.1",
    keywords = "zodb buildout",
    url='http://svn.zope.org/'+name,
    long_description=long_description,

    packages = find_packages('.'),
    include_package_data = True,
    namespace_packages = ['zc'],
    install_requires = ['zc.buildout', 'setuptools', 'six',
                        'zc.recipe.egg', 'ZConfig >=2.4'],
    extras_require = dict(test=tests_require),
    entry_points = {
        'zc.buildout': [
             'server = %s:StorageServer' % name,
             ]
         },
    classifiers = [
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        ],
    test_suite='zc.zodbrecipes.tests.test_suite',
    tests_require=tests_require,
    )
