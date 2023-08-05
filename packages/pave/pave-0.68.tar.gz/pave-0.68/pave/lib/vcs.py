# -*- coding: utf-8 -*-
# (C) 2012-2013 Mike Miller.
# License: GNU GPLv3+
r'''
    Deploy code with this version control helper.
    $VCS support must be installed beforehand, see the `packages`_ section.

    If the destination does not exist, an initial checkout is done.
    If it does exist, the repository is updated to the latest version.

    Formats::

        - VCS_TYPE REPO_URL DEST EXTRA          # simple or
        - do: VCS_TYPE REPO_URL DEST EXTRA      # robust

    ``VCS_TYPE``:
        Version Control System, one of ``svn``, ``hg``, or ``git``.
    ``REPO_URL``:
        URL to repository.
    ``DEST``:
        Destination folder.
    ``EXTRA``:
        Extra command line parameters.
    ``do``:
        What to do.
    ``input``:
        Useful to automate interactive prompts.
    ``user:``:
        Execute vcs under this remote username.

    Example::

        - vcs:
            - do: hg %repo_base/appname ~%user/appname
              input: p\nn                           # interactive answer
              user: %user

'''
from os.path import dirname, basename, join
import logging

from fabric.contrib.files import exists as rexists
from voluptuous import Invalid, Any

from pave.schema import conditionals_schema
from pave.utils import shplit, check_list_conditionals


log = logging.getLogger()
pwds = []
vcmap = {
    'svn':  dict(checkout='checkout', update='update'),
    'hg':   dict(checkout='clone',    update='pull -u', chkupdate='incoming'),
    'git':  dict(checkout='clone',    update='pull'),
}
vcslist = vcmap.keys()

# trying to figure out the best way of doing this:
def min_two_tokens(v):
    'validate'
    tokens = v.split()
    length = len(tokens)
    if length < 3:
        raise  Invalid('Expected length of at least 3.')
    return v

def in_vclist(v):
    'validate'
    tokens = v.split()

    if tokens[0] not in vcslist:
        raise  Invalid('Unknown vcs: ', tokens[0])
    return v

#~ chkstr = All(basestring, min_two_tokens, in_vclist)  # broken :/
chkstr = basestring  # broken because of new input key
vcs_schema = {
    'input': basestring,
    'user': basestring,
}
vcs_schema.update(conditionals_schema)
schema = [Any(basestring, vcs_schema)]


def handle(section, cmds, context):
    changed, errors = 0, 0
    from pave.lib.run import handle as runhandle

    for i, directive in enumerate(section):
        inpstr = ''
        user = None
        mycon = context.copy()
        if type(directive) is dict:
            inpstr = directive.get('input', inpstr)
            user = directive.get('user', user)
            if not 'do' in directive:
                raise ValueError, 'no do: key.'  # should be caught in schema
            if user == 'sudo':
                mycon.use_sudo = True
            elif user:
                mycon.use_sudo = True
                mycon.sudo_user = user

        directive = check_list_conditionals(directive, mycon, module=__name__,
                                    replace=False)
        if not directive: continue

        tokens = shplit(directive.get('do'))
        dest = ('~' + user) if user else ''
        vcs = tokens[0]
        repo = tokens[1]
        reponame = (basename(repo) or 'repo') + ' ' # use repo if name lost
        if len(tokens) > 2:
            dest = join(dest, tokens[2])
        thisvcs = vcmap[vcs]
        exists = rexists(dest)

        if exists:
            log.info(u'%sexists, checking for updates…', reponame)
            if vcs == 'hg': # hg gives notice of updates on incoming, not pull
                command = '%s %s && %s %s' % (vcs, thisvcs['chkupdate'],
                                              vcs, thisvcs['update'])
            else:
                command = '%s %s' % (vcs, thisvcs['update'])
        else:               # checkout
            log.change(u'%smissing, performing checkout…', reponame)
            command = '%s %s %s %s' % (vcs, thisvcs['checkout'], repo, dest)
            dest = dirname(dest)

        if len(tokens) > 3:  # add any extra params to the end
            command += ' ' + ' '.join(tokens[3:])

        # need to feed input?
        if inpstr:
            command = ("echo -e '%s' | " % inpstr) + command

        # run each task separately so we can log the results as they happen.
        command += ' && echo CHANGED || true'
        task = {'do':command, 'workdir':dest, 'user':user}

        chd, errs = runhandle([task], cmds, mycon, chatty=False)
        if exists:
            if chd: log.change('repo updated.')
            else:   log.skip('no updates found.')
        changed += chd
        errors += errs

    return changed, errors

