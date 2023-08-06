from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from datetime import datetime, timedelta

import itertools
import base64
import hashlib
import hmac

import sys

try:
    import simplejson as json
except ImportError:
    import json

texttype = sys.version >= '3' and str or unicode


# bytes stuff
def bytestr(s, enc='utf-8'):
    # returns bytes
    return s.encode(enc) if isinstance(s, texttype) else s


def safecmp(a, b):
    # a, b are bytes
    if sys.version >= '3':
        assert isinstance(a, bytes)
        assert isinstance(b, bytes)
    if sys.version < '3':
        zip_longest = itertools.izip_longest
    else:
        zip_longest = itertools.zip_longest
    pairs = zip_longest(a, b, fillvalue=' ')

    ord23 = lambda c: sys.version < '3' and ord(c) or c
    return not sum(ord23(x) ^ ord23(y) for (x, y) in pairs)


# Some bits for JWS
def b64uencode(s):
    # returns bytes
    return base64.urlsafe_b64encode(bytestr(s, 'utf-8')).replace(b'=', b'')


def b64udecode(s):
    # return bytes
    s = bytestr(s) + b'=' * (4 - (len(s) % 4))
    return base64.urlsafe_b64decode(s)


def validate(token, key):
    parts = token.split(b'.')
    h = json.loads(texttype(b64udecode(parts[0]), 'utf-8'))
    assert h['alg'] in set(('RS256', 'HS256'))
    input = b'.'.join(parts[:2])
    if h['alg'] == 'RS256':
        hashed = SHA256.new(input)
        return PKCS1_v1_5.new(key).verify(hashed, b64udecode(parts[2]))
    else:
        sig = hmac.new(key, input, hashlib.sha256).digest()
        return safecmp(sig, b64udecode(parts[2]))


# Functions for secure cookies
def wrap(secret, expires_, date_fmt, **vals):
    expires_ = datetime.utcnow() + timedelta(expires_)
    if 'expires' not in vals:
        vals['expires'] = expires_.strftime(date_fmt)
    data = b64uencode(json.dumps(vals))
    sig = b64uencode(hmac.new(bytestr(secret), data, hashlib.sha1).digest())
    return data + b'.' + sig


def unwrap(secret, date_fmt, s):
    data, sig = s.split(b'.')
    new = b64uencode(hmac.new(bytestr(secret), data, hashlib.sha1).digest())
    if not safecmp(new, sig):
        return {}

    data = json.loads(texttype(b64udecode(data), 'utf-8'))
    now = datetime.utcnow().strftime(date_fmt)
    if now > data['expires']:
        return {}

    return data


def sign(payload, key, alg='RS256'):
    # returns bytes
    h = json.dumps({'alg': alg})
    input = b64uencode(h) + b'.' + b64uencode(json.dumps(payload))
    if alg == 'RS256':
        sig = PKCS1_v1_5.new(key).sign(SHA256.new(input))
    elif alg == 'HS256':
        sig = hmac.new(key, input, hashlib.sha256).digest()
    return input + b'.' + b64uencode(sig)
