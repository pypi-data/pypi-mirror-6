# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Manage kernel parameters.  Saves to memory and disk.

    Example::

        - kernel:           # str || list || conditional
            - vm.swappiness = 10

'''
import logging

from fabric.api import env
from fabric.contrib.files import sed
from voluptuous import Any

from pave.schema import conditionals_schema
from pave.utils import runcmd, sequence, check_list_conditionals

log = logging.getLogger()
schema = Any(basestring, [basestring, conditionals_schema])


def handle(section, cmds, context):
    changed, errors = 0, 0

    for variable in sequence(section):
        thischanged = 0
        variable = check_list_conditionals(variable, context, module=__name__)
        if not variable: continue

        name, value = [ arg.strip() for arg in variable.split('=', 1) ]

        # get current param value
        inmemory = runcmd(cmds.krn_get_param % name)
        if inmemory.failed: errors += 1
        log.debug('current mem  value: %s = %s', name, inmemory)

        # needs to be changed?
        if inmemory == value:
            log.skip('current mem  value matches: %s=%s', name, inmemory)
        else:
            log.change('setting mem  value: %s to %s', name, value)
            result = runcmd(cmds.krn_set_param % (name + '=' + value),
                            **context)
            if result.succeeded: thischanged += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

        # get current value on-disk
        # grep found 0 succeeded, not found 1 failed
        ondisk = runcmd(cmds.krn_srch_file, name, cmds.krn_param_fnm)
        if ondisk.succeeded:  # found
            ondiskval = ondisk.split('\n')[-1].partition('=')[2].strip()
            log.debug('current disk value: %s = %s', name, ondiskval)
        else:
            ondiskval = ''
            log.debug('disk value not found: %s', name)

        if ondiskval == value:
            log.skip('current disk value matches: %s=%s', name, ondiskval)
        else:
            log.change('setting disk value: %s to %s', name, value)
            if ondisk.succeeded:  # this greps the file again, not efficient:
                # was found, needs to be changed
                result = sed(cmds.krn_param_fnm, cmds.krn_param_reg % name,
                             variable, use_sudo=context.get('use_sudo'))
                if result.succeeded:    thischanged += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError
            else:
                # not in file, add
                # append needs to be reimplemented, not enough info avail
                result = runcmd(cmds.file_append, variable, cmds.krn_param_fnm,
                                **context)
                if result.succeeded:  thischanged += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

        if thischanged:  # send one change per setting only
            changed += 1

    return changed, errors

