# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Create operating system users.

    Example::

        - users:
            - name: appuser                 # required
              groups: appgroup www-data     # whitespace separated groups
              create-home: True
              shell: /bin/bash
              password: use appuser         # see passwords: section

'''
import logging

from fabric.api import env

from voluptuous import Any, Required as req
from pave.schema import conditionals_schema
from pave.utils import check_list_conditionals, find_password, runcmd

log = logging.getLogger()
user_schema = {
    req('name'):                            basestring,
    req('groups',       default=None):      Any(None, basestring),
    req('create-home',  default=True):      bool,
    'shell':                                basestring,
    'password':                             basestring,
}
user_schema.update(conditionals_schema)
schema = [user_schema]


def handle(section, cmds, context):
    changed, errors = 0, 0
    context.chunking = True  # needed by these commands

    existing = runcmd(cmds.usr_lst)  # doesn't need to run as root
    if existing.failed:  errors += 1
    if existing:
        existing = existing.split()
    log.debug('existing: %s', existing)

    for user in section:
        user = check_list_conditionals(user, context, module=__name__, replace=False,
                             force=True)
        if not user: continue

        mycon = context.copy()    # prevent context spills
        name = user.pop('name')
        if name in existing:
            log.skip('not creating existing user: %s', name)
        else:
            log.change('creating user: %s', name)
            # check defaults
            if user['groups']:  # comma delimited
                user['groups'] = ','.join(user['groups'].split())

            if 'password' in user:
                user['password'], myerr = find_password(user['password'], True)
                errors += myerr

            mycon.update(user)
            result = runcmd(cmds.usr_add, name, **mycon)

            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    return changed, errors

