from __future__ import unicode_literals

# just in case we run this file as WSGI app
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# do stuff gracefully
try:
    from persona_idp.idp import PersonaIDP
    application = PersonaIDP()
except:
    application = None


VERSION = (0, 9, 0, 'final', 0)


def get_version(version=None):
    if version is None:
        version = VERSION

    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #  | {a|b|c}N - for alpha, beta and rc releases

    parts = 2 if version[2] == 0 else 3
    main = '.'.join('{0}'.format(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        sub = '.dev'

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = '{0}{1}'.format(mapping[version[3]], version[4])

    # see http://bugs.python.org/issue11638 - .encode('ascii')
    return '{0}{1}'.format(main, sub)
