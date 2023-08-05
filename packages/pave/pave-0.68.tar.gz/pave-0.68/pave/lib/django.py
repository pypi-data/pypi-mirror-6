# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Django helper module.
    *Captain Obvious recommends Django be installed on the target
    beforehand, see the* `packages`_ *section.*

    ``loaddata:``
        Load fixture files from given path, glob ok.

    ``manage:``
        Execute a management command every time this task group is run.

    ``manage-once:``
        Once and never again.

    Example::

        - django:
            workdir: ~%sitename/%sitename
            loaddata: "fixtures/*.json"
            manage-once: update_index
            syncdb: True
'''
import logging
from fabric.api import env
from fabric.context_managers import cd
from voluptuous import Any, Required as req

from pave.schema import conditionals_schema
from pave.utils import (runcmd, sequence, donepath, markdone,
                        eval_conditionals, err_cond)

log = logging.getLogger()
schema = {
    req('workdir'):                     basestring,
    req('syncdb', default=True):        bool,
    req('migrate-init', default=True):  bool,
    req('loaddata', default=''):        basestring,
    req('manage', default=[]):          Any(basestring, [basestring]),
    req('manage-once', default=[]):     Any(basestring, [basestring]),
    req('user', default=None):          basestring,
}
schema.update(conditionals_schema)


def handle(section, cmds, context):
    'Run the system package manager, and any others given.'
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from this module
        return changed, errors

    if section['user']:
        context.use_sudo = True
        context.sudo_user = section['user']

    with cd(section['workdir']):

        if section['syncdb']:
            result = runcmd(cmds.dj_chktable, **context)
            if result.succeeded:  # found a table
                log.skip(u'syncdb: already done.')
            else:
                log.change(u'syncdb: may take a few mins…')
                result = runcmd(cmds.dj_syncdb, **context)
                if result.succeeded:   changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

        if section['migrate-init']:
            result = runcmd(cmds.dj_chkmigrt, **context)
            if result.succeeded:
                log.skip(u'initial migrate has already been run.')
            else:
                log.change(u'initial migration…')
                result = runcmd(cmds.dj_initmgrt, **context)
                if result.succeeded:   changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

        if section['loaddata']:
            # check is not yet implemented, perhaps parse the json and
            # confirm an id in the table.
            result = runcmd(cmds.dj_chkdata % section['loaddata'],
                            chunking=False, **context)
            if result.succeeded:
                log.skip(u'loaddata: fixtures already loaded.')
            else:
                log.change(u'loaddata: fixtures…')
                result = runcmd(cmds.dj_loaddata, section['loaddata'],
                                **context)
                if result.succeeded:   changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

        for manparam in sequence(section['manage']):
            log.change(u'manage: %s…' % manparam)
            result = runcmd('%s %s' % (cmds.dj_mancmd, manparam), **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

        for manparam in sequence(section['manage-once']):
            cmd = manparam.split()[0]
            tdir, fpath = donepath(cmds, 'done.django.manage-once', cmd, manparam)
            # test file
            result = runcmd(cmds.file_test, fpath, **context)
            if result.succeeded:
                log.skip(u'manage-once: %s… has been run already.', cmd)
            else:
                log.change(u'manage-once: %s…' % manparam[:30])
                result = runcmd('%s %s' % (cmds.dj_mancmd, manparam), **context)
                if result.succeeded:
                    changed += 1
                    errors += markdone(cmds, tdir, fpath, context)
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

    return changed, errors  # only one change

