# -*- coding: utf-8 -*-
'''
    %%prog v%s - (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+
    Yet another config and deployment tool, leveraging fabric.

    %%prog [options]
'''
if True: # foldable
    import sys, os
    import copy, errno, logging, json, platform, string, traceback
    from os.path import dirname, join, expanduser
    from importlib import import_module
    from optparse import OptionParser
    from pprint import pformat

    import yaml
    from fabric.api import env, local, run, settings
    from fabric.exceptions import NetworkError
    from fabric.context_managers import hide, show
    from fabric.network import disconnect_all
    from fabric.tasks import execute
    from fabric.version import __version__ as fabver
    from voluptuous import Invalid as InvalidData

    from meta import __version__, __progname
    from logcfg import (console, ColorFmtr, EspeakHandler, ioLogger, log,
                        logfmt, start_file_log, SecshFilterD)

    _def_filename    = 'pave.yml'
    _def_encoding   = 'utf8'
    def_jobs        = 1
    pw_tries        = 3
    allvars         = {}
    opts            = None
    lcmds           = None

    try: # find a logging location
        import xdg.BaseDirectory  # modern linux
        tempdir = join(xdg.BaseDirectory.xdg_cache_home, __progname)
    except ImportError:
        xdg = None
        tempdir = join(expanduser('~'), '.cache', __progname)
    logdir = join(tempdir, 'logs')

    # some of these dependent on the values above
    import platforms
    from lib.keygen import keygen, check_ssh_config
    from schema import schema
    from targets import detect_range, expand_hostname_range
    from utils import ( AttrDict, ask_crypt, bold, getpwd, shplit, CURRENT,
                        get_cursor_pos, PaveSafeLoader, sequence, wait_key,
                        shell_error_map, safe_eval, VarTemplate )


def _expandstr(template, variables): # reusable
    return VarTemplate(template).substitute(variables)

def expandstr(self, node):   # expands vars
    'Yaml loader/constructor that expands variable strings.'
    if opts.brace_exp:
        if '{' in node.value and '}' in node.value:
            node.value = node.value.format(**allvars)
    else:
        if '%' in node.value:
            node.value = _expandstr(node.value, allvars)

    return self.construct_scalar(node)


def expand_targets(targets, groups):
    'Convert group names into targets and add them to the list.'
    result = []
    for target in targets:
        if target in groups:
            target = groups[target]
        if isinstance(target, list):
            result.extend(expand_targets(target, groups))
        else:
            match = detect_range(target)
            if match:   result.extend(expand_hostname_range(match))
            else:       result.append(target)
    return result


def fatal_exit(msg, exitcode, parser=None):
    'Convenience function to log and exit on fatal error.'
    if parser:  parser.print_help(); print
    log.fatal(msg); print
    logging.shutdown()
    sys.exit(exitcode)


def _fmt_log(shell, code):
    msg = 'inpsector %s exited with %s - %s'
    msg = msg % (shell.split()[0], code, shell_error_map.get(code, 'Unknown'))
    return msg


def get(cfgdata, path, offset=0):
    ''' An xpath-like yaml data grabber.
        Looks at these in order, last one wins:

            - Schema default
            - Config file
            - Command line
    '''
    # check command line, should be done better
    if path in opts.option:
        return opts.option[path]
    if path == '/main/targets' and opts.target:
        return opts.target
    if path == '/main/jobs' and opts.jobs > 1:
        return opts.jobs

    # check config file
    result = None
    rescfg = cfgdata
    names = path.split('/')[offset:]
    length = len(names)
    for i, name in enumerate(names):
        if name:
            if type(rescfg) is dict:
                if i == (length - 1):
                    rescfg = rescfg.get(name, None)
                else:
                    rescfg = rescfg.get(name, {})
            elif type(rescfg) is list:
                if rescfg:
                    if name == '*':
                        rescfg = tuple([ get(res, path, i+1) for res in rescfg ])
                    elif name.isdigit():
                        index = int(name)
                        if index < len(rescfg):
                            rescfg = rescfg[index]

    if rescfg is not None: # not in (None, {}, []): ?
        result = rescfg

    return result


def get_module(modname):
    '''Given a module name, find and load it.'''
    try:
        module = import_module('pave.lib.%s' % modname)
    except ImportError:     # look for third party modules
        module = import_module(modname)
    return module


def get_platform_cmds(pldata, local=False):
    'Given platform data, return the appropriate command class.'
    cmdobj = None
    sysname, vers = 'Linux', 'unknown'

    if pldata:
        # this doesn't happen early enough to make a difference:
        #~ allvars.update(pldata)
        if pldata.get('system') == 'Linux':
            distinfo = pldata.get('linux_dist')
            if len(distinfo) and distinfo[0]:  # list of 3 str
                sysname = distinfo[0].partition(' ')[0]  # cut from first space
                sysname = sysname.title()                # debian, grr...
            if len(distinfo) > 1 and distinfo[1]:
                vers = distinfo[1]
        else:
            sysname = pldata.get('system')
    if local:  log.debug('using a local %s system.' % sysname)
    else:      log.info('found a(n) %s system, version %s.' % (sysname, vers))

    # retrieve class
    vers = ''.join([ c  for c in vers  if c.isdigit() ])  # clean up
    classname = sysname + vers
    while True:
        try:  cmdobj = getattr(platforms, classname)
        except AttributeError:
            if classname and classname[-1].isdigit():
                classname = classname[:-1]  # chomp and try again
                continue
        break

    if cmdobj is None:
        fatal_exit('"%s/%s" is not yet supported.' % (pldata.get('system'),
                   ' '.join(pldata.get('linux_dist', []))), os.EX_UNAVAILABLE)
    return cmdobj


def load_data(opts, args):
    ''' Load the pavefile and expand any variables found.
    '''
    filedat, data = '', {}
    try:  # read in pavefile, first parse
        with file(opts.filename) as f:
            filedat = f.read()  # cache for later
            data = yaml.load(filedat, Loader=PaveSafeLoader)
        if not data:
            fatal_exit('pavefile "%s" empty.' % opts.filename, os.EX_DATAERR)

        # look at passwords early, so they can be expandable variables
        # look for them in includes
        includes = data.get('main', {}).get('include', [])
        includedat = ''
        if isinstance(includes, basestring):
            includes = shplit(unicode(includes))
        for incfname in includes:
            with file(incfname) as f:
                incfdat = f.read()
                pwds = yaml.load(incfdat,
                                 Loader=PaveSafeLoader).get('passwords', [])
                if pwds: data.update({'passwords': pwds})
                includedat += incfdat + '\n'  # cache for later

        # validate passwords section
        plines = schema({'main': {}, 'passwords': data.get('passwords', [])})
        plines = plines.get('passwords', [])
        # parse passwords section
        env.pave_passwords = {}
        for i, item in enumerate(plines):
            if isinstance(item, basestring):
                pargs = shplit(unicode(item))
                cmd, name = pargs[0], pargs[1]
                if cmd == 'ask':
                    prompt = ' '.join(pargs[2:])
                    passwd = getpwd(prompt, tries=pw_tries)
                    if not passwd:
                        raise EOFError, 'Password empty, exiting.'
                elif cmd == 'set':
                    passwd = pargs[2]
                env.pave_passwords[name] = passwd   # save to fabric's env
                allvars['pwd_' + name] = passwd     # to vars as well
                if name == 'password': env.password = passwd
            elif type(item) is dict:
                env.passwords = item
                env.pave_passwords = item

        # expand vars in vars section once
        allvars.update(data.get('vars', {}))
        for key, val in allvars.iteritems():
            if isinstance(val, basestring):
                if opts.brace_exp:
                    if '{' in val:   allvars[key] = val.format(**allvars)
                else:
                    if '%' in val:  allvars[key] = _expandstr(val, allvars)
        # command line override?
        for var in opts.var:
            allvars[var[0]] = var[1]
        env.pave_vars = allvars

        # look at pavefile a second time with var expander loaded
        if allvars:
            PaveSafeLoader.add_constructor(u'tag:yaml.org,2002:str', expandstr)
            # is it a template?
            if opts.filename.lower().endswith('.j2'):
                from jinja2 import Template
                template = Template(filedat)
                filedat = template.render(**allvars)
            data = yaml.load(filedat, Loader=PaveSafeLoader)

        # handle includes again
        if includedat:
            data.update(yaml.load(includedat, Loader=PaveSafeLoader))

        # rm password section from logging below; pwds attached to env obj
        for pline in data.get('passwords', []):
            if pline.startswith('set '):
                data.pop('passwords', None); break

        # do the full schema check
        data = schema(data)

        # printen Sie
        log.debug('schema:\n' + pformat(schema.schema))
        log.debug('pavefile:\n' + pformat(data))
        return data

    except EOFError, e:
        log.warn(str(e))
        sys.exit(os.EX_TEMPFAIL)
    except KeyboardInterrupt, e:
        print;  log.warn('Keyboard interrupt, exiting.')
        sys.exit(os.EX_TEMPFAIL)
    except InvalidData, e:
        fatal_exit('Invalid Data: %s - %s' % (e.msg,
                   '/' + '/'.join([unicode(p) for p in e.path])),os.EX_DATAERR)
    except KeyError, e:
        fatal_exit('pavefile: variable "%s" doesn\'t exist.' % e.args,
                    os.EX_DATAERR)
    except yaml.YAMLError, e:
        msg = ' '.join(unicode(e).split()) # normalize whitespace
        fatal_exit('yaml.%s: %s' % (e.__class__.__name__, msg), os.EX_DATAERR)
    except ImportError:
        fatal_exit('using jinja2 pavefile but jinja not found.', os.EX_CONFIG)
    except Exception, e:
        log.exc('%s:\n  %s', e.__class__.__name__, traceback.format_exc())
        fatal_exit('Exiting.', os.EX_SOFTWARE)


def main(opts, args):
    'Start paving.'
    exit_status = os.EX_OK
    # read the plans
    data = load_data(opts, args)

    # start your engines
    data, inspectors = prep_environ(data, opts)
    if opts.test:  return  # quit early
    results = {}
    context = AttrDict( use_sudo=get(data, '/main/sudo'),
                        sudo_user=get(data, '/main/sudo-user') )
    orig_stdout, orig_stderr = sys.stdout, sys.stderr # save for later
    sys.stdout = ioLogger(log, 'debug')               # redirect stdout to logs
    sys.stderr = ioLogger(log, 'debug')               # redirect stderr to logs
    everything = ('aborts', 'debug', 'running', 'status', 'stderr', 'stdout',
                    'user', 'warnings')  # fabric everything not everything :/
    log.debug(u'starting fabric.execute() on steamroll…')
    locfhandler = log.handlers.pop()  # don't double log to localhost

    # experimental use of tasks from external fabfile
    if 'fab-tasks' in data:  # start fabric
        from fabric import state
        from fabric.main import find_fabfile, load_fabfile, parse_arguments

        fabfile = find_fabfile()
        if not fabfile:
            fatal_exit('Couldn\'t find any fabfiles!', os.EX_IOERR)
        _, callables, _ = load_fabfile(fabfile)
        state.commands.update(callables)

        for i, fabtask in enumerate(data.get('fab-tasks', [])):
            if type(fabtask) is dict:
                fabargs = ':'.join(fabtask.items()[0])
                fabargs = parse_arguments([fabargs])[0]
            else:
                fabargs = (fabtask, [], {}, [], [], [])

            name, fargs, kwargs, hosts, roles, excludes = fabargs
            log.info('%02i %s', i, name, extra=dict(module='fab-task'))
            log.debug('args: %s', fabargs, extra=dict(module='fab-task'))
            execute(name, hosts=hosts, roles=roles, exclude_hosts=excludes,
                    *fargs, **kwargs)

    if 'tasks' in data:  # start fabric
        with show(*everything):
            try:
                results = execute(steamroll, data, inspectors, context)
            except KeyboardInterrupt:
                if get_cursor_pos() > 1: print  # prevent log on existing line
                log.warn(u'Killed by Ctrl-C, shutting down…')
                exit_status = 130  # from bash docs

            log.addHandler(locfhandler)
            disconnect_all()

    # exit stage left
    log.note('results %s', results)
    sys.stdout, sys.stderr = orig_stdout, orig_stderr # restore
    logging.shutdown()
    return exit_status


def prep_environ(data, opts):
    'Prepare execution environment according to options given.'
    # look at tasks
    if opts.command:    # override
        data['tasks'] = [opts.command]
    elif not (get(data, '/tasks') or get(data, '/fab-tasks')):
        fatal_exit('No tasks or fab-tasks section found.', os.EX_DATAERR)
    elif opts.select:  # filter tasks, see setup() for err checking
        tasks = data['tasks']
        data['_orig_task_length'] = len(tasks) # save for later
        try:  tasks = safe_eval('tasks[%s]' % opts.select, tasks=tasks)
        except IndexError:
            fatal_exit('-s selection index out of range.', os.EX_USAGE)
        if not tasks:
            fatal_exit('-s no tasks left, holmes.', os.EX_USAGE)
        data['tasks'] = sequence(tasks)

    # explicitly set fabric env keys
    env.warn_only =  True  # handle errors and display to user
    for key, val in (get(data, '/main/env') or {}).iteritems():
        setattr(env, key, val)

    # add to module path
    path = get(data, '/main/sys.path')
    if path:
        if isinstance(path, basestring):
            path = path.split(':')
        sys.path += path

    # set logging folder:
    log_to = get(data, '/main/log-to')
    if log_to:
        global logdir
        logdir = expanduser(log_to)

    # find and expand targeted hosts
    targets = get(data, '/main/targets')
    if isinstance(targets, basestring):
        targets = targets.split()
    if not targets:
        fatal_exit('No targets found.', os.EX_CONFIG)
    targets = expand_targets(targets, data.get('target-groups', []))

    # misc
    env.hosts = targets
    env.pave_bak = get(data, '/main/bak-files')
    env.pave_platform_details = {}
    user = get(data, '/main/user')
    if user and user != CURRENT:
        env.user = user

    # load and minimize inspector script
    inspectors = []
    mode = get(data, '/main/inspect')
    if mode:
        if mode is True:
            filenames = ['inspector.py', 'inspector.sh']
        else:
            filenames = ['inspector.' + mode]
        for filename in filenames:
            script = ''
            with file(join(dirname(__file__), filename)) as f:
                for line in f:  # minimize
                    if line.isspace() or line.startswith('#'):
                        continue
                    script += line.replace('    ', ' ')

            if filename.endswith('.py'):        # add two inspectors to handle
                shell, shellcode = 'python2 -c', script      # lack of python2
                inspectors.append((shell, shellcode))
                shell, shellcode = 'python -c', script
            else:
                shell, shellcode = 'sh -c', script
            inspectors.append((shell, shellcode))

    # set fabric opts
    env.pave_raise_errs = not get(data, '/main/warn-only')
    # not sure if a good idea, but can't see why this would not be set:
    # tell sudo to set the HOME env variable when run as user:
    env.sudo_prefix = "sudo -SHp '%(sudo_prompt)s' " % env
    jobs = get(data, '/main/jobs')
    if jobs > 1:
        log.info('multiple jobs enabled (%s)', jobs)
        env.parallel = True
        env.pool_size = jobs

    # try this... still doesn't separate stderr
    env.combine_stderr = False

    # configure ssh
    keygen()  # generate a local key if there is none
    check_ssh_config()

    return data, inspectors


def setup():
    'Parse command-line, set up logging, create temp folders.'
    global opts
    parser = OptionParser(usage=__doc__.rstrip() % __version__,
                          version=__version__)
    parser.add_option('-b', '--brace-exp', action='store_true',
        help='Use string.format-style brace expansion instead of printf.')
    parser.add_option('-c', '--command', metavar='STR',
        help='Override pavefile tasks with an ad hoc command.')
    parser.add_option('-f', '--filename', metavar='NAME',
        default='.%s%s' % (os.sep, _def_filename),
        help='Use an input file besides %default.')
    parser.add_option('-i', '--interactive', action='store_true',
        help='Stop and ask whether to run each task group.')
    parser.add_option('-j', '--jobs', metavar='#', default=def_jobs,type='int',
        help='Run pave tasks in parallel with the given pool size.')
    parser.add_option('-o', '--option', metavar='N V', action='append',nargs=2,
        help='Override a pavefile option.', default=[])
    parser.add_option('-s', '--select', metavar='#', help='Select task groups'
        ' to run, instead of all. (0-based slice syntax, # or #:#).')
    parser.add_option('-S', '--skel', action='store_true',
        help='Output a "skeleton" pavefile to get started on.')
    parser.add_option('-t', '--target', metavar='T',action='append',default=[],
        help='Override targets with this host or group.  Multiple accepted.')
    parser.add_option('-q', '--quiet', action='store_true',
        help='Silence routine output, allowing warnings and errors.  ' +
             'Overrides verbose.')
    parser.add_option('-v', '--var', metavar=' N V', action='append', nargs=2,
        help='Override a pavefile variable.', default=[])
    parser.add_option('-V', '--verbose', action='store_true',
        help='Enable overwhelmingly verbose debugging output.')

    choices=('auto', 'on', 'off')
    parser.add_option('--color', type='choice', default='auto',
        choices=choices, metavar='CHOICE',
        help='Message coloring/icons %s.' % (choices,))
    parser.add_option('--crypt', action='store_true',
        help='Ask for a password, print its hash and exit. For use with users:'
             ' module in the pavefile.')
    parser.add_option('--speak', action='store_true',
        help='Talk to me, holmes.')
    parser.add_option('--test', action='store_true',
        help='Test mode: parse and validate, skip execution.')

    try:
        opts, args = parser.parse_args()
    except SystemExit:
        sys.exit(os.EX_USAGE)

    # configure console logging
    if opts.quiet or opts.jobs > 1:
        console.setLevel(logging.WARNING)
    else:
        console.setLevel((logging.DEBUG if opts.verbose else logging.INFO))
        if console.level <= logging.DEBUG:
            console.addFilter(SecshFilterD())
    if opts.color == 'auto':
        if console.stream.isatty():     fmtr = ColorFmtr(logfmt)
        else:                           fmtr = logging.Formatter(logfmt)
    elif opts.color in 'on':            fmtr = ColorFmtr(logfmt)
    else:                               fmtr = logging.Formatter(logfmt)
    console.setFormatter(fmtr)

    opts.option =  dict(opts.option)
    if opts.crypt:
        result = ask_crypt()
        print
        if result:
            print >> sys.stderr, '    ', result, '\n'
        sys.exit()

    if opts.skel: # output skeleton file
        import shutil
        dest = join(os.getcwd(), _def_filename)
        if os.path.exists(dest):
            fatal_exit('"%s" already exists.' % dest, os.EX_CANTCREAT)
        try:
            shutil.copyfile(join(dirname(__file__), 'skeleton.yml'), dest)
            log.info('created "%s".', _def_filename)
        except IOError, e:
            fatal_exit('pavefile not created: ' + e.strerror, os.EX_CANTCREAT)
        sys.exit()

    # error checking
    if not os.access(opts.filename, os.R_OK):
        fatal_exit('pavefile "%s" not found or not accessible.'
                    % opts.filename, os.EX_NOINPUT, parser)

    if opts.command and opts.select:
        fatal_exit('-c/--command and -s/--select cannot be used together.',
                    os.EX_USAGE, parser)
    if opts.interactive and opts.jobs > 1:
        fatal_exit('-i/--interactive and -j/--jobs cannot be used together.',
                    os.EX_USAGE, parser)
    if opts.select:
        charset = string.digits + '-' + ':'
        for char in opts.select:
            if char not in charset:
                fatal_exit('-s/--select: invalid character entered.',
                            os.EX_USAGE, parser)
        try:  safe_eval('t[%s]' % opts.select, t=[])
        except IndexError: pass
        except Exception, e:
            fatal_exit('-s, --select: %s' % e, os.EX_USAGE, parser)

    # create temp folders
    folders = (tempdir, 0750), (logdir, 0750)
    for folder, perms in folders:
        try:
            os.makedirs(folder)  # perms incorrect w/makedirs
            if not xdg:
                os.chmod(folder, perms)
        except OSError, e:
            if e.errno == errno.EEXIST: pass
            else:
                fatal_exit("Can't create temp folder: %s" % e, os.EX_CANTCREAT)

    # more logging
    start_file_log(join(logdir, 'localhost'))
    if opts.jobs > 1:   logf = log.note  # promote message
    else:               logf = log.info
    logf('pave version %s, Python: %s, fabric: %s\n' +
         '                  pavefile: %s, logs: %s/logs',
        __version__, platform.python_version(), fabver, opts.filename, tempdir)
    if opts.speak:  # after versions
        log.addHandler(EspeakHandler())

    # check localhost
    with hide('stdout', 'running'):
        platdetails = local(platforms.OS.python %
                        join(dirname(__file__), 'inspector.py'), capture=True)
        if platdetails:
            log.debug(platdetails)
            platdetails = json.loads(platdetails)
            global lcmds
            lcmds = get_platform_cmds(platdetails, local=True)
        else:
            fatal_exit("Inspection of localhost failed." % e, os.EX_SOFTWARE)

    return opts, args


def steamroll(data, inspectors, context):
    '''Let's get rollin...'''
    hostlogh = start_file_log(join(logdir, env.host))
    tasks = data['tasks']
    numtasks = data.get('_orig_task_length') or len(tasks) # not working as expected
    log.note(u'paving %s@%s with %s tasks…', env.user, env.host, len(tasks))

    platdetails = None
    for inspector in inspectors:
        shell, shellcode = inspector
        with hide('running'):
            with settings(warn_only=True, shell=shell):
                try:
                    platdetails = run(shellcode)
                    if platdetails.failed:
                        log.warn(_fmt_log(shell, platdetails.return_code))
                        platdetails = None; continue
                    platdetails = json.loads(platdetails)
                    break
                except NetworkError, e:
                    log.fatal('%s: %s', e.__class__.__name__, e)
                    return 0, 1  # os.EX_NOHOST

    if platdetails is None:
        log.fatal('platform details not found, exiting.')
        return 0, 1

    context = context.copy()  # prevent context spills w/ change below
    context.encoding = platdetails.get('encoding', _def_encoding)
    cmds = get_platform_cmds(platdetails)
    env.pave_platform_details[env.host_string] = platdetails    # make avail
    env.pave_platform = cmds                                    # to mods
    # var expansion for platform details could be done here

    results = []
    offset = 0
    if opts.select:  # fix task numbers
        offset = int(opts.select.partition(':')[0] or 0) # find start

    for i, task in enumerate(tasks):
        i = i + offset
        mycontext = context.copy()  # prevent context spills

        if isinstance(task, basestring):  # handle bare strings as "run" tasks
            mname, sectdata = 'run', task
            desc = mname + ': ' + sectdata[:25]
        elif type(task) is dict:
            task = copy.deepcopy(task)        # prevent mod issues
            mname, sectdata = task.items()[0] # grab the first and only
            desc = mname + ':'
        try:
            log.debug('=' * 60)
            if opts.interactive:
                msg = bold(u'Task group %02i/%02i: %s… [Y/n/a/q]? '
                           % (i, numtasks-1, desc))
                if opts.verbose:
                    print >> sys.stderr, msg,
                    sys.stderr.flush(interactive=True)
                else:
                    log.note(msg)
                res = wait_key(); print >> sys.stderr, res # to console
                if   res == 'q':  break
                elif res == 'n':  continue
                elif res == 'a':  opts.interactive = False
                else:             pass
            results.append(
                get_module(mname).handle(sectdata, cmds, mycontext)
            )
            log.debug('completed task group %s of %s', i, numtasks-1)
        except ImportError, e:
            log.error('could not find module named: %s', e.message.split()[-1])
            log.warn(u'%s shutting down early—error occurred.', env.host)
            results.append( (0,1) )  # add err
            break
        except RuntimeError, e:  # from modules, problem already logged.
            log.warn(u'%s shutting down early—error occurred.', env.host)
            results.append( (0,1) )  # add err
            break
        except Exception, e:
            if log.isEnabledFor(logging.DEBUG):
                log.exc('Uncaught %s:\n  %s' % (e.__class__.__name__,
                                         traceback.format_exc()) )
            else:  # normal means didn't work, perhaps bc of multiproc?
                t = traceback.extract_tb(sys.exc_info()[2])[-1]
                fname = '.' + os.sep + os.sep.join(t[0].split(os.sep)[-3:])
                log.exc( 'Uncaught %s: %s, line %s of %s' % (
                          e.__class__.__name__, e, t[1], fname) )
            log.warn(u'%s shutting down early—exception occurred.', env.host)
            results.append( (0,1) )  # add err
            break

    log.debug('disconnecting.')
    log.removeHandler(hostlogh)
    return sum( c for c,e in results ), sum( e for c,e in results )

