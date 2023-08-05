'''
    (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+

    Strangely enough, schema and schema-related code lives here.
'''
import imp, logging, unicodedata
from os.path import dirname, join

import voluptuous
from voluptuous import All, Any, Required as req, Range as rng, Invalid

import lib
from utils import shplit

log = logging.getLogger()
CURRENT = 'CURRENT'

# classes
class SchemaError(Exception):
    pass

def if_var_three_args(v):
    if not isinstance(v, basestring):
        raise Invalid('not a string.')
    args = shplit(v)
    if len(args) != 3:
        raise Invalid('variable test: wrong number of args: %r' % v)


# module schema additions
conditionals_schema = {
    'if':                               if_var_three_args,
    'if-exec':                          basestring,
    'if-platform':                      basestring,
    'do':                               basestring,
}

# define core section schemas
main_schema = {
    req('bak-files', default=True):     bool,
    req('env', default={}):             dict,
    req('include', default=[]):         Any(basestring, [basestring]),
    req('inspect', default=True):       Any(bool, basestring),
    req('jobs', default=1):             All(int, rng(min=1,max=100)),
    req('log-to', default=''):          basestring,
    req('sudo', default=True):          bool,
    'sudo-user':                        basestring,
    'sys.path':                         Any(basestring, [basestring]),
    req('targets', default=''):         Any(basestring, [basestring]),
    req('user', default=CURRENT):       basestring,
    req('version', default=CURRENT):    basestring,
    req('warn-only', default=False):    bool,
}

def validate_varname(value, msg=None):
    'Rules for variable names in the pavefile.'
    msg = 'variable names start with letters, or underscore.'
    cat = unicodedata.category(value[0])
    if not cat in ('Ll', 'Lu', 'Pc'):
        raise Invalid(msg)
    if cat == 'Pc' and value[0] != '_':
        raise Invalid(msg)

    msg = 'variable names must be with letters, digits, or underscore.'
    for ch in value[1:]:
        cat = unicodedata.category(ch)
        if not cat in ('Ll', 'Lu', 'Pc', 'Nd'):
            raise Invalid(msg)
        if cat == 'Pc' and ch != '_':
            log.note('raising...')
            raise Invalid(msg)
    return value


vars_schema = {
    validate_varname:   Any(int, float, basestring, bool, list),
}
target_groups_schema = {
    basestring:         Any(basestring, [basestring]),
}
passwords_schema = [basestring]

# load library module schemas
mod_schemas = {}
for modname in [ m for m in lib.modlist ]:
    modpath = join(dirname(__file__), 'lib', '%s.py' % modname)
    mod = imp.load_source('pave.lib.' + modname, modpath)
    if mod and hasattr(mod, 'schema'):
        mod_schemas[modname] = mod.schema

tasks_schema = [basestring, mod_schemas]
fabtasks_schema = [basestring, dict]
disabled_schema = fabtasks_schema

root_schema = {
    req('main'):        main_schema,
    'passwords':        passwords_schema,
    'target-groups':    target_groups_schema,
    'tasks':            tasks_schema,
    'disabled':         disabled_schema,
    'fab-tasks':        fabtasks_schema,
    'vars':             vars_schema,
}
schema = voluptuous.Schema(root_schema, extra=False)


if __name__ == '__main__':

    from pprint import pprint
    pprint(schema)

