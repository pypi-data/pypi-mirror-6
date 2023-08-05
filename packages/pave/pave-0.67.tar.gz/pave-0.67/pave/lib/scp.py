# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Copy files to and fro.  Given a source and destination, copy files.

    Notes:

    * By default a put (upload) is performed, but the direction can be
      specified as the first parameter.
    * Paths with whitespace must be quoted.
    * Destinations folders should end in a ``/`` character for efficiency,
      as doing so skips the need for several filesystem tests.
    * If sudo is enabled,
      relative paths/tildes will be interpreted (and files owned) by the
      root user.
      Therefore it is recommended that absolute remote paths be given.
    * Does not currently handle wildcards.
    * While this module is similar to using the scp command-line program it
      may not work identically.

    Example::

        - scp:
            - SRC DEST          # put
            - SRC DEST MODE     # put, w/ Unix octal mode or "same"
            - get SRC DEST

            # example conditional
            - if: inst_ssl == True
              do: put bundle.crt "%sitefldr/ssl/bundle.crt"

    Additional details:

    * `fabric.operations.get <http://docs.fabfile.org/en/latest/api/core/operations.html#fabric.operations.get>`_
    * `fabric.operations.put <http://docs.fabfile.org/en/latest/api/core/operations.html#fabric.operations.put>`_

'''
import logging
from os.path import basename, join

from fabric.api import env
from fabric.operations import get, local, put
from voluptuous import Invalid, All

from pave.schema import conditionals_schema
from pave.utils import q, runcmd, shplit, check_list_conditionals

log = logging.getLogger()


def check(v):
    'validate command lines.  Todo: should check if on disk.'
    tokens = shplit(v)
    length = len(tokens)
    if tokens[0] == 'get':
        if length != 3:
            raise Invalid('Expected length of 3.')
    else:
        if (length < 2) or (length > 4):
            raise  Invalid('Expected length of 2-4.')
        if length > 3 and '=' not in tokens[3]:
            raise Invalid('Expected mode=XXXX format.')
    return v
#~ subtask_schema = {basestring: All(basestring, check)}
subtask_schema = {basestring: basestring}
subtask_schema.update(conditionals_schema)

schema = [  All(basestring, check), subtask_schema ]


def tilde_helper(path1, path2):
    if path1.startswith('~'):
        path1 = '$HOME' + path1[1:]
    if path2.startswith('~'):
        path2 = '$HOME' + path2[1:]
    return path1, path2


def handle(section, cmds, context):
    changed, errors = 0, 0
    context.pop('sudo_user', None)
    context.pop('encoding', None)
    def hash_files(locfn, remfn):
        errors = 0
        result = runcmd(cmds.file_hash, remfn, **context)
        if result.succeeded:
            remhash = result.split()[0]
        else:
            log.error(result); errors += 1

        result = local(cmds.file_hash % locfn, capture=True)
        if result.succeeded:
            lochash = result.split()[0]
            log.debug('local hash: %s', lochash)
        else:
            log.error(result); errors += 1
        return lochash, remhash, errors


    for command in section:
        command = check_list_conditionals(command, context, module=__name__)
        if not command: continue

        args = shplit(command)
        if args[0] == 'put':
            mode = 'put'
            args = args[1:]
        elif args[0] == 'get':
            mode = 'get'
            args = args[1:]
        else:
            mode = 'put'

        if mode == 'put':
            mode, mycon = None, {}  # overloading mode, not a great idea
            if len(args) == 2:
                locfn, remfn = args
            elif len(args) == 3:
                locfn, remfn, mode = args
                mode = mode.partition('=')[2]
            locfn, remfn = tilde_helper(locfn, remfn)

            # check if file mode should be set
            if mode == 'same':
                mycon = context.copy()
                mycon.mirror_local_mode = True
                mode = None # reset to put default
            elif mode and mode.isdigit():
                mode = int(mode, 8)
                mycon = context
            else:
                mycon = context

            # if the remfn ends in /, add filename.
            lbase = basename(locfn)
            rbase = basename(remfn)
            if lbase and not rbase:
                remfn = join(remfn, lbase)

            # check for existing and identical file
            # don't halt on test failure
            if runcmd(cmds.file_exists, remfn, **context).succeeded:
                log.debug('"%s" found.', remfn)

                lochash, remhash = None, None
                if rbase:                  # is this a folder?
                    if runcmd(cmds.dir_test, remfn, **context).succeeded:
                        log.debug('"%s" is a folder.', remfn)
                        remfn = join(remfn, basename(locfn))

                        if runcmd(cmds.file_exists,remfn, **context).succeeded:
                            log.debug('"%s" found.', remfn)
                            lochash, remhash, e = hash_files(locfn, remfn)
                        else:
                            log.debug('remote file not found. %s', remfn)
                    else:
                        lochash, remhash, e = hash_files(locfn, remfn)
                else:
                    lochash, remhash, e = hash_files(locfn, remfn)

                if lochash and (lochash == remhash):
                    log.skip('put: not uploading identical file: %s.',q(locfn))
                    continue
            else:
                log.debug('remote file not found. %s', remfn)

            # upload the file
            log.change('put: %s --> %s', q(locfn), q(remfn))
            try:
                result = put(locfn, remfn, mode=mode, **mycon)  # returns list
            except ValueError, e:  # :/
                log.error(str(e)); errors += 1
                if env.pave_raise_errs: raise RuntimeError
            if result.succeeded:  changed += 1
            else:
                log.error('put failed--check permissions.'); errors += 1
                if env.pave_raise_errs: raise RuntimeError

        elif mode == 'get':
            remfn, locfn = args
            locfn, remfn = tilde_helper(locfn, remfn)
            # copy filename to remote if nec.
            lbase = basename(locfn)
            rbase = basename(remfn)
            if rbase and not lbase:
                locfn = join(locfn, rbase)

            # check for existing and identical file, dirs not yet supported
            # don't halt on test failure
            if local(cmds.file_test % locfn, capture=True).succeeded:
                remhash, lochash = None, None
                result = runcmd(cmds.file_hash, remfn, **context)
                if result.succeeded:
                    remhash = result.split()[0]
                else:
                    log.error(result); errors += 1

                result = local(cmds.file_hash % locfn, capture=True)
                if result.succeeded:
                    lochash = result.split()[0]
                else:
                    log.error(result); errors += 1

                if lochash and (lochash == remhash):
                    log.skip('get: not downloading identical file: ' +
                             '%s.', q(remfn))
                    continue
            else:
                log.debug('local file not found. %s', locfn)

            # download the file
            log.change('get: %s <--- %s', q(locfn), q(remfn))
            result = get(remfn, locfn)  # returns a list
            if result.succeeded:  changed += 1
            else:
                log.error('get failed--check permissions.'); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    return changed, errors

