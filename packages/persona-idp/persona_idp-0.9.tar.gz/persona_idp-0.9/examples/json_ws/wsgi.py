# add persona_idp onto pythonpath
import sys
import os

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CUR_DIR))
sys.path.append(ROOT_DIR)


# do the actual work
from persona_idp.idp import PersonaIDP
from persona_idp import utils

import requests
import logging

logger = logging.getLogger('persona_idp.example.json_ws')


BACKEND = 'http://rcstest-zatofront-001:11223/dpaw/ldap/auth/'


def verify_external(user=None, password=None, **kwargs):
    ######### HACK, TODO once we set it up on a correct domain
    email = user.lower().replace('www-dev.dec.wa.gov.au', 'DPaW.wa.gov.au')
    #########
    data = {'email': email, 'password': password}
    headers = {'Content-type': 'application/json'}
    logger.info("Sending authentication request for {0} to {1}".format(
        data['email'], BACKEND))
    r = requests.post(BACKEND, data=utils.json.dumps(data), headers=headers)
    data = utils.json.loads(r.content)
    logger.info("Received response {0}, status {1}".format(
        r.status_code, data['response']['status']))
    return data['response']['status'].lower() == 'okay'


application = PersonaIDP(root_dir=CUR_DIR, verify_func=verify_external)
