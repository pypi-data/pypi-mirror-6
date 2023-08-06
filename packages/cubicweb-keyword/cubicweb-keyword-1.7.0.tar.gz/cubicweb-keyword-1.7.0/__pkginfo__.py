# pylint: disable-msg=W0622
"""cubicweb-classification-schemes packaging information"""

modname = 'keyword'
distname = "cubicweb-keyword"

numversion = (1, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "classification schemes system for the Cubicweb framework"
long_desc = """Summary
-------
The `keyword` cube provides classification by using hierarchies of keywords to
classify content.

Each classification is represented using a `Classification` entity, which will
hold a keywords tree.

There is two types of keywords:

- `Keyword` which contains a description,

- `CodeKeyword` which contains the keyword description and the associated code.

In order to link an entity to a keyword, you have to add a relation `applied_to`
in the schema.

Each keyword has the `subkeyword_of` relation definition. This allows to
navigate in the classification without a Modified Preorder Tree Traversal
representation of the data.

Some methods are defined in order to get parents and children or get the status
of a keyword (leaf or root).

See also `cubicweb-tag`_ as another (simpler) way to classify content.

.. _`cubicweb-tag`: http://www.cubicweb.org/project/cubicweb-tag
"""

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.15.0'}
__use__ = tuple(__depends_cubes__)

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]
try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
        [join(THIS_CUBE_DIR, 'test'), [fname for fname in glob('test/*.py')]],

    ]
    for dname in ('data', 'i18n', 'migration', ):
        if isdir(dname):
            data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])

    # Note: here, you'll need to add subdirectories if you want
    # them to be included in the debian package
    for dname in ('data', ):
        data_files.append([join(THIS_CUBE_DIR, 'test', dname), listdir(join('test', dname))])

except OSError:
    # we are in an installed directory
    pass
