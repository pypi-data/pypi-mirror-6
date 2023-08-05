# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
'''
    Configure the remote system.  Also handles templating, see below.

    ``render:``
        Renders a template to a local file, which is then uploaded to host.

        ``engine:``
            The templating language, such as python (printf|Template|format),
            or the executable name of an external package, e.g: ``jinja2``

    ``render-remote:``
        Simple remote "templating" with sed.

    Example::

        - configure:            # str || list accepted on all sub-tasks below:
            create:  # file or folder/
                - foo.conf
                - /tmp/project/

            append:  # text remotefname
                Answer=42 %rc

            comment: # [comment char] from-regex remote-fname
                - ' "insecure on" %rcfile '

            replace: # from-regex to remote-fname
                - ^foo$ bar %rcfile
                # note that because of yaml syntax and splitting, two layers
                # of quoting or blocks may be needed when backslashes used:
                - >
                    '^foo\s*$' bar %rcfile

            render: # engine [extra-vars] local-template remote-fname
                - printf swappiness=50 examples/printf_template.txt %rc2
                - format FOO=BAR       examples/format_template.txt %rc3

            render-remote: # [vars] remote-source remote-dest
                - INSTANCE_NUM=1 %sitecfg /etc/init/%svcname.conf

            update: # copy a file into place if newer, SRC DEST
                - ~/%sitename/cfg/celeryd.conf /etc/init/celeryd.conf

            access: # mode user group remote-fname # use "" for empty
                - 0640 %user %user %rc2
'''
import os, logging, tempfile, traceback
from string import Template

from fabric.api import env
from fabric.operations import put
from fabric.contrib.files import sed, comment, exists as rexists
from voluptuous import Any, Required
try:
    import jinja2
except ImportError:
    jinja2 = None

from pave.utils import (runcmd, sequence, contains, backup, shplit, q,
                        eval_conditionals, err_cond)
from pave.schema import conditionals_schema


log = logging.getLogger()
fl = 20 # filename length
vsch = Any(basestring, [basestring])
req = lambda key: Required(key, default=[])
schema = {
    req('append'): vsch, req('comment'): vsch, req('replace'): vsch,
    req('render'): vsch, req('update'):  vsch, req('access'):  vsch,
    req('render-remote'): vsch, req('create'): vsch,
}
schema.update(conditionals_schema)


def _format_exc(text):
    return '\n          ' + '\n          '.join(text.split('\n'))


def render(engine, text, tvars):
    'Render templates.'
    from pave.main import tempdir # avoid circ. deps
    try:
        fd, tempfname = tempfile.mkstemp(dir=tempdir)
        log.debug('created tempfile at %s', tempfname)

        if engine == 'printf':
            result = text % tvars
        elif engine == 'format':
            result = text.format(**tvars)
        elif engine == 'Template':
            result = Template(text).substitute(**tvars)
        elif engine == 'jinja':
            if jinja2:  result = jinja2.Template(text).render(**tvars)
            else:       log.error('Jinja templating engine not installed!')

        if log.isEnabledFor(logging.DEBUG):
            log.debug(repr(result))
        os.write(fd, result.encode('utf8'))
        os.close(fd)
        return tempfname
    except KeyError, e:
        log.error('Missing given variable: %r', e.message)
    except Exception, e:
        log.error(_format_exc(traceback.format_exc(limit=5)))


def handle(section, cmds, context):
    # needs factoring into sep functions
    changed, errors = 0, 0
    if eval_conditionals(section, context) is False:
        log.skip(err_cond, '')  # log here to tag from this module
        return changed, errors

    context = context.copy()  # needs to be here; may be used by other mods
    context.pop('sudo_user', None)
    context.pop('encoding', None)
    context.pop('chunking', None)

    sections = sorted(section.keys())
    if 'access' in sections:            # move access to the back
        sections.remove('access')
        sections.append('access')

    for operation in sections:
        for task in sequence(section[operation]):
            log.debug(u'splitting %r…', task)     # to pinpoint shlex errs
            args = shplit(task)

            if operation == 'append':
                text, fname = args
                if contains(fname, text, **context):
                    log.skip(u'append: text %.20r… exists in "%s".', text,
                              fname[-fl:])
                else:
                    if rexists(fname):
                        # need to reimplement contains to avoid 2x exist check
                        if env.pave_bak: backup(fname, cmds, context)
                    log.change(u'appending text %.20r… to "…%s".', text,
                                fname[-fl:])
                    # more functional/efficient to implement append ourselves
                    if "'" in text: text = text.replace("'", r"\'")
                    result = runcmd(cmds.file_append, text, fname, **context)
                    if result.succeeded:   changed += 1
                    else:
                        log.error(result); errors += 1
                        if env.pave_raise_errs: raise RuntimeError

            elif operation == 'create':
                fname = args[0]
                if rexists(fname):
                    log.skip(u'create: %.40r… exists.', fname)
                else:
                    log.change(u'creating %.40r…', fname)
                    obj_create = (cmds.dir_create  if fname.endswith('/')
                                                   else cmds.file_create)
                    result = runcmd(obj_create, fname, **context)
                    if result.succeeded:   changed += 1
                    else:
                        log.error(result); errors += 1
                        if env.pave_raise_errs: raise RuntimeError

            elif operation == 'comment':  # comment and replace roughly the same
                if len(args) == 3:  char = args[-3]
                else:               char = '# '
                text, fname = args[-2], args[-1]
                after = char + text

                if contains(fname, after, **context):
                    log.skip(u'comment: "%s" has comment "%.10s…".',
                              fname[-fl:], after)
                else:
                    if contains(fname, text, **context):
                        if env.pave_bak: backup(fname, cmds, context)
                        log.change(u'commenting %.20r… in "%s".', text,
                                    fname[-fl:])
                        result = comment(fname, text, char=char, **context)
                        if result.succeeded:   changed += 1
                        else:
                            log.error(result); errors += 1
                            if env.pave_raise_errs: raise RuntimeError
                    else:
                        log.error(u'comment: text %.20r… not found in "%s".',
                                  text, fname[-fl:])
                        errors += 1
                        if env.pave_raise_errs: raise RuntimeError

            elif operation == 'replace':
                # this operation isn't very efficient
                before, after, fname = args
                if (contains(fname, after, fixed=True, **context) and
                    # when after is a subset of before
                    not contains(fname, before, **context)):
                    log.skip(u'replace: "%s" has text %.20r… .', fname[-fl:],
                              after)
                else:
                    if contains(fname, before,  **context):
                        if env.pave_bak: backup(fname, cmds, context)
                        log.change(u'replacing %.20r… in "%s".', before,
                                    fname[-fl:])
                        result = sed(fname, before, after,
                            backup=('' if env.pave_bak else '.bak'), **context)
                        if result.succeeded:   changed += 1
                        else:
                            log.error(result); errors += 1
                            if env.pave_raise_errs: raise RuntimeError
                    else:
                        log.error(u'replace: %.20r… not found in "%s".',
                                   before, fname[-fl:])
                        errors += 1
                        if env.pave_raise_errs: raise RuntimeError

            elif operation == 'render':  # check local file with schema
                remotefname = args[-1]
                if rexists(remotefname, **context):
                    log.skip('render: "%s" already exists.', remotefname[-fl:])
                else:
                    # no backup needed here
                    log.change('rendering to "%s".', remotefname[-fl:])
                    eng = args[0]
                    tvars = [ arg.split('=',1) for arg in args[1:-2] if '=' in arg ]
                    tmplfname = args[-2]

                    # local should overwrite global vars
                    tvars = dict(tvars)
                    copy = env.pave_vars.copy()
                    copy.update(tvars)
                    tvars = copy

                    with file(tmplfname) as f:
                        tempfname = render(eng, f.read(), tvars)
                        result = put(tempfname, remotefname)
                        if result.succeeded:
                            changed += 1
                            os.unlink(tempfname) # rm
                        else:
                            log.error(result); errors += 1
                            if env.pave_raise_errs: raise RuntimeError

            elif operation == 'render-remote':
                src, dest = args[-2], args[-1]

                result = runcmd(cmds.test_nt, src, dest, **context)
                if result.succeeded:
                    log.change(u'render: copying newer "…%s" to "…%s".',
                                src[-fl:], dest[-fl:])
                    command = 'sed '
                    tvars = [ arg.split('=',1) for arg in args[0:-2] if '=' in arg ]
                    for tvar in tvars:
                        command += "-e 's/%s/%s/g' " % tuple(tvar)
                    command += '%s > %s'

                    result = runcmd(command, q(src), q(dest), **context)
                    if result.succeeded:   changed += 1
                    else:
                        log.error(result); errors += 1
                        if env.pave_raise_errs: raise RuntimeError
                else:
                    log.skip(u'rend-rem: template "…%s" older than "…%s".',
                                src[-fl:], dest[-fl:])

            elif operation == 'update':
                src, dest = args

                result = runcmd(cmds.test_nt, src, dest, **context)
                if result.succeeded:
                    log.change(u'update: copying newer "…%s" to "…%s".',
                                src[-fl:], dest[:fl])

                    result = runcmd(cmds.file_update, q(src), q(dest),
                                    **context)
                    if result.succeeded:   changed += 1
                    else:
                        log.error(result); errors += 1
                        if env.pave_raise_errs: raise RuntimeError
                else:
                    log.skip(u'update: "…%s" older than "…%s".',
                                src[-fl:], dest[-fl:])

            elif operation == 'access':
                params = args[:-1]
                fn = args[-1]
                # get details
                results = runcmd(cmds.file_stat, fn)
                if results.succeeded:
                    cmode, cuser, cgrp = results.split()
                else:
                    log.error('access: unable to stat "%s"', fn[-fl:])
                    cmode, cuser, cgrp = '', '', ''
                    errors += 1; continue
                    # don't quit on test failure
                # no backups for metadata changes
                for i, param in enumerate(params):
                    if i == 0: # mode
                        mode = param.zfill(4)
                        cmode = cmode.zfill(4)
                        if mode == cmode:
                            log.skip('access: "%s" has mode %s', fn[-fl:], mode)
                        else:
                            log.change('access: changing "%s" to mode %s', fn[-fl:], mode)
                            res = runcmd(cmds.file_chmod, mode, fn, **context)
                            if res.succeeded:   changed += 1
                            else:
                                log.error(res); errors += 1
                                if env.pave_raise_errs: raise RuntimeError

                    elif i == 1: # user
                        if param == cuser:
                            log.skip('access: "%s" has owner %s', fn[-fl:], param)
                        else:
                            log.change('access: changing "%s" to owner %s', fn[-fl:], param)
                            res = runcmd(cmds.file_chown, param, fn, **context)
                            if res.succeeded:   changed += 1
                            else:
                                log.error(res); errors += 1
                                if env.pave_raise_errs: raise RuntimeError

                    elif i == 2: # group
                        if param == cgrp:
                            log.skip('access: "%s" has group %s', fn[-fl:], param)
                        else:
                            log.change('access: changing "%s" to group %s', fn[-fl:], param)
                            res = runcmd(cmds.file_chgrp, param, fn, **context)
                            if res.succeeded:   changed += 1
                            else:
                                log.error(res); errors += 1
                                if env.pave_raise_errs: raise RuntimeError
            else:
                log.warn('unknown operation "%s" given.')

    return changed, errors

