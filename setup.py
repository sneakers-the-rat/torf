from setuptools import setup, find_packages

with open('torf/_version.py') as f:
    exec(f.read())

try:
    long_description = open('README.rst').read()
except OSError:
    long_description = ''

setup(
    name               = 'torf',
    version            = __version__,
    packages           = find_packages(),
    python_requires    = '>=3.6, ==3.*',
    install_requires   = ['flatbencode==0.2.*'],

    author             = 'Random User',
    author_email       = 'rndusr@posteo.de',
    description        = 'High-level Python 3 module for creating and parsing torrent files',
    long_description   = long_description,
    keywords           = 'bittorrent torrent bencode magnet',
    url                = 'https://github.com/rndusr/torf',

    classifiers        = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6'
    ]
)
