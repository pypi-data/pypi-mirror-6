# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Manage local/remote ssh keys and their generation.

    ``remote:``
        Generates a key at the remote host under the given username.

    ``copy-id:``
        Copies local keys to the remote host.

        Values may be a single or list of Boolean
        (True copies the public key of the local user to the authorized keys
        file of the remote user),
        or string of two arguments containing the local file
        (.pub appended automatically) and the remote user.

    Example::

        - keygen:
            remote: "%sitename"             # quotes not required but
            copy-id:                        # fixes syntax highlighting
                - True                          # default src dest
                - "%local_path.pub %user"       # specified

'''
import logging
from os.path import expandvars, expanduser, exists, dirname, join

from fabric.api import env
from fabric.operations import local
from voluptuous import Any, Required as req

from pave.schema import conditionals_schema
from pave.utils import runcmd, sequence, shplit, eval_conditionals, err_cond

# defaults
_def_type = 'rsa'
_def_psfr = ''

log = logging.getLogger()
schema = {
    req('copy-id', default=True):           Any(bool, basestring,
                                                [basestring, bool]),
    req('remote', default=None):            Any(None, basestring),
    req('type', default=_def_type):         basestring,
    req('passphrase', default=_def_psfr):   basestring,
}
schema.update(conditionals_schema)

def keygen(type=_def_type, passphrase=_def_psfr, **context):
    'Generate ssh keys locally.'
    from pave.main import lcmds
    locpath = expandvars(lcmds.ssh_keypath % type)

    # check just the dirname in case the user already has a different type key.
    if exists(dirname(locpath)):
        log.debug('Found local .ssh folder at "%s".', dirname(locpath))
    else:
        cmdstr = lcmds.ssh_keygen % ( type, locpath, passphrase)
        log.note('Generating local ssh keys with: %r', cmdstr)
        result = local(cmdstr, capture=True)
        if result.failed:
            log.error(result)
            if env.pave_raise_errs: raise RuntimeError

def check_ssh_config():
    'Check for config locally.'
    from pave.main import lcmds
    cfgpath = join(dirname(expandvars(lcmds.ssh_keypath)), 'config')
    if exists(cfgpath):
        log.debug('"%s" found, using ssh config.', cfgpath)
        env.use_ssh_config = True
    else:
        log.debug('"%s" not found, not using ssh config.', cfgpath)


def handle(section, cmds, context):
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from this module
        return changed, errors

    from pave.main import lcmds

    for copyid in sequence(section['copy-id']):
        if copyid:
            remakf = cmds.ssh_akfile
            remdir = dirname(remakf)
            mycon = context.copy()
            if copyid is True:
                locbase = expandvars(lcmds.ssh_keypath % section['type'])
                mycon.use_sudo, remusr = False, ''
            else:
                locbase, remusr = shplit(copyid)
                locbase = expanduser(locbase)
                mycon.use_sudo = True
                mycon.sudo_user = remusr
            # ensure we get the public key file
            locpath = (locbase if locbase.endswith('.pub') else locbase+'.pub')

            result = runcmd(cmds.dir_test, remdir, **mycon)
            if result.succeeded:
                log.skip('copy-id: .ssh folder already created. %s', remusr)
            else:
                log.change('copy-id: creating .ssh %s', remusr)
                result = runcmd('mkdir -p %s', remdir, **mycon)
                result = runcmd('chmod 700 %s', remdir, **mycon)
                if result.succeeded:   changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

            with file(locpath) as f:
                for line in f:
                    line = line.rstrip()

                    result = runcmd(cmds.file_search, line, remakf, **mycon)
                    if result.succeeded:
                        log.skip('copy-id: local key found at remote host.')
                    else:
                        log.change('copy-id: adding key to remote host.')
                        result = runcmd(cmds.file_append, line, remakf,**mycon)
                        if result.succeeded:  changed += 1
                        else:
                            log.error(result); errors += 1
                            if env.pave_raise_errs: raise RuntimeError

    for username in sequence(section['remote']):
        if username:
            mycon = context.copy()
            mycon.sudo_user = username
            mycon.use_sudo = True
            pkpath = cmds.ssh_keypath % section['type']
            result = runcmd(cmds.file_test, pkpath, **mycon)
            if result.succeeded:
                log.skip('remote: remote key found.')
            else:  # file doesn't exist
                log.change('remote: keygen for user %s.' % username)
                result = runcmd(cmds.ssh_keygen, section['type'], pkpath,
                                section['passphrase'], **mycon)
                if result.succeeded:  changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

    return changed, errors

