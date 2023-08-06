# add persona_idp onto pythonpath
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

# do the actual work
from persona_idp.idp import PersonaIDP
from persona_idp import utils

import time
import base64
import struct
import hmac
import hashlib


SECRETS = utils.json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'secrets.json')))


# Functions for HOTP/TOTP
def hotp(secret, ivals):
    key = base64.b32decode(secret)
    msg = struct.pack('>Q', ivals)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    if sys.version < '3':
        o = ord(h[19]) & 15
    else:
        o = h[19] & 15
    return (struct.unpack('>I', h[o:o + 4])[0] & 0x7fffffff) % 1000000


def totp(secret, tolerance=0):
    values = set()
    for i in range(-tolerance, tolerance + 1):
        ivals = (int(time.time()) + (i * 30)) // 30
        values.add('%06i' % hotp(secret, ivals))
    return values


def verify_totp(totp_val=None, user=None, **kwargs):
    try:
        user = user.split('@', 1)[0]
    except ValueError:
        return False

    secret = SECRETS[user]['totp'].encode('utf-8')
    return totp_val in totp(secret, 1)


application = PersonaIDP(verify_func=verify_totp)
