# -*- coding: utf-8 -*-
'''
    vdirsyncer.utils
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Markus Unterwaditzer
    :license: MIT, see LICENSE for more details.
'''

import os
import vdirsyncer.log

password_key_prefix = 'vdirsyncer:'


def expand_path(p):
    p = os.path.expanduser(p)
    p = os.path.abspath(p)
    return p


def split_dict(d, f):
    a = {}
    b = {}
    for k, v in d.items():
        if f(k):
            a[k] = v
        else:
            b[k] = v

    return a, b


def parse_options(items):
    for key, value in items:
        if value.lower() in ('yes', 'true', 'on'):
            value = True
        elif value.lower() in ('no', 'false', 'off'):
            value = False
        try:
            value = int(value)
        except ValueError:
            pass
        yield key, value


def get_password(username, resource):
    """tries to access saved password or asks user for it

    will try the following in this order:
        1. read password from netrc (and only the password, username
           in netrc will be ignored)
        2. read password from keyring (keyring needs to be installed)
        3a ask user for the password
         b save in keyring if installed and user agrees

    :param username: user's name on the server
    :type username: str/unicode
    :param resource: a resource to which the user has access via password,
                     it will be shortened to just the hostname. It is assumed
                     that each unique username/hostname combination only ever
                     uses the same password.
    :type resource: str/unicode
    :return: password
    :rtype: str/unicode


    """
    import getpass
    try:
        from urlparse import urlsplit, urlunsplit
    except ImportError:
        from urllib.parse import urlsplit, urlunsplit

    try:
        import keyring
    except ImportError:
        keyring = None

    logger = vdirsyncer.log.get('sync')
    hostname = urlsplit(resource).hostname

    def _netrc():
        '''.netrc'''
        from netrc import netrc
        try:
            netrc_user, account, password = \
                netrc().authenticators(hostname) or (None, None, None)
            if netrc_user == username:
                return password
        except IOError:
            pass

    def _keyring():
        '''system keyring'''
        if keyring is None:
            return None

        key = resource
        password = None

        while True:
            password = keyring.get_password(password_key_prefix + key,
                                            username)
            if password is not None:
                return password

            parsed = urlsplit(key)
            path = parsed.path
            if path.endswith('/'):
                path = path.rstrip('/')
            else:
                path = path.rsplit('/', 1)[0] + '/'

            new_key = urlunsplit((
                parsed.scheme,
                parsed.netloc,
                path,
                parsed.query,
                parsed.fragment
            ))
            if new_key == key:
                return None
            key = new_key

    for func in (_netrc, _keyring):
        password = func()
        if password is not None:
            logger.debug('Got password for {} from {}'
                         .format(username, func.__doc__))
            return password

    prompt = ('Server password for {} at the resource {}: '
              .format(username, resource))
    password = getpass.getpass(prompt=prompt)

    if keyring is not None:
        answer = None
        while answer not in ['', 'y', 'n']:
            prompt = 'Save this password in the keyring? [y/N] '
            answer = raw_input(prompt).lower()
        if answer == 'y':
            keyring.set_password(password_key_prefix + resource,
                                 username, password)

    return password
