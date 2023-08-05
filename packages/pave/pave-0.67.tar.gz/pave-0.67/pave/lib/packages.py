# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Manage software packages.
    Packages names for ``install``, ``remove``, etc. are listed as
    whitespace-delimited strings.

    ``expiration:``
        The age in days after which the OS package index is considered
        to have expired, requiring action.

        To be a good neighbor, the default, 0 (= 24 hours) means packages
        won't be updated unless it has been a full day since the last update.
        A value of -1 forces action.
    ``inventory:``
        Make a list of installed packages to compare against.
    ``update/upgrade:``
        Update the system's package index, upgrade packages to latest release.
    ``upgrade-full:``
        Upgrade packages, even if it causes obsolete packages to be removed,
        or new packages to be installed, for example new kernel versions.
        e.g. Debian's "dist-upgrade".

    Example::

        - packages:
            if-platform: Debian
            install:
                sysvbanner python-pip
            # expiration: -1    # force attempt

'''
import logging

from fabric.api import env
from fabric.context_managers import hide
from voluptuous import Required as req

from pave.schema import conditionals_schema
from pave.utils import eval_conditionals, err_cond, runcmd

log = logging.getLogger()
schema = {
    req('expiration',   default=0):         int,
    req('install',      default=''):        basestring,
    req('inventory',    default=True):      bool,
    req('remove',       default=''):        basestring,
    req('update',       default=True):      bool,
    req('upgrade',      default=True):      bool,
    req('upgrade-full', default=True):      bool,
}
schema.update(conditionals_schema)


def cleanup(cmds, context):
    'Clean any mess left over by package installation.'
    changed, errors, removed = 0, 0, 0
    log.debug(u'package.cleanup…')
    result = runcmd(cmds.pkg_clean, **context)
    if result.failed:
        log.error(result); errors = 1
        if env.pave_raise_errs: raise RuntimeError

    elif hasattr(cmds, 'parse_pkg_output'):
        modifications = cmds.parse_pkg_output(result)
        removed = modifications[2]
        if any(modifications):
            changed += 1
    return changed, errors, removed


def _check_err(result):
    errs = 0
    if result.failed:
        log.error(result); errs += 1
        if env.pave_raise_errs: raise RuntimeError
    return errs


def handle(section, cmds, context):
    'Run the system package manager, and any others given.'
    changed, errors = 0, 0
    parse = hasattr(cmds, 'parse_pkg_output')
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from module
        return changed, errors

    # inventory existing packages
    inventory, pkginv = section['inventory'], [] # schema default
    log.debug('inventory: %s', inventory)
    if inventory:
        log.info('inventory: collecting installed pkg list.')
        with hide('stdout'):
            pkginv = runcmd(cmds.pkg_inventory)
            if pkginv.failed:
                log.error(pkginv); errors += 1
                if env.pave_raise_errs: raise RuntimeError
            pkginv = pkginv.split()
        if log.isEnabledFor(logging.DEBUG):
            log.debug('found %s packages.', len(pkginv))

    # update index
    update = section['update']
    expires = section['expiration']
    log.debug('update: %s  expiration: %s day(s)', update, expires)
    if update:
        # skip if done recently
        result = runcmd(cmds.pkg_update_time, expires, **context)
        if result.failed:
            log.error(result); errors += 1 # don't halt on test failure
        if result:  # string returned == is old enough
            log.change(u'update: OS pkg index… (takes a few mins).')
            result = runcmd(cmds.pkg_update, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        else:
            log.skip(u'update: occurred recently.')

    # save last pkg modification time
    if not parse:
        lasttime = runcmd(cmds.pkg_stat_mtime, **context)
        errors += _check_err(lasttime)

    def handle_operation(cmd, name, text):
        ''' Repetitive code for each package-change operation.
            There are currently two strategies on how to discern if an
            upgrade happened.  Reading the output of the command, or
            checking mtime on the filesystem.  Not clear which is portable.
        '''
        chd, errs = 0, 0
        # try the operation
        result = runcmd(cmd, **context)
        errs += _check_err(result)

        if parse:
            changes = cmds.parse_pkg_output(result)
            log.debug('parse: output %s', changes)
            changes = any(changes)
        else:
            thistime = runcmd(cmds.pkg_stat_mtime, **context)  # look again
            errs += _check_err(thistime)
            if str(lasttime) == str(thistime):
                changes = True

        if changes:
            log.change('%s: %s.', name, text);  chd += 1
        else:
            log.skip('%s: %snot %s.', name, (inventory or 'oops '), text)
        return chd, errs

    # remove: should be before upgrade, so removed aren't upgraded.
    pkgstr = section['remove']
    log.debug('remove: %r', pkgstr)
    if pkgstr:
        if inventory:
            pkgstr = ' '.join([ p  for p in pkgstr.split()  if p in pkginv ])
        if pkgstr:
            log.info(u'remove: %s…', pkgstr)
            cmdstr = cmds.pkg_remove % pkgstr
            chd, errs = handle_operation(cmdstr, 'remove', str(pkgstr))
            changed += chd; errors += errs
        else:
            log.skip(u'remove: NADA—inventory complete.')

    # upgrade
    upgrade = section['upgrade']
    log.debug('upgrade: %s', upgrade)
    if upgrade:
        # skip if done recently
        result = runcmd(cmds.pkg_upgrd_time, expires, **context)
        if result.failed:
            log.error(result); errors += 1 # don't halt on test failure

        if result:  # True/string == is old enough
            log.info(u'upgrade: OS pkgs… (may take a few mins).')
            if (section.get('upgrade-full') and
                getattr(cmds, 'pkg_upgrd_full', None)):
                upgrd_cmd = cmds.pkg_upgrd_full
            else:
                upgrd_cmd = cmds.pkg_upgrade

            chd, errs = handle_operation(upgrd_cmd, 'upgrade', 'done')
            changed += chd; errors += errs
        else:
            log.skip(u'upgrade: occurred recently.')

    # install
    pkgstr = section['install']
    log.debug('install: %r', pkgstr)
    if pkgstr:
        if inventory:
            newpkgs = [ p for p in pkgstr.split() if p not in pkginv ]
            pkgstr = ' '.join(newpkgs)
        if pkgstr:
            log.info(u'install: %s pkgs… (may take a few mins).',
                      len(pkgstr.split()))
            cmdstr = cmds.pkg_install % pkgstr
            chd, errs = handle_operation(cmdstr, 'install', str(pkgstr))
            changed += chd; errors += errs
        else:
            log.skip(u'install: NADA—inventory complete.')

    return int(bool(changed)), errors  # only one change

