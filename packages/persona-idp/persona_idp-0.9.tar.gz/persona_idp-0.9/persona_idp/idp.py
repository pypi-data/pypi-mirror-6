#!/usr/bin/env python2
from Crypto.PublicKey import RSA

import os
import time
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse    # python3
import sys
import mimetypes

from persona_idp import utils

DIR = os.path.dirname(os.path.abspath(__file__))


def always_success(*args, **kwargs):
    # this function authenticates any user:password combination
    # please, don't use this in production
    return True


class PersonaIDP(object):
    private_key = os.path.join(os.path.dirname(DIR), 'tests.pem')
    expires = 30    # days
    handlers = {}
    verify_func = always_success
    storage_key = 'PersonaIDP'
    date_fmt = '%Y-%m-%d %H:%M:%S'
    secret = "FIXME"
    authenticate_template = 'authenticate.html'
    provision_template = 'provision.html'
    root_dir = DIR

    key = None

    def __init__(self, *args, **kwargs):
        self.handlers = {
            'provision': self.provision, 'authenticate': self.authenticate,
            'verify': self.verify, 'static': self.static,
            'session': self.session, 'certify': self.certify,
        }

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.key = RSA.importKey(open(self.private_key).read())

    # rendering "engine"
    def render(self, tmpl, vars):
        tmpl_path = os.path.join(self.root_dir, 'templates', tmpl)
        if not os.path.isfile(tmpl_path):
            tmpl_path = os.path.join(DIR, 'templates', tmpl)
        with open(tmpl_path) as f:
            src = f.read()
            for k, v in vars.items():
                src = src.replace('{{ %s }}' % k, v)
            return src

    # URL endpoints
    def static(self, env):
        f = os.path.join(self.root_dir, env['PATH_INFO'].strip('/'))
        if not os.path.isfile(f):
            f = os.path.join(DIR, env['PATH_INFO'].strip('/'))
        if os.path.isfile(f):
            mime = mimetypes.guess_type(f)
            return 200, mime[0], open(f, 'rb').read(), mime[1]
        else:
            return self.http404(env)

    def provision(self, env):
        return 200, self.provision_template

    def authenticate(self, env):
        return 200, self.authenticate_template

    def verify(self, env):
        assert env['REQUEST_METHOD'] == 'POST'
        data = utils.json.loads(env['wsgi.input'].read())
        if self.verify_func(**data):
            session = utils.wrap(self.secret, self.expires, self.date_fmt,
                                 user=data['user'])
            return 200, 'json', {'status': 'okay', 'nonce': session}
        else:
            return 200, 'json', {'status': 'failed'}

    def session(self, env):
        # return { 'proven': email, 'csrf': csrf }
        assert env['REQUEST_METHOD'] == 'POST'
        return 200, 'json', utils.unwrap(self.secret, self.date_fmt,
                                         env['wsgi.input'].read())

    def certify(self, env):
        """
        assert env['REQUEST_METHOD'] == 'POST'
        params = json.loads(env['wsgi.input'].read())
        host = params['email'].split('@')[1]

        claims = {'iss': host, 'public-key': json.loads(params['pubkey'])}
        duration = min(24 * 60 * 60, int(params['duration']))
        claims['iat'] = int(time.time()) * 1000
        claims['exp'] = claims['iat'] + duration * 1000
        claims['principal'] = {'email': params['email']}

        key = load_key('RS256', {'n': KEY.key.n, 'd': KEY.key.d,
                                'e': KEY.key.e})
        from browserid.jwt import generate, load_key
        return 200, 'json', {'cert': generate(claims, key)}
        """
        """
        assert env['REQUEST_METHOD'] == 'POST'
        params = json.loads(env['wsgi.input'].read())
        host = params['email'].split('@')[1]

        header = {
            'alg': 'RS256'
        }

        claims = {'iss': host, 'public-key': json.loads(params['pubkey'])}
        duration = min(24 * 60 * 60, int(params['duration']))
        claims['iat'] = int(time.time()) * 1000
        claims['exp'] = claims['iat'] + duration * 1000
        claims['principal'] = {'email': params['email']}

        # see jwt.generate_jwt, we cannot use it directly because it
        # modifies 'iat' and 'exp' :(
        import jws
        certificate = ("%s.%s.%s" % (jws.utils.encode(header),
                                jws.utils.encode(claims),
                                jws.sign(header, claims, KEY))
                    )

        return 200, 'json', {'cert': certificate}
        """
        assert env['REQUEST_METHOD'] == 'POST'
        params = utils.json.loads(env['wsgi.input'].read())
        host = params['user'].split('@')[1]

        claims = {'iss': host, 'public-key': params['key']}
        duration = min(24 * 60 * 60, params['duration'] + 13)
        claims['iat'] = (int(time.time()) - 13) * 1000  # clock skew
        claims['exp'] = claims['iat'] + duration * 1000
        claims['principal'] = {'email': params['user']}
        return 200, 'text', utils.sign(claims, self.key)

    def http404(self, env):
        return 404, 'text', 'not found'

    # WSGI application
    def __call__(self, env, respond):
        pi = env['PATH_INFO'] and env['PATH_INFO'].strip('/').split('/') or []

        if pi and pi[0] in self.handlers:
            rsp = self.handlers[pi[0]](env)
        else:
            rsp = self.http404(env)

        if rsp[1].endswith('.html'):
            headers = {'Content-Type': 'text/html; charset=utf-8'}
            persona = 'login.persona.org'
            if env.get('HTTP_REFERER'):
                referrer = urlparse.urlparse(env['HTTP_REFERER'])
                persona = referrer.scheme + '://' + referrer.netloc
            content = self.render(rsp[1], {'key': self.storage_key,
                                           'persona': persona})
        elif rsp[1] == 'json':
            headers = {'Content-Type': 'application/json'}
            content = utils.json.dumps(rsp[2])

        elif rsp[1] == 'text':
            headers = {'Content-Type': 'text/plain; charset=utf-8'}
            content = rsp[2]

        else:
            headers = {'Content-Type': rsp[1]}
            if rsp[3]:
                headers['Content-Encoding'] = rsp[3]
            content = rsp[2]

        status = {200: '200 OK', 404: '404 Not Found'}
        respond(status[rsp[0]], headers.items())
        return [content]


# a command line utility for generating .well-known/browserid
def support(private_key_file):
    private_key = RSA.importKey(open(private_key_file))

    doc = {
        'public-key': {
            'algorithm': 'RS',
            'n': str(private_key.n),
            'e': str(private_key.e),
        },
        'authentication': '/persona/authenticate/',
        'provisioning': '/persona/provision/',
    }
    print(utils.json.dumps(doc, indent=2))


if __name__ == '__main__':
    if (len(sys.argv) != 3 or sys.argv[1].lower() != 'support' or
            not os.isfile(sys.argv[2])):
        print('Usage: %s support <private_key>' % sys.argv[0])
    else:
        support(sys.argv[2])
