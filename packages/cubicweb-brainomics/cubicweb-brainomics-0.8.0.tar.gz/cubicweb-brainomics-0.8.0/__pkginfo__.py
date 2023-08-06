# pylint: disable=W0622
"""cubicweb-brainomics application packaging information"""

modname = 'brainomics'
distname = 'cubicweb-brainomics'

numversion = (0, 8, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Cube for the Brainomics Project, see http://www.brainomics.net/'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.17.0',
                'cubicweb-questionnaire': '>= 0.5.0',
                'cubicweb-neuroimaging': '>= 0.5.0',
                'cubicweb-genomics': '>= 0.7.0',
                'cubicweb-medicalexp': '>= 0.8.0',
                'cubicweb-card': None,
                'cubicweb-bootstrap': '>= 0.4.0',
                'cubicweb-squareui': '>= 0.2.0',
                'cubicweb-comment': None,
                'cubicweb-jqplot': None,
                }
__recommends__ = {'cubicweb-vtimeline': '>= 0.4.0'}


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
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'wdoc',
              'i18n', 'migration', 'importers',
              'data/bootstrap', 'data/bootstrap/css', 'data/bootstrap/img', 'data/images', 'data/img',):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

