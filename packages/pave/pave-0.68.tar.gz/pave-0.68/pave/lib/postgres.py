# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Manage postgres.
    *Captain Obvious here to chime-in that postgres must be installed on
    remote target beforehand, see* `packages`_.

    ``link current:``
        Create a symbolic link from the last sorted item in
        ``/etc/postgresql/`` to ``/etc/postgresql/curr``.
    ``replace``,  ``access:``
        See the corresponding directive under configure.
        These are for convenience to group postgres-related configuration
        together.
    ``user``,  ``db``,  ``grant``,  ``sql:``
        ``postgresql-client-common`` (or distro equiv.) must be installed on
        remote target beforehand.
        Run the appropriate commands to create objects or configure the
        database.  String or list of strings may be given.

    Example::

        - postgres:
            link current: False
            replace:
                - '#\s*password_enc password_enc %pgcfg/postgresql.conf'

            su-password:
                use pgsu                                # see passwords:
                # md5 acbd18db4cc2f85cedef654fccc4a4d8  # how to hard-code

            db: # quotes not required below, but fixes highlighting. :/
                - name: "%sitename"
            user:
                - name: "%sitename"
            grant:
                # privs   on_obj    named         to_user
                all       database  %sitename     %sitename

            sql: # str|list lines of sql, first token should be dbname:
                template1 select datname from pg_database
                          where datname = '%sitename';

'''
import logging

from fabric.api import env, run
from fabric.contrib.files import exists as rexists #append,
from voluptuous import Any, Required as req

from pave.lib.configure import handle as cfghandle, vsch as cfgvsch
from pave.schema import conditionals_schema
from pave.utils import (runcmd, sequence, eval_conditionals, err_cond,
                        find_password, md5, shplit)


log = logging.getLogger()

# section schema
createuser_schema = Any(None, [{
    req('name'):                          basestring,
    req('encrypted',    default=True):    bool,
    req('createdb',     default=False):   bool,
    req('createrole',   default=False):   bool,
    req('superuser',    default=False):   bool,
    req('login',        default=True):    bool,
}] )
createdb_schema = Any(None, [{
    req('name'):                          basestring,
    req('template', default='template0'): basestring,
    'tablespace':                         basestring,
    'encoding':                           basestring,
    'locale':                             basestring,
    'description':                        basestring,
}] )
schema = {
    req('link current', default=True):    bool,
    req('replace',      default=[]):      cfgvsch,
    req('access',       default=[]):      cfgvsch,
    req('su-password',  default=''):      basestring,  # need validation here
    req('user',         default=[]):      createuser_schema,
    req('db',           default=[]):      createdb_schema,
    req('grant',        default=[]):      Any(basestring, [basestring]),
    req('sql',          default=[]):      Any(basestring, [basestring]),
}
schema.update(conditionals_schema)


def handle(section, cmds, context):
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from module
        return changed, errors

    if section.pop('link current', None):
        # get pg versions
        result = run('ls -1 /etc/postgresql/')
        if result.succeeded:
            dirs = sorted(result.split('\n'))
            if dirs:
                latest = dirs[-1]
                if rexists('/etc/postgresql/curr'):
                    log.skip('/etc/postgresql/curr exists')
                else:
                    log.change('linking %s to ./curr', latest)
                    result = runcmd(cmds.pg_ln_curr, latest, **context)
                    if result.succeeded:   changed += 1
                    else:
                        log.error(result); errors += 1
                        if env.pave_raise_errs: raise RuntimeError
            else:
                log.error('link: config not found--is pg installed?'); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        else:
            log.error('link: %s--is pg installed?', result); errors += 1
            if env.pave_raise_errs: raise RuntimeError

    # set this after link_curr, since it has to be root to do that
    context.sudo_user = context.get('sudo_user') or 'postgres'
    context.chunking = True  # needed by these commands

    replaces = sequence(section.pop('replace', None))
    if replaces:
        cfghandle({'replace': replaces}, cmds, context)

    # access
    perms = sequence(section.pop('access', None))
    if perms:
        cfghandle({'access': perms}, cmds, context)

    supwd = section.pop('su-password', None)
    if supwd:
        if supwd.startswith('md5 '):  # already md5d
            supwd = shplit(supwd)[1]
        else:
            supwd, errs  = find_password(supwd)
            errors += errs
            # http://www.postgresql.org/docs/9.1/static/catalog-pg-authid.html
            supwd = 'md5' + md5(supwd+'postgres')

        result = runcmd(cmds.pg_get_pwd, **context)
        if result.failed:
            log.error(result); errors += 1
        result = result.strip()
        log.debug('password: existing hash %r.', result)
        log.debug('password:   ...new hash %r.', supwd)

        if result == supwd:
            log.skip('password matches.')
        else:
            log.change('setting password.')
            result = runcmd(cmds.pg_set_pwd, supwd, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    for user in sequence(section.pop('user', [])):
        # look for existing
        result = runcmd(cmds.pg_ls_user, **context)
        if result.succeeded:  existing = result.split()
        else:
            log.error(result); errors += 1 # don't stop on search failure
            existing = []

        username = user['name']
        if username in existing:
            log.skip('user: %s found.', username)
        else:
            log.change('user: creating %s.', username)
            mycon = context.copy()
            mycon.update(user)
            result = runcmd(cmds.pg_cr_user, username, **mycon)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    for db in sequence(section.pop('db', [])):
        # look for existing
        result = runcmd(cmds.pg_ls_db, **context)
        if result.succeeded:  existing = result.split()
        else:
            log.error(result); errors += 1 # don't stop on search failure
            existing = []

        dbname = db['name']
        if dbname in existing:
            log.skip('db: %s found.', dbname)
        else:
            log.change('db: creating %s.', dbname)
            mycon = context.copy()
            mycon.update(db)
            desc = db.get('description','')
            if desc: desc = u'"%s"' % desc
            result = runcmd(cmds.pg_cr_db, dbname, desc, **mycon)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    for grant in sequence(section.pop('grant', [])):
        # look for existing
        privs, objtype, dbname, uname = grant.split()
        if objtype == 'db': objtype = 'database'
        # look for existing acl
        result = runcmd(cmds.pg_ls_acl, dbname, **context)
        if result.succeeded:
            acl = (len(result.split()) == 3)
        else:
            log.error(result); errors += 1 # don't stop on search failure
            acl = False

        if acl:
            log.skip('grant: acl for %s %s found.', dbname, objtype)
        else:
            log.change('grant: '+cmds.pg_grant.partition(' -c ')[2], privs,
                        objtype, dbname, uname)
            result = runcmd(cmds.pg_grant, privs, objtype, dbname, uname,
                            **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    for statement in sequence(section.pop('sql', [])):
        # not sure how to skip this, maybe save a file.
        dbname = statement.split()[0]
        statement = statement[len(dbname) + 1:]
        log.change(u'sql: running %.20r… against %s.', statement, dbname)
                    #~ statement.encode('ascii','backslashreplace'), dbname)
        result = runcmd(cmds.pg_sql, dbname, statement, **context)
        if result.succeeded:   changed += 1
        else:
            log.error(result); errors += 1
            if env.pave_raise_errs: raise RuntimeError

    if section:
        log.warn('extra junk in section: %s', section.keys())

    return changed, errors











