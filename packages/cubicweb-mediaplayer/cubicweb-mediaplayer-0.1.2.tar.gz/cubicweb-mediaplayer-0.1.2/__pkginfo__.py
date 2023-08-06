# pylint: disable=W0622
"""cubicweb-mediaplayer application packaging information"""

modname = 'mediaplayer'
distname = 'cubicweb-mediaplayer'

numversion = (0, 1, 2)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'provide a schema and API for sound and media files with a html5 player'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.17.12',
                'cubicweb-file': '>= 1.15.0',
                'python-id3': None,
                }
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

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

for dirname in [('entities',),
                ('views',),
                ('views', 'htmltemplates'),
                ('data',),
                ('data', 'jplayer'),
                ('data', 'jplayer', 'js'),
                ('data', 'jplayer', 'skin'),
                ('data', 'jplayer', 'skin', 'blue.monday'),
                ('data', 'jplayer', 'skin', 'circle.skin'),
                ('data', 'jplayer', 'skin', 'pink.flag'),
                ('data', 'jplayer', 'skin', 'simple.css'),
                ('data', 'img'),
                ('doc',),
                ('i18n',),
                ('hooks',),
                ('utils',),
                ('migration',),
                ]:
    dirname = join(*dirname)
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

