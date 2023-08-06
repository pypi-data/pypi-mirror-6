Persona-IDP
============

.. image:: https://pypip.in/v/persona-idp/badge.png
        :target: https://crate.io/packages/persona-idp

.. image:: https://pypip.in/d/persona-idp/badge.png
    :target: https://crate.io/packages/persona-idp

.. image:: https://secure.travis-ci.org/dpaw2/persona-idp.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/dpaw2/persona-idp

.. image:: https://pypip.in/license/persona-idp/badge.png
    :target: https://pypi.python.org/pypi/persona-idp/    


This is a generic and reusable python implementation of 
`Mozilla Persona Identity Provider`_.

This module is used on our production servers and authenticates users
against our internal Active Directory controller.

See also `BrowserID specification`_ for more details.

.. _Mozilla Persona Identity Provider: https://developer.mozilla.org/en-US/Persona/Identity_Provider_Overview
.. _BrowserID specification: https://github.com/mozilla/id-specs/blob/prod/browserid/index.md

Installation
------------

Either::

    $ git clone https://github.com/dpaw2/persona-idp
    $ cd persona-idp
    $ python setup.py install

or::

    $ pip install persona-idp

Usage
-----

Please, *modify* at least the secret and rsa_key (unless you want to have
*serious security* issues)::

    $ cat wsgi.py
    from persona_idp.idp import PersonaIDP

    application = PersonaIDP(rsa_key='/etc/apache2/certs/private.pem',
                             secret='my123secret',
                             provision_template='/tmp/provision.txt')

and::

    $ gunicorn --workers=2 wsgi:application

or::

    $ echo 'WSGIScriptAlias /persona /var/www/persona/wsgi.py' >> \
    >   /etc/apache2/conf.d/persona.conf


Examples
--------

See the *examples/* folder.

Tests
-----

::

    $ python setup.py test


Help
----

Join the *dpaw* mailing list, or read the archives, at
    http://groups.google.com/group/dpaw

Issues
------

Use our github issue tracker, at
   https://github.com/dpaw2/persona-idp/issues 

Contribute
----------

::

    $ git clone https://github.com/dpaw2/persona-idp
    $ python setup.py develop

We prefer patches submitted via pull requests, at
    https://github.com/dpaw2/persona-idp/pulls


Acknowledgements
----------------

This work is based on previous work of @djc and his `persona-totp`_.

.. _persona-totp: https://github.com/djc/persona-totp/
