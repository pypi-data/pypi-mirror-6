# -*- coding: utf-8 -*-
'''
    (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+

    A grab bag of assorted stuff.
'''
import sys, logging, hashlib, re, random, string
from os.path import join
from getpass import getpass
from pipes import quote  # use shlex in py 3.3+
from platform import python_version_tuple
from crypt import crypt as _crypt

from yaml import SafeLoader
from fabric.api import env, local, run, sudo
from fabric.contrib.files import exists as rexists, _escape_for_regex

from meta import __progname
import platforms

# shlex & unicode :/
if python_version_tuple() < ('2', '7', '3'):
    from pave.uni_shlex import split as shplit
else:
    from shlex import split as shplit
# wait key
try:                    # Win32
    from msvcrt import getch as _getch
except ImportError:     # UNIX
    def _getch():
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

log = logging.getLogger()
CURRENT = 'CURRENT'
shell_error_map = {  # from bash docs
    1: 'General Error',
    2: 'Misuse of shell builtins',
    126: 'Command invoked cannot execute.',
    127: 'Command not found.',
    128: 'Invalid argument to exit',
    130: 'Script terminated by Control-C',
    255: 'Exit status out of range',
}
err_cond = 'test(s) %sreturned a False.'


class PaveSafeLoader(SafeLoader):
    ''' Disables the use of "%" chars as directive characters, so we don't have
        to quote so much. '''
    def check_directive(self):
        return False
    def check_plain(self):
        # removes % from the list
        ch = self.peek()
        return ch not in u'\0 \t\r\n\x85\u2028\u2029-?:,[]{}#&*!|>\'\"@`'  \
                or (self.peek(1) not in u'\0 \t\r\n\x85\u2028\u2029'
                    and (ch == u'-' or (not self.flow_level and ch in u'?:')))


class AttrDict(dict):
    'Dict that acts like an object.'
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def copy(self):
        return AttrDict(self)

# allow unicode var names in templating:
class _VarTemplateMetaclass(string._TemplateMetaclass):
    def __init__(cls, name, bases, dct):
        super(_VarTemplateMetaclass, cls).__init__(name, bases, dct)
        if 'pattern' in dct:
            pattern = cls.pattern
        else:
            pattern = _VarTemplateMetaclass.pattern % {
                'delim' : re.escape(cls.delimiter),
                'id'    : cls.idpattern }
        cls.pattern = re.compile(pattern, re.IGNORECASE|re.VERBOSE|re.UNICODE)

class VarTemplate(string.Template):
    __metaclass__ = _VarTemplateMetaclass
    delimiter = '%'
    idpattern = r'[_\w][_\w0-9]*'


def backup(fname, cmds, context):
    'Make a .orig backup of files we are going to modify.'
    bakname = fname + '.orig'
    if not rexists(bakname):
        result = runcmd(cmds.file_copy_q, fname, bakname, **context)
        if result.failed:
            log.warn(result)
            # if env.pave_raise_errs: raise RuntimeError # don't quit
        else:
            log.debug('backed up "%s" to .orig', fname)


def bold(text):
    'Add a bold attribute to given text.'
    return '\033[1m%s\033[0m' % text


# see logcfg for custom logger to change module name
def check_list_conditionals(item, context, module=None, replace=True,
                            force=False):
    ''' Check if item is a dictionary and if so eval conditionals.
        Helpful For list-based modules.
        Returns None if item should be skipped.
        Replace - replace object with its do/then clause.
    '''
    if type(item) is dict:
        if module:  extra = {'module': module.split('.')[-1]}
        else:       extra = None

        thenstr = item.get('then') or item.get('do')
        title = item.get('title')
        if force or thenstr:
            if eval_conditionals(item, context) is False:
                log.skip(err_cond, u'for "%.30s…" ' % (title or thenstr),
                         extra=extra)
                item = None
            elif replace:
                item = thenstr
        elif replace:           # this should be handled in schema
            log.error('conditional missing "then/do:" key.')
            raise RuntimeError
    return item


def contains(filename, text, exact=False, use_sudo=False, escape=False,
             fixed=False):
    ''' Copied from fabric--shows output and escape defaults to False.
        I may remove this and reimplement.
    '''
    func = use_sudo and sudo or run
    if escape:
        if not fixed:
            text = _escape_for_regex(text)
        if exact:
            text = '^%s$' % text
    else:
        text = text.replace("'", "\'")
    if fixed: fixed = '-F'
    else:     fixed = '-E'
    egrep_cmd = '''grep %s -- '%s' "%s" ''' % (fixed, text, filename)
    result = func(egrep_cmd, shell=False)
    log.debug('return code: %s', result.return_code)
    return result.succeeded


# crypt ----------------------------------------------------------------
def ask_crypt(tries=3):
    '''Asks for a password and returns crypt'd.'''
    for attempt in range(tries):
        passwd  = getpass('Enter password to crypt: ')
        passwd2 = getpass('Enter again to confirm:  ')
        if passwd == passwd2:
            if passwd:
                return crypt(passwd)
            else:
                log.warn('Passwords empty, exiting.')
                return
        else:
            log.error('Passwords do not match, try again.')
    log.critical('Fail.')


def crypt(passwd):
    'Crypt a password. See ``man crypt`` for details.'
    salt = [
        chr( random.randrange(1, 27) + random.choice((64,96)) ),
        chr( random.randrange(1, 27) + random.choice((64,96)) ),
        chr( random.randrange(10) + 48 ),
        chr( random.randrange(10) + 48 ),
    ]
    random.shuffle(salt)
    salt = ''.join(salt)
    encrypted = _crypt(passwd, '$5$' + salt)
    if log.isEnabledFor(logging.DEBUG):
        #~ log.debug('crypt.passwd: %r', passwd.encode('base64').rstrip())
        log.debug('crypt.salt: %r', salt)
        log.debug('crypt.result: %r', encrypted)
    return encrypted
# crypt ----------------------------------------------------------------

# done -----------------------------------------------------------------
def donepath(cmds, base, itemname, item):
    'Create and return a path to a "done" file.'
    path = base + '.%s.%s' % (itemname, md5(item))
    tdir = join(cmds.tempdir, __progname + '-$USER')
    fullpath = join(tdir, path)
    return tdir, fullpath


def markdone(cmds, tdir, path, context):
    'Mark a task as "done".'
    locerrs = 0
    result = runcmd(cmds.dir_create, tdir, **context)
    if result.failed:
        log.error(result); locerrs += 1
        if env.pave_raise_errs: raise RuntimeError
    result = runcmd(cmds.file_create, path, **context)
    if result.failed:
        log.error(result); locerrs += 1
        if env.pave_raise_errs: raise RuntimeError
    return locerrs
# done -----------------------------------------------------------------


def eval_conditionals(sectiondict, context):
    'If multiple tests, must all be true; boolean AND.'
    vartest = sectiondict.pop('if', None)
    exectest = sectiondict.pop('if-exec', None)
    plattest = sectiondict.pop('if-platform', None)

    if vartest:
        val1, comp, val2 = shplit(vartest)  # schema can check length
        val1 = unicode(env.pave_vars.get(val1, val1))
        vartest = _strcmp(val1, comp, val2)
        log.debug(u'var-test: %s » %s', (val1, comp, val2), vartest)

    if exectest:
        exectest = runcmd(exectest, **context).succeeded
        log.debug(u'exec-test: » %s', exectest)

    if plattest:
        tokens = shplit(plattest)
        if len(tokens) == 1:
            theclass = getattr(platforms, tokens[0], bool) # bool def as false
            plattest = issubclass(env.pave_platform, theclass)
            log.debug(u'platform-test: %s ⊇ %s » %s', env.pave_platform._get_fqn(),
                      theclass._get_fqn(), plattest)
        else:
            details = env.pave_platform_details.get(env.host_string, {})
            val1, comp, val2 = tokens
            val1 = unicode(safe_eval(val1, **details))
            plattest = _strcmp(val1, comp, val2)
            log.debug(u'platform-test: %s » %s', (val1, comp, val2), plattest)

    tests = [ t for t in (vartest, exectest, plattest) if t is not None ]
    return all(tests)


def fmtcmd(cmd, *args, **options):
    'format a command line given both arguments and options.'
    result = ''
    chunks = re.split(r'[\[\]]', cmd)
    log.debug('chunks: %s', chunks)
    current_arg = 0
    for i, chunk in enumerate(chunks):
        if chunk.startswith('-'):   # is a kwarg
            subchunks = re.split(r'[ =]', chunk)
            if len(subchunks) > 1:
                argname = subchunks[0]
                name = subchunks[1]
            else:
                argname = subchunks[0]
                name = subchunks[0].lstrip('-')

            name, _, negative = name.partition('|')  # postgres :/
            prefix = ('--' if argname.startswith('--') else '-')

            if name in options:
                value = options[name]
                if value is None:
                    continue
                elif type(value) is bool:
                    if value:           chunk = argname.partition('|')[0]
                    else:
                        if negative:    chunk = prefix + negative
                        else:           continue
                else:
                    chunk = argname + ' ' + quote(value)
                result += chunk
        elif chunk.isspace():
            result += chunk
        elif chunk:                       # is an arg
            try:
                count = chunk.replace('%%', '').count('%')
                chunk = chunk % args[current_arg:count]
                current_arg += count
            except (IndexError, TypeError), e:
                log.error('%s: %s', e.__class__.__name__, e)
            result += chunk

    return result


def get_cursor_pos():
    ''' Return the current column number of the terminal cursor.
        Used to figure out if we need to print an extra newline.
    '''
    value = 2
    if sys.stdout.isatty():
        import string
        sys.stdout.write('\033[6n')
        response = ''
        while True:
            c = sys.stdin.read(1)
            if c == 'R': break
            elif (c in string.digits) or (c == ';'):
                response += c
        if response:
            response = response.partition(';')[2]
            if response:
                value = int(response)
    return value


def getpwd(prompt, tries=3):
    'Request a password until two copies match.'
    while tries:
        first = getpass(prompt + ': ')
        second = getpass(prompt + ' again:')

        if first == second:
            if first:
                log.info('Passwords match.')
            return first  # '' signals exit
        else:
            tries = tries - 1
            if tries: log.error('Passwords don\'t match!  Try again.')


def find_password(directive, encrypt=None):
    result = ''
    errors = 0

    if directive.startswith('use '):
        try:
            directive = shplit(directive)[1]
        except IndexError:
            log.error('incorrect password use-directive.')
            errors += 1
            if env.pave_raise_errs:     raise RuntimeError
        try:
            result = env.pave_passwords[directive]
        except KeyError:
            log.error('password "%s" not found.', directive)
            errors += 1
            raise RuntimeError
    elif directive:
        result = directive

    if result and encrypt:
        result = crypt(result)
    return result, errors


def md5(data):
    'Given a piece of data, return its md5 hash.'
    digest = hashlib.md5()
    digest.update(data)
    return digest.hexdigest()


def q(fname):
    'Quote strings (e.g. filenames) if needed.'
    if ' ' in fname:
        fname = u'"%s"' % fname
    return fname


def runcmd(cmdline, *args, **options):
    'Run a command with fabric, using arguments to decide on sudo or not.'
    use_sudo = options.pop('use_sudo', None)
    sudo_user = options.pop('sudo_user', None)
    is_local = options.pop('local', None)
    chunking = options.pop('chunking', None)

    if chunking and '[' in cmdline:
        cmdline = fmtcmd(cmdline, *args, **options)
    elif args:
        cmdline = cmdline % args  # allow formatting w/ chunking off

    if is_local:
        result = local(cmdline, capture=True)
    elif use_sudo:
        result = sudo(cmdline, user=sudo_user)
    else:
        result = run(cmdline)
    log.debug('return code: %s', result.return_code)
    return result


def safe_eval(text, **namespace):
    ''' Disables builtins and provides only given variables.
        http://lybniz2.sourceforge.net/safeeval.html
    '''
    return eval(text, {'__builtins__': None}, namespace)


def sequence(value, *toappend):
    ''' Given an object, check if it is a sequence.  If not, add it to one.
        Return the sequence.
    '''
    if type(value) not in (list, tuple):
        value = [value]
    if toappend:    # is a tuple
        if type(value) is list:
            toappend = list(toappend)
        value = value + toappend
    return value


def _strcmp(val1, comp, val2):
    'Simple string compare function.'
    result = None
    if comp == '==':
        if val1 == val2:    result = True
        else:               result = False
    elif comp == '!=':
        if val1 != val2:    result = True
        else:               result = False
    return result


def trunc(msg, length):
    'Truncate a string with trailing ellipsis.'
    if len(msg) > length:
        msg = msg[:length] + u'…'
    return msg


def wait_key():
    'Waits for a keypress at the console.'
    return _getch()

