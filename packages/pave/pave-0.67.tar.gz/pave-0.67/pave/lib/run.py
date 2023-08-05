# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Executes a list of commands using the remote shell.  Each command may be:

    * A string
        A command that runs under the default user.
    * A mapping with one or more of the following members:
        | ``do: CMD_STRING``
        |     The command to run.
        | ``user: USERNAME``
        |     Run as another user.
        |     May be ``sudo`` (root), or a valid remote username.
        | ``title: TITLE``
        |     to document or hide long, ugly commands.
        | ``workdir: PATH`` set working directory.
        | ``local: <bool>`` runs it locally instead of remotely.

    See :ref:`cond_exec` for more details on ``if:`` and ``if-exec:``.

    .. note::

        While *not recommended* to set passwords via command-line tools for
        various reasons, tasks makes an attempt to hide them (vars starting
        with "``pwd_``") from standard logs.  Passwords will still be displayed
        in debug logs (and perhaps shell history) upon command-line execution.

    Example::

        - banner "Hello!"     # world

        # signal a change event and prevent errors from halting execution:
        - touch %filename && echo CHANGED || true
        - rm /etc/nginx/sites-enabled/default && echo CHANGED || echo SKIPPED

        # Even poor-er man's conditionals:
        - " [ '%mode' == 'qa' ] && echo 'QA install' "

        # more robust task definition:
        - run:
            - title: Nothing to see here...
              if-exec: test -f /foo
              do: echo "This is running under $USER (appuser)"
              user: appuser

'''
import logging

from fabric.api import env
from fabric.context_managers import cd
from voluptuous import Any

from pave.schema import conditionals_schema
from pave.utils import (runcmd, trunc, shell_error_map, sequence,
                        check_list_conditionals)

log = logging.getLogger()
subtask_schema = {
    'local': bool,
    'do': basestring,
    'user': basestring,
    'title': basestring,
    'workdir': basestring,
}
subtask_schema.update(conditionals_schema)

schema = [ Any(basestring, subtask_schema) ]


def make_title(title, command, pwds):
    if not title:
        title = trunc(command, 72).rstrip()
        for pwd in pwds:        # obscure passwords in std logs, broken?
            if pwd in title:
                title = title.replace(pwd, '****')
    return title


def handle(section, cmds, context, chatty=True):
    changed, errors = 0, 0
    context = context.copy()    # needs to be here; may be used by other mods
    context.chunking = False    # disable bracket splitting
    pwds = env.pave_passwords.keys()

    for i, command in enumerate(sequence(section)):
        title = ''
        local = None
        workdir = '.'
        mycon = context    # may change on each command and need to copy

        if type(command) is dict:
            title = command.get('title', title)
            workdir = command.get('workdir', workdir)
            local = command.get('local', None)
            user = command.get('user', None)

            cmdstr = command.get('do')
            if not cmdstr:
                log.error('task %s in section %s missing do: clause.',
                          i, __name__.split('.')[-1])
                errors += 1
                if env.pave_raise_errs:
                    raise RuntimeError

            mycon = context.copy()  # prevent context spill
            if local:
                mycon.local = True
            elif user == 'sudo':
                mycon.use_sudo = True
            elif user:
                mycon.use_sudo = True
                mycon.sudo_user = user

            # down here--tests need to be run as correct user, dir
            with cd(workdir):
                command = check_list_conditionals(command, mycon,
                                                module=__name__, replace=False)
            if not command: continue

            title = make_title(title, cmdstr, pwds)
        else:
            cmdstr = command
            title = make_title(title, cmdstr.partition('&&')[0], pwds)

        # execute
        with cd(workdir):
            if chatty:
                log.info(title if title.endswith(u'…') else title + u'…')
            result = runcmd(cmdstr, **mycon)
            if result.succeeded:
                if 'CHANGED' in result:             # if both, CHANGED wins
                    changed += 1
                    if chatty: log.change(title + u' » DONE.')
                elif result.endswith('SKIPPED'):
                    if chatty: log.skip(title)
                if local:
                    log.debug('local-output:\n' + result)
            else:
                msg = title + '\n            Full Error:\n'
                text = result.decode(context.encoding)
                log.debug(text)

                msg = title + '\n            Returned: '
                msg += '\n'.join( text.rstrip().rsplit('\n', 3)[1:] )
                msg += '\n            Exit code: %s, ' % result.return_code
                msg += shell_error_map.get(result.return_code, 'Unknown')
                log.error(msg); errors += 1
                if env.pave_raise_errs:
                    raise RuntimeError

    return changed, errors

