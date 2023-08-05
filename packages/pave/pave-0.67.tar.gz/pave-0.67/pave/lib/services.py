# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Manage system daemons/services.  Values are whitespace separated strings.

    ``restart:``, ``restart-fail:``
        restart will start the service if it was stopped, restart-fail will
        fail with an error if it was not running originally.

    .. note::

        Some daemon startup scripts are not written well and quit when the
        ssh session ends.  To prevent this from occurring, prepend the
        service name with "``nohup:``" as shown below.

    Example::

        - services:
            # the follwing two are temporary until reboot:
            running: hostname hwclock
            stopped: whoopsie
            # permanently; /packages/remove more reliable on ubuntu
            disabled: whoopsie
            restart: nohup:memcached

'''
import logging

from fabric.api import env, run
from fabric.contrib.files import exists as rexists
from voluptuous import Required

from pave.schema import conditionals_schema
from pave.utils import runcmd, eval_conditionals, err_cond


log = logging.getLogger()
val = basestring
req = lambda key: Required(key, default='')
schema = {
    req('running'): val, req('stopped'): val,       req('disabled'): val,
    req('restart'): val, req('restart-fail'): val,
}
schema.update(conditionals_schema)


def check_nohup(svcname):
    'look for a nohup:SVCNAME construct.'
    if ':' in svcname:
        nohup, _, svcname = svcname.partition(':')
        nohup += ' '
    else:
        nohup = ''
    return nohup, svcname


def handle(section, cmds, context):
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from this module
        return changed, errors

    # query current status
    services, running = {}, []
    svclist = runcmd(cmds.svc_lst)  # doesn't need to run as root
    if svclist.failed:
        log.error(svclist); errors += 1 # don't quit on test failure
    else:
        services = cmds.parse_svclist(svclist) # a dict
        sorted_services = sorted(services.items())
        if log.isEnabledFor(logging.DEBUG):
            svctxt = ', '.join([ ('%s:%s' % svc) for svc in sorted_services])
            log.debug('existing: %s, length:%s',  '{' + svctxt + '}',
                      len(services))
        running = [ s  for s,st in sorted_services  if st == 1 ]

    # loop over section, instead of below:
    shouldruns = section.get('running', '').split()
    for svcname in shouldruns:
        nohup, svcname = check_nohup(svcname)
        if svcname not in running:
            log.change('starting %s', svcname)
            result = runcmd(nohup + cmds.svc_start, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        elif svcname not in services:
            log.error('%s not installed.', svcname); errors += 1
        else:
            log.skip('%s already started', svcname)

    shouldstops = section.get('stopped', '').split()
    for svcname in shouldstops:
        if svcname in running:
            log.change('stopping %s', svcname)
            result = runcmd(cmds.svc_stop, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        elif svcname not in services:
            log.error('%s not installed.', svcname); errors += 1
        else:
            log.skip('%s already stopped.', svcname)

    shoulddiss = section.get('disabled', '').split()
    for svcname in shoulddiss:  # not entirely sure how this should work
        found = False
        if run('ls /etc/rc?.d/S*%s*' % svcname).succeeded:
            found = True
            log.change('disabling rc.d %s', svcname)
            result = runcmd(cmds.svc_disable, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        elif run('ls /etc/rc?.d/K*%s*' % svcname).succeeded:
            found = True
            log.skip('rc.d %s already disabled.', svcname)

        if hasattr(cmds, 'svc_disable_ups'):
            if (rexists('/etc/init/%s.disabled' % svcname) and not
                rexists('/etc/init/%s.conf' % svcname)):
                found = True
                log.skip('upstart job %s already disabled.', svcname)
            elif rexists('/etc/init/%s.conf' % svcname):
                found = True
                log.change('disabling upstart job %s', svcname)
                result = runcmd(cmds.svc_disable_ups, svcname, svcname,
                                svcname, **context)
                if result.succeeded:   changed += 1
                else:
                    log.error(result); errors += 1
                    if env.pave_raise_errs: raise RuntimeError

        if not found:
            log.error('%s not installed.', svcname); errors += 1
            if env.pave_raise_errs: raise RuntimeError

    shouldrests = section.get('restart-fail', '').split()
    for svcname in shouldrests:
        nohup, svcname = check_nohup(svcname)
        if svcname in running:
            log.change('restarting %s', svcname)
            result = runcmd(nohup + cmds.svc_restart, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        elif svcname not in services:
            log.error('%s not installed.', svcname); errors += 1
        else:
            log.error('%s not running, can\'t be restarted.', svcname);
            errors += 1
            if env.pave_raise_errs: raise RuntimeError

    shouldrests = section.get('restart', '').split()
    for svcname in shouldrests:
        nohup, svcname = check_nohup(svcname)
        if svcname in running:
            log.change('restarting %s', svcname)
            result = runcmd(nohup + cmds.svc_restart, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError
        elif svcname not in services:
            log.error('%s not installed.', svcname); errors += 1
        else:
            log.change('restart: starting stopped %s', svcname)
            result = runcmd(nohup + cmds.svc_start, svcname, **context)
            if result.succeeded:   changed += 1
            else:
                log.error(result); errors += 1
                if env.pave_raise_errs: raise RuntimeError

    return changed, errors

