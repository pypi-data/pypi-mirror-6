# (c) 2012, Zettar Inc.
# Written by Chin Fang <fangchin@zettar.com>
#   https://github.com/ansible/ansible/tree/devel/lib/ansible/inventory
# regex implementation and doctests by Mike Miller
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
'''
    This module is for enhancing the inventory parsing capability such
    that it can deal with hostnames specified using a simple pattern in the
    form of [beg:end], example: [1:5] where if begin is not specified, it
    defaults to 0.

    If beg is given and is left-zero-padded, e.g. '001', it is taken as a
    formatting hint when the range is expanded. e.g. [001:010] is to be
    expanded into 001, 002 ...009, 010.

    Note that when beg is specified with left zero padding, then the length of
    end must be the same as that of beg, else a exception is raised.
'''
import re

class HostSpecError(Exception):
    pass

range_fmt = re.compile(r'''
    (                       # group host basename
        [A-Za-z0-9\-\.]*    # zero or more alphanumeric, dash, or period
    )

    \[              # A left bracket
    (               # group start digits
        \d*         # zero or more digits
    )
        [:\-]       # a colon or dash
    (               # group end digits
        \d+         # one or more digits
    )
    \]              # A right bracket
    (               # group host domain
        [\w\-\.]*   # zero or more alphanumeric, underscore, dash, or period
    )
''', re.VERBOSE) # |re.DEBUG) prints regex details


def detect_range(hostspec):
    '''
        A helper function that checks a given host string to see if it contains
        a range pattern descibed in the docstring above.

        Returns a True match object if the given string contains a pattern,
        else None.

        >>> detect_range('hostname4')

        >>> detect_range('192.[168].2.1')

        >>> detect_range('foo[bar]baz')

        >>> detect_range('[@$\\n*#:*\\t$&@]\\]')

        >>> detect_range('host_name[1:8]')  # no underscores in hostnames

        >>> detect_range('host[1:8]').groups()
        ('host', '1', '8', '')

        >>> detect_range('10.0.0.1[01:08]').groups()
        ('10.0.0.1', '01', '08', '')

        >>> detect_range('host[1:8].with-dash.com').groups()
        ('host', '1', '8', '.with-dash.com')

        >>> detect_range('www-[0001:8000].g.cn').groups()
        ('www-', '0001', '8000', '.g.cn')
    '''
    return range_fmt.match(hostspec)


def expand_hostname_range(matchobj):
    '''
        A helper function that expands a given string that contains a pattern
        specified in top docstring, and returns a list that consists of the
        expanded version.

        The '[' and ']' characters are used to maintain the pseudo-code
        appearance. They are replaced in this function with '|' to ease
        string splitting.

        Example::

            Passing a match obj allows a second execution of the regex to be
            skipped:
            match = detect_range(hostspec)
            if match:
                expand_hostname_range(match)

        References: http://ansible.github.com/patterns.html#hosts-and-groups

        >>> expand_hostname_range(detect_range('host[1:8]'))
        ['host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8']

        >>> expand_hostname_range(detect_range('host[0-2]'))
        ['host0', 'host1', 'host2']

        >>> expand_hostname_range(detect_range('host[0:3]'))
        ['host0', 'host1', 'host2', 'host3']

        >>> expand_hostname_range(detect_range('host[:2]'))
        ['host0', 'host1', 'host2']

        >>> expand_hostname_range(detect_range('www[01:04].g.cn'))
        ['www01.g.cn', 'www02.g.cn', 'www03.g.cn', 'www04.g.cn']

        >>> expand_hostname_range(detect_range('[0001:0002]node.g.cn'))
        ['0001node.g.cn', '0002node.g.cn']
    '''
    all_hosts = []
    head, beg, end, tail = matchobj.groups()
    if not beg:
        beg = '0'
    if not end:
        raise HostSpecError('Host range end value missing.')

    # range length formatting hint
    rlen = 0
    if beg[0] == '0' and len(beg) > 1:
        rlen = len(beg)

    if rlen and rlen != len(end):
        raise HostSpecError('Host range format incorrectly specified.')

    for i in range(int(beg), int(end)+1):
        if rlen:
            rseq = str(i).zfill(rlen) # range sequence
        else:
            rseq = str(i)
        all_hosts.append(head + rseq + tail)

    return all_hosts


if __name__ == '__main__':
    import doctest
    doctest.testmod()

