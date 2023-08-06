# pylint: disable-msg=W0622
"""cubicweb-securityprofile application packaging information"""

modname = 'securityprofile'
distname = 'cubicweb-securityprofile'

numversion = (0, 2, 2)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = """A SecurityProfile is a way to easily give membership to a set of
groups to several users: define your SecurityProfile, say that it
gives_membership to the CWGroups you're interested in, and link your
users to the profile.

This cube also adds:

* a security_officers CWGroup which has rights to manage
  SecurityProfiles and the relations used by that entity

* the possibility to map some attributes from an LDAP directory to
  define which SecurityProfiles a user is linked to
"""
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.15.3'}
__recommends__ = {}


from os import listdir as _listdir
from os.path import join, isdir, exists
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
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'wdoc', 'i18n', 'migration'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

