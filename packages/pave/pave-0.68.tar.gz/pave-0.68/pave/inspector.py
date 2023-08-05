# inspector - queries host details then caches the result in the temp folder.
import os, json, platform as p
from locale import getdefaultlocale as gdl
from os.path import join, expanduser

# work dir
wd = join(os.environ.get('XDG_CACHE_HOME') or expanduser('~/.cache'), 'pave')
# cache file name
cfn = join(wd, 'platform.json')

# grab the details
def query():
    details = dict(encoding=gdl()[1],
        arch=p.architecture(),machine=p.machine(),node=p.node(),
        proc=p.processor(),py_vers=p.python_version(),
        py_vert=p.python_version_tuple(),os_release=p.release(),
        system=p.system(),version=p.version(),win_vers=p.win32_ver(),
        mac_vers=p.mac_ver(),linux_dist=p.linux_distribution(),
    )
    return details

# check if cache file exists and > 0
if not (os.access(cfn, os.R_OK) and os.stat(cfn).st_size > 5):
# create the Cache file, using info from one of the files below.
    if not os.path.exists(wd):
        os.makedirs(wd)
        os.chmod(wd, 0750)
    with file(cfn, 'w') as f:
        json.dump(query(), f, separators=(',',':'))

# print results file to stdout
with file(cfn) as f:
    print f.read()
