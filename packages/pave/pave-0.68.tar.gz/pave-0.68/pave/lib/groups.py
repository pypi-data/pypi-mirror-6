# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Create operating system user groups.

    Example::

        - groups:           # str || list || conditional
            - appgroup
            - "dev:1100"    # how to set gid

            - if-exec: test -e /dev/cdrom
              do: cdrom
'''
import logging

from fabric.api import env
from fabric.context_managers import hide
from voluptuous import Any

from pave.schema import conditionals_schema
from pave.utils import runcmd, sequence, check_list_conditionals

log = logging.getLogger()
schema = Any(basestring, [basestring, conditionals_schema])


def handle(section, cmds, context):
    changed, errors = 0, 0
    context.chunking = True  # needed by these commands

    # find existing:
    with hide('stdout'):  # useless text
        existing = runcmd(cmds.grp_lst)  # doesn't need to run as root
    if existing.failed:  errors += 1
    if existing:
        existing = existing.split()
    log.debug('existing groups: %s', existing)

    for group in sequence(section):
        group = check_list_conditionals(group, context, module=__name__)
        if not group: continue

        mycon = context.copy() # prevent context spill
        if ':' in group:
            group, mycon.gid = group.split(':', 1)

        if group in existing:
            log.skip('"%s" already exists.', group)
        else:
            log.change('creating group: %s', group)
            result = runcmd(cmds.grp_add, group, **mycon)

            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    return changed, errors

