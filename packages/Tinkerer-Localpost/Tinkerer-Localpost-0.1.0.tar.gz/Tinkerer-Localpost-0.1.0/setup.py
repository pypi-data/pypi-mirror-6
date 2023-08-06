'''
    Tinkerer-Localpost Setup
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Package setup script.

    :copyright: Copyright 2013, Nathan Hawkes
    :license: FreeBSD, see LICENCE file
'''
from setuptools import setup, find_packages
import localpost


long_desc = '''
Tinkerer-Localpost is an addon for Tinkerer that makes it easy to see your blog
before you publish it.

Tinkerer-Localpost provides the ability to see your site as it would appear on
the Web from the privacy of your own computer. Use it to review your posts and
pages, check your RSS feed, build custom themes and customize your blog to your
heart's content.

Remember, before you post, always http://localhost.

Tinkerer-Localpost requires Tinkerer to function properly.
'''

requires = ['tinkerer>=1.2.1',]

test_requires = ['nose', 'tox', 'tinkerer>=1.2.1']


setup(
    name = 'Tinkerer-Localpost',
    version = localpost.__version__,
    url = 'http://github.com/gisraptor/tinkerer-localpost',
    download_url = 'https://pypi.python.org/pypi/Tinkerer-Localpost',
    license = 'FreeBSD',
    author = 'Nathan Hawkes',
    author_email = 'gisraptor@gmail.com',
    description = 'Localhost your Tinkerer blog',
    long_description = long_desc,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Utilities'
    ],
    platforms = 'any',
    packages = find_packages(exclude=['localposttest',]),
    entry_points = {
        'console_scripts': [
            'localpost = localpost.cmdline:main'
        ]
    },
    install_requires = requires,
    test_requires = test_requires,
    test_suite = 'nose.collector'
)
