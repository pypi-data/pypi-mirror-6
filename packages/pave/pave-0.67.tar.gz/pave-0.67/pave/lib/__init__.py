''' (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+
'''

# need a module list to load schemas, etc
from os import listdir
from os.path import basename, dirname, splitext

modlist = set([
    splitext(basename(fn))[0]
    for fn in listdir(dirname(__file__))
    if fn.endswith('.py')
    if not basename(fn).startswith('_')
])

