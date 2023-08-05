# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Good hygene is important.

    ``folders:``
        Deletion of files under ``/tmp``, ``/var/tmp``, & ``/home/`` only.
    ``locales-except:``
        *"Unless you're working at the UN and administer a central server for
        all member states, it is difficult to conceive why you would
        need a system where all of these locales are installed."* |br|
        Similar to a one-time Debian locale-purge.
    ``packages:``
        Run appropriate package cleanup command(s).

    Example::

        - cleanup:
            packages: True
            locales-except: en en_US
            folders:  # use with caution
                - /tmp/stuff/*
                - /tmp/stuff2

'''
import logging

from fabric.api import env
from fabric.context_managers import cd
from fabric.contrib.files import exists as rexists
from voluptuous import Required as req

try:  from pave.lib import packages  # circular at schema import, mv to handle?
except ImportError: pass
from pave.utils import runcmd, eval_conditionals, err_cond
from pave.schema import conditionals_schema

log = logging.getLogger()
whitelist = ('/tmp/', '/var/tmp/', '/home/')
schema = {
    req('folders', default=[]):         [basestring],
    req('packages', default=True):      bool,
    'locales-except':                   basestring,
}
schema.update(conditionals_schema)

def handle(section, cmds, context):
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from this module
        return changed, errors

    for task in section:
        if task == 'packages':
            if section['packages']:
                chd, errs, mods = packages.cleanup(cmds, context)
                if chd:
                    log.change(u'packages: removed %s obsolete.', mods)
                elif not errs:
                    log.skip(u'packages: none to remove.')
                changed += chd; errors += errs

        elif task == 'locales-except':
            with cd(cmds.locale_dir):
                # check to see what is there now:
                before = runcmd(cmds.locale_test, **context)
                if before.failed:
                    log.error(before); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

                log.info(u'removing any extra locale files…')
                filespec = '|'.join(section[task].split())
                result = runcmd(cmds.locale_cln, filespec, **context)
                if result.succeeded:   pass  # changed += 1 # need to check if done
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

                # what's it look like afterward?
                after = runcmd(cmds.locale_test, **context)
                if after.succeeded:
                    if before == after:
                        log.skip('locales: before %s, after %s', before, after)
                    else:
                        log.change('locales: before %s, after %s', before, after)
                        changed +=1
                else:
                    log.error(after); errors += 1
                    if env.pave_raise_errs: raise RuntimeError


        elif task == 'folders':
            for folder in section[task]:
                if '../' not in folder:
                    permitted = False
                    for path in whitelist:  #  check
                        if folder.startswith(path):
                            permitted = True
                            break
                    if permitted:
                        if rexists(folder):
                            log.change('removing %s', folder)
                            result = runcmd('rm -rf %s', folder, **context)
                            if result.succeeded:   changed += 1
                            else:
                                log.error(result); errors += 1
                                if env.pave_raise_errs: raise RuntimeError
                        else:
                            log.skip('"%s" is already deleted.', folder)
                    else:
                        log.error('deletion of "%s" not permitted.', folder)
                        errors += 1
                        if env.pave_raise_errs: raise RuntimeError
        else: # should be done by schema
            log.error('unknown cleanup task "%s"', task);  errors += 1
            if env.pave_raise_errs: raise RuntimeError

    return changed, errors

