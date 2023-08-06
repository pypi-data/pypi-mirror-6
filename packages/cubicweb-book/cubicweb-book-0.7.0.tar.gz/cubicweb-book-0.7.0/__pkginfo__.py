# pylint: disable-msg=W0622
"""cubicweb-book application packaging information"""

modname = 'book'
distname = 'cubicweb-%s' % modname

numversion = (0, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
description = 'component to describe books for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
long_desc = """
This cube provides the entity type ``Book`` and uses the OpenLibrary API_
to automatically fill the book's description

Check out : `Fetching book descriptions and covers`_

.. _`Fetching book descriptions and covers` : http://www.logilab.org/blogentry/9138
.. _API : http://openlibrary.org/dev/docs/api
"""
web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'cubicweb': '>= 3.10.0',
               'cubicweb-addressbook': None,
               'cubicweb-person': None,
               'cubicweb-file': None,
               }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob
scripts = glob(join('bin', 'book-*'))

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n',
                'migration', 'wdoc', 'data/images'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

