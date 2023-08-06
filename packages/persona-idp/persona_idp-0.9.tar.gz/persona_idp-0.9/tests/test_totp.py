#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA

import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
from examples.totp import wsgi as totp
from persona_idp import utils


class Readable(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def testenv(data):
    return {
        'REQUEST_METHOD': 'POST',
        'wsgi.input': Readable(data),
    }


class TotpTestCase(unittest.TestCase):
    key = RSA.importKey(open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'tests.pem')).read())

    def test_b64u(self):
        res = utils.b64udecode(utils.b64uencode('test'))
        assert res == b'test'

        res = utils.b64udecode(utils.b64uencode('a'))
        assert res == b'a'

        res = utils.b64udecode(utils.b64uencode('ab'))
        assert res == b'ab'

        res = utils.b64udecode(utils.b64uencode('abc'))
        assert res == b'abc'

        res = utils.b64udecode(utils.b64uencode('Iñtërnâtiônàlizætiøn'))
        assert utils.safecmp(res, utils.bytestr('Iñtërnâtiônàlizætiøn'))

    def test_jws(self):
        jws = utils.sign({'foo': 'bar'}, self.key)
        assert utils.validate(jws, self.key)

        parts = jws.split(b'.')
        parts[1] = utils.b64uencode(utils.json.dumps({'bar': 'foo'}))
        fake = b'.'.join(parts)
        assert not utils.validate(fake, self.key)

    def test_verify(self):
        totp_val = totp.totp(totp.SECRETS['me']['totp']).pop()
        req = testenv(utils.json.dumps({'user': 'me@example.com',
                                        'totp_val': totp_val}))
        rsp = totp.application.verify(req)
        assert rsp[2]['status'] == 'okay'

        bad = utils.unwrap('FQVXRM3Q2JM6ECGG', totp.application.date_fmt,
                           rsp[2]['nonce'])
        assert not bad

    def test_session(self):
        session = utils.wrap(totp.application.secret,
                             totp.application.expires,
                             totp.application.date_fmt,
                             user='me@example.com')
        req = testenv(session)
        rsp = totp.application.session(req)
        assert rsp[2]['user'] == 'me@example.com'

        dt = (datetime.utcnow() - timedelta(1)).strftime(
            totp.application.date_fmt)
        session = {'user': 'me@example.com', 'expires': dt}
        nonce = utils.wrap(totp.application.secret,
                           totp.application.expires,
                           totp.application.date_fmt, **session)
        assert not utils.unwrap(totp.application.secret,
                                totp.application.date_fmt, nonce)

    def test_certificate(self):
        params = {'user': 'me@example.com', 'key': {'foo': 'bar'}}
        params['duration'] = 21600
        req = testenv(utils.json.dumps(params))
        jwt = totp.application.certify(req)[2]
        assert utils.validate(jwt, self.key)

        claims = utils.json.loads(utils.texttype(
            utils.b64udecode(jwt.split(b'.')[1]), 'utf-8'))
        assert claims['iss'] == 'example.com'
        assert claims['principal']['email'] == 'me@example.com'
        assert claims['exp'] - claims['iat'] == 21613000

    def test_hs256(self):
        key = os.urandom(20)
        jws = utils.sign({'foo': 'bar'}, key, 'HS256')
        assert utils.validate(jws, key)


if __name__ == '__main__':
    unittest.main()
