import sys, os
from os.path import join
from distutils.core import setup

from pave.meta import __version__, __progname as name

# readme is needed at register/upload time, not install time
try:
    with open('readme.rst') as f:
        long_description = ['|\n', '|\n', '|\n','\n'] # push logo under login box
        for line in f:
            if line.startswith('.. '):          # remove sphinx directives at end
                break
            long_description.append(line)
        long_description = ''.join(long_description)
except IOError:
    long_description = ''

# do we need importlib?
requires = []
if sys.version < '2.7':
    requires.append('importlib')

# install helper script?
scripts = [join(name, name)]
if os.name == 'nt':
    scripts.append(name + '.cmd')


setup(
    name              = name,
    version           = __version__,
    description       = ( 'Simple push-based configuration and deployment ' +
                          'tool, leveraging fabric.  ' +
                          'No servers, few dependencies.'),
    author            = 'Mike Miller',
    author_email      = 'mixmastamyk@bitbucket.org',
    url               = 'https://bitbucket.org/mixmastamyk/pave',
    download_url      = 'https://bitbucket.org/mixmastamyk/pave/get/' +
                        'default.tar.gz',
    license           = 'GPLv3+',
    requires          = ['PyYAML(>=3.05,<4.0)', 'fabric(>=1.4,<2.0)',
                         'voluptuous(>=0.8.3,<0.9)'] + requires,# for pypi page
    install_requires  = ['PyYAML>=3.05,<4.0a0', 'fabric>=1.4,<2.0a0',
                         'voluptuous>=0.8.3,<0.9a0'] + requires,  # real reqs
                         #~ 'voluptuous==dev'],
    packages          = [name, join(name, 'lib')],
    scripts           = scripts,
    package_data      = {name: ['inspector.sh', 'skeleton.yml']},
    #~ dependency_links  = ['https://github.com/alecthomas/voluptuous/tarball/' +
                         #~ 'master#egg=voluptuous-dev'],  # temp dev download
    extras_require = {
        'win': ['colorama', 'fcrypt'],
    },

    long_description  = long_description,
    classifiers       = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
