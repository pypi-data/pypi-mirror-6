# -*- coding: utf-8 -*-
'''
    (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+

    Set up and configure logging and custom levels.
'''
import sys, os, subprocess
import logging, logging.handlers
from datetime import datetime as dt
from logging import Formatter
from os.path import expanduser
from glob import glob
try:
    import curses
except ImportError:
    curses = None
    try:
        import colorama
        colorama.init()
    except ImportError:
        print '\nError: color support not available.  Install colorama:'
        print '       pip install colorama\n'


# level constants
logging.NOTE = 32       # positive yet important
logging.SKIP = 22       # skipped an action
logging.CHANGE = 27     # changed target
logging.EXCEPT = 42     # pave/lib exception

log = logging.getLogger()
out = sys.__stdout__
logfmt = '  %(levelname)-7.7s %(module)s: %(message)s'
logfmtf = '%(asctime)s' + logfmt[1:], '%H:%M:%S'
ext_font = glob(expanduser('~/.fonts/[Ss]ymbola*.???'))


# logging classes
class SecshFilterI(logging.Filter):
    'Filter annoying "Secsh channel..." info messages.'
    def filter(self, record):
        allow = True
        if (isinstance(record.msg, basestring) and
            record.msg.startswith('Secsh channel ')):
            allow = False
        if record.module == 'sftp':
            allow = False
        return allow


class SecshFilterD(logging.Filter):
    'Filter annoying "[chan X]..." debug messages.'
    def filter(self, record):
        allow = True
        if isinstance(record.msg, basestring):
            allow = not (record.module == 'channel')
        return allow


class EspeakHandler(logging.StreamHandler):
    'Speak messages for notification.'
    def __init__(self, *args, **kwargs):
        super(EspeakHandler, self).__init__(*args, **kwargs)
        with open(os.devnull, "w") as null:
            try:
                self.process = subprocess.Popen(['espeak'],
                    stdin=subprocess.PIPE, stderr=null )
            except:
                log.error('espeak is not installed.')
                self.process = None

    def emit(self, record):
        if self.process:
            try:
                msg = self.format(record)
                self.process.stdin.write(msg + '\n')
                self.process.stdin.flush()
            except:
                self.handleError(record)

    def __del__(self):
        if self.process:
            self.process.close()


class ColorFmtr(Formatter):
    'Colors the levelname of a log message.'
    def __init__(self, *args, **kwargs):
        #~ super(ColorFmtr, self) -->
        # Py 2.6: TypeError: super() argument 1 must be type, not classobj
        Formatter.__init__(self, *args, **kwargs)
        if curses:
            curses.setupterm()
            if curses.tigetnum('colors') < 8:
                raise EnvironmentError, 'Not enough colors available.'
            self.curses = curses
            setf = curses.tigetstr('setaf')
            setbg = curses.tigetstr('setab')
            bold = curses.tigetstr('bold')
            white_on_red = (curses.tparm(setf, curses.COLOR_WHITE) +
                            curses.tparm(bold, curses.A_BOLD) +
                            curses.tparm(setbg, curses.COLOR_RED))
            self.colormap = dict(
                DEBUG    = curses.tparm(setf, curses.COLOR_BLUE),
                INFO     = curses.tparm(setf, curses.COLOR_GREEN),
                SKIP     = curses.tparm(setf, curses.COLOR_CYAN),
                CHANGE   = curses.tparm(setf, curses.COLOR_YELLOW),
                WARNING  = curses.tparm(setf, curses.COLOR_YELLOW) +
                            curses.tparm(bold, curses.A_BOLD),
                NOTE     = curses.tparm(setf, curses.COLOR_GREEN) +
                            curses.tparm(bold, curses.A_BOLD),
                ERROR    = curses.tparm(setf, curses.COLOR_RED) +
                            curses.tparm(bold, curses.A_BOLD),
                EXCEPT   = curses.tparm(setf, curses.COLOR_RED) +
                            curses.tparm(bold, curses.A_BOLD),
                CRITICAL = white_on_red,
                FATAL    = white_on_red,
                NOTSET   = curses.tigetstr('sgr0')
            )
            self.icomap = dict(
                DEBUG       = u'•',
                INFO        = u'✓',
                SKIP        = u'⏬',
                CHANGE      = u'✎',
                WARNING     = u'⚠',
                NOTE        = u'★',
                ERROR       = u'✗',
                EXCEPT      = u'💣' if ext_font else u'✘',
                CRITICAL    = u'💀' if ext_font else u'✘',
                FATAL       = u'💀' if ext_font else u'✘',
                NOTSET      = u'•',
            )
        else:
            self.colormap = dict(
                DEBUG    = '\x1b[34m',                  # blue
                INFO     = '\x1b[32m',                  # green
                SKIP     = '\x1b[36m',                  # cyan
                CHANGE   = '\x1b[33m',                  # yellow
                WARNING  = '\x1b[33m\x1b[1m',           # yellow bold
                NOTE     = '\x1b[32m\x1b[1m',           # green bold
                ERROR    = '\x1b[31m\x1b[1m',           # red bold
                EXCEPT   = '\x1b[31m\x1b[1m',           # red bold
                CRITICAL = '\x1b[37m\x1b[1m\x1b[41m',   # white bold on red
                FATAL    = '\x1b[37m\x1b[1m\x1b[41m',   # white bold on red
                NOTSET   = '\x1b[0m' # '\x1b(B\x1b[m'   # reset
            )
            self.icomap = dict(
                DEBUG       = '-',
                INFO        = '+',
                SKIP        = 'v',
                CHANGE      = '~',
                WARNING     = '!',
                NOTE        = '@',
                ERROR       = 'x',
                EXCEPT      = 'X',
                CRITICAL    = '*',
                FATAL       = '*',
                NOTSET      = ' ',
            )

    def format(self, record):
        colormap = self.colormap
        levelname = record.levelname
        s = Formatter.format(self, record)
        ico = self.icomap[levelname]
        # have to replace afterward because "%(levelname)-7.7s" cuts esc seqs
        # UnicodeDecodeError here = unicode char in msg w/o leading u'...'
        s = s.replace(levelname, (colormap.get(levelname, '') +
                      ico + ' ' + levelname + colormap.get('NOTSET')), 1)
        return s


class MsecFormatter(Formatter):
    'Includes milliseconds in asctime.'
    converter=dt.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = ct.strftime(datefmt or "%Y-%m-%d %H:%M:%S")
        s = "%s.%03d" % (t, record.msecs)
        return s


class ioLogger:
    '''
        Redirect output streams to logging system.
            orig_stdout = sys.stdout                        # save for later
            sys.stdout = ioLogger(log, 'debug')             # redirect stdout
            # ...
            sys.stdout = orig_stdout                        # restore
    '''
    def __init__(self, logger, level='debug'):
        self.logger = logger
        self.level = logging._levelNames[level.upper()]
        self.buffer = u''

    def isatty(self):
        return False

    def flush(self, interactive=False):
        if interactive:
            self.logger.log(self.level, self.buffer)
            self.buffer = u''  # might help

    def write(self, text):
        # this could be refactored, but may be a bit faster this way.
        if text.endswith('\n'):     # flush buffer
            try:  text = self.buffer + text.rstrip()
            except UnicodeDecodeError:
                text = (self.buffer +
                        text.decode('utf8', errors='replace').rstrip())
            self.logger.log(self.level, text)
            self.buffer = u''
        else:                       # add to buffer
            try: self.buffer += text
            except UnicodeDecodeError:
                self.buffer += text.decode('utf8', errors='replace')
            # having a weird error with pyemphem, what are these chars?
            # looks like apostrophe and acute accent:
            # libastro-3.7.5/magdecl.c: In function ���E0000���:

# functions
def start_file_log(filepath):
    '''Log each host's actions to files in temp folder.'''
    h = logging.handlers.RotatingFileHandler(filepath,
                                             encoding='utf8', backupCount=5)
    h.doRollover()  # rollover each execution
    h.setFormatter(MsecFormatter(*logfmtf))
    h.setLevel(logging.DEBUG)
    h.addFilter(SecshFilterD())  # doesn't seem to be working :/
    log.addHandler(h)
    return h


def makefunc(level):
    def thefunc(msg, *args, **kwargs):
        if log.isEnabledFor(level):
            log._log(level, msg, args, **kwargs)
    return thefunc


# allows modules to use functions that log as if they were local :/
def _makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None,
                extra=None):
    '''Custom Logger.makeRecord that doesn't raise KeyError on extra.'''
    rv = logging.LogRecord(name, level, fn, lno, msg, args, exc_info, func)
    if extra is not None:
        for key in extra:
            rv.__dict__[key] = extra[key]
    return rv
logging.Logger.makeRecord = _makeRecord


# set up logging, custom levels
logging.addLevelName(logging.NOTE, 'NOTE')      # new levels
logging.addLevelName(logging.SKIP, 'SKIP')
logging.addLevelName(logging.CHANGE, 'CHANGE')
logging.addLevelName(logging.EXCEPT, 'EXCEPT')
logging.addLevelName(logging.CRITICAL, 'FATAL') # rename existing

# add convenience funcs
log.note    = makefunc(logging.NOTE)
log.skip    = makefunc(logging.SKIP)
log.change  = makefunc(logging.CHANGE)
log.exc     = makefunc(logging.EXCEPT)

console = logging.StreamHandler(sys.stdout)
log.addHandler(console)
log.setLevel(logging.DEBUG)
console.addFilter(SecshFilterI())

