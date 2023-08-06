# pylint: disable-msg=W0622
"""cubicweb-cmt application packaging information"""

modname = 'cmt'
distname = 'cubicweb-cmt'

numversion = (0, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = 'Copyright (c) 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.'

author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

description = 'conference management tool'

web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.4']

__depends__ = {'cubicweb': '>= 3.10.0',
               'cubicweb-blog': None,
               'cubicweb-cmcicpay': None,
               'cubicweb-conference': '>= 0.12.0',
               'cubicweb-forgotpwd': '>= 0.2.0',
               'cubicweb-openidrelay': None,
               'cubicweb-registration': None,
               'cubicweb-shoppingcart': '>= 0.4.0',
               'cubicweb-tag': None,
               }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir, exists, dirname
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
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])

