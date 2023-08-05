'''
    (C) 2012-2013 Mike Miller.
    License: GNU GPLv3+
    Where platform-specific commands and settings are kept.

    Class names should match the identifier string given by Python's
    platform module.  The version number can be appended as well to narrow its
    specificity.
'''
import re

deb_pkg_out_pat = re.compile(r'^(\d+) upgraded, (\d+) newly installed, ' +
                             r'(\d+) to remove')  # first three ints


class OS(object):
    python      = 'python "%s"'
    pythonc     = 'python2 -c "%s"'
    # No use to override __getattr__ etc unless using instances.
    # Currently using classes.
    @classmethod
    def _get_fqn(myclass):
        return str(myclass).split("'")[1]


class Windows(OS):
    pass


class Unix(OS):
    dir_test    = 'test -d "%s"'
    dir_create  = 'mkdir -p "%s"'
    file_append = '''echo -e '%s' >> "%s"'''
    file_chgrp  = 'chgrp %s "%s"'
    file_chmod  = 'chmod %s "%s"'
    file_chown  = 'chown %s "%s"'
    file_copy_q = 'cp "%s" "%s"'
    file_create = 'touch "%s"'
    file_exists = 'test -e "%s"'
    file_hash   = 'md5sum "%s"'
    file_search = '''grep -F '%s' "%s"'''
    file_test   = 'test -f "%s"'
    file_update = 'cp -f %s %s'
    home_path   = '/home'
    test_nt     = "test '%s' -nt '%s'"
    tempdir     = '/tmp'

    pg_ln_curr  = 'ln -sf "/etc/postgresql/%s" /etc/postgresql/curr'
    pg_get_pwd  = "psql -d template1 -t -c 'select passwd from pg_shadow;' "
    pg_set_pwd  = ('psql -c "ALTER USER postgres WITH ENCRYPTED PASSWORD'
                    ''' '%s';" template1 ''')
    pg_ls_user  = ("psql -d template1 -t -c 'select u.usename from "
                   "pg_catalog.pg_user u;' ")
    pg_cr_user  = ('createuser [--encrypted|no-encrypted] '
                   '[--createdb|no-createdb] [--createrole|no-createrole] '
                   '[--superuser|no-superuser] [--login|no-login] %s')
    pg_ls_db    = ("psql -d template1 -t -c 'SELECT datname FROM pg_database "
                   "WHERE datistemplate = false;' ")
    pg_cr_db    = ('createdb [--locale] [--encoding] [--tablespace] '
                   '[--template] %s %s')
    pg_ls_acl   = ('psql -d template1 -t -c "select datname, datacl from '
                   '''pg_database where datname = '%s';" ''')
    pg_grant    = ("psql -d template1 -c 'GRANT %s PRIVILEGES ON %s "
                   "%s to %s;' ")
    pg_sql      = 'psql -d %s -t -c "%s" '

    ssh_keypath = '${HOME}/.ssh/id_%s'
    ssh_akfile  = '${HOME}/.ssh/authorized_keys'
    ssh_keygen  = '''ssh-keygen -t %s -f "%s" -N '%s' '''
    svc_restart = 'service %s restart'

    dj_mancmd   = './manage.py'
    dj_chktable = (r"echo '\t\d' | ./manage.py dbshell | "
                    "/bin/grep -m 1 ' table ' ")
    dj_syncdb   = '%s syncdb --noinput --all' % dj_mancmd
    dj_chkmigrt = 'ls */migrations/*.pyc'
    dj_initmgrt = '%s migrate --fake --noinput' % dj_mancmd
    dj_loaddata = '%s loaddata %%s' % dj_mancmd
    # bash only
    #~ dj_chkdata  = '''
        #~ d=( $(/bin/grep -E '(pk|model)' %s|head -2|tr -d ',"'|tr . _|cut -f 3 -d:) )
        #~ echo search: ${d[@]}
        #~ echo "select * from ${d[1]} where id = $d;"|./manage.py dbshell|grep $d'''
    # py 2.6, perhaps awk would be better?
    dj_chkdata  = OS.pythonc % r'''
import sys, glob as g, commands as c
pk, tb = None, None
with file(sorted(g.glob('%s'))[0]) as f:
  for line in f:
    if pk and tb: break
    if 'pk' in line:
      pk = line.split()[1][:-1]
    elif 'model' in line:
      tb = line.split()[1][1:-2].replace('.', '_')
print 'search:', pk, tb
cmd = ('echo \'select id from %%s where id = %%s;\' | ./manage.py dbshell | grep %%s'
  %% (tb, pk, pk))
res = c.getoutput(cmd).strip()
print 'found :', res
if not res: sys.exit(1)'''


if True:

    class Linux(Unix):
        locale_dir      = '/usr/share/locale'
        locale_test     = 'find . -maxdepth 1 -type d | wc -l'
        locale_cln      = ("/bin/bash -O extglob -c 'rm -rf %s/!(%%s)/'"
                            % locale_dir)
        file_stat       = 'stat -c "%%a %%U %%G" "%s"'

        grp_add         = 'addgroup [--gid] %s'
        grp_lst         = 'cut -d: -f1 /etc/group'

        krn_get_param   = 'sysctl -n %s'
        krn_set_param   = 'sysctl -w "%s"'
        krn_param_fnm   = '/etc/sysctl.conf'
        krn_param_reg   = r'^\s*%s\s*=.*'  # ' vm.swappiness = ...'
        krn_srch_file   = "grep '%s' %%s" % krn_param_reg

        svc_lst         = 'service --status-all'
        svc_start       = 'service %s start'
        svc_stop        = 'service %s stop'
                          # change the name of the param with [--old new]
        usr_add         = ('useradd [--create-home] [--groups] ' +
                           '[--shell] [--password] %s')
        usr_lst         = 'cut -d: -f1 /etc/passwd'

        svc_disable     = 'update-rc.d %s disable'

        @staticmethod
        def parse_svclist(svclist):
            'Handles sysvinit format.'
            services = {}
            for service in svclist.split('\n'):
                tokens = service.split()
                services[tokens[3]] = (1  if tokens[1] == '+'  else 0)
            return services


    if True:

        class Debian(Linux):
            pkg_clean       = 'apt-get -y -q clean; apt-get -y -q autoremove'
            pkg_install     = 'DEBIAN_FRONTEND=noninteractive apt-get -y -q install %s'
            pkg_inventory   = "dpkg-query --show | cut -f1 | tr '\\n' ' ' "
            pkg_remove      = 'DEBIAN_FRONTEND=noninteractive apt-get -y -q purge %s'
            pkg_update      = 'apt-get -y -q update'
            pkg_update_time = 'find /var/lib/apt -name lists -daystart -mtime +%s'
            pkg_upgrade     = 'DEBIAN_FRONTEND=noninteractive apt-get -y -q upgrade'
            pkg_upgrd_full  = 'DEBIAN_FRONTEND=noninteractive apt-get -y -q dist-upgrade'
            pkg_upgrd_time  = 'find /var/lib/dpkg -name status -daystart -mtime +%s'
            pkg_stat_mtime  = 'stat -c %y /var/lib/dpkg/status'

            @staticmethod
            def parse_pkg_output(output):
                '0 upgraded, 0 newly installed, 0 to remove and 20 not upg...'
                if output:
                    for line in output.splitlines():
                        match = deb_pkg_out_pat.match(line)
                        if match:
                            return [ int(digit) for digit in match.groups() ]
                return []

        class Ubuntu(Debian):
            svc_lst         = 'service --status-all 2> /dev/null; initctl list'
            svc_disable_ups = ('mv -f /etc/init/%s.conf /etc/init/%s.disabled;'
                               ' echo "manual" > /etc/init/%s.override')

            @staticmethod
            def parse_svclist(svclist):
                'Handle sysvinit and upstart formats.'
                services = {}
                for service in svclist.split('\n'):
                    tokens = service.split()
                    if tokens[0] == '[':  # sysvinit
                        services[tokens[3]] = (1  if tokens[1] == '+'  else 0)
                    else:                 # upstart
                        status = (tokens[2] if tokens[1].startswith('(')
                                            else tokens[1])
                        status = status.partition('/')[0]
                        services[tokens[0]] = (1  if status == 'start'  else 0)
                return services


        class Raspbian(Debian):
            pass


        class Redhat(Linux):
            pkg_clean       = 'yum -y -q clean packages'
            pkg_install     = 'yum -y -q install %s'
            pkg_inventory   = 'rpm -qa | rev | cut -f 3- -d- | rev | sort'
            pkg_remove      = 'yum -y -q remove %s'
            pkg_update      = 'yum makecache'
            pkg_update_time = 'find /var/cache/yum/*/* -name updates -daystart -mtime +%s'
            pkg_upgrade     = 'yum -y -q update'
            pkg_upgrd_time  = 'find /var/lib -name yum -daystart -mtime +%s'
            pkg_stat_mtime  = 'stat -c %y /var/lib/yum'

            svc_start       = 'chkconfig %s on'
            svc_stop        = 'chkconfig %s off'

            @staticmethod
            def parse_svclist(svclist):
                'name (pid XXX) is running... # :/'
                services = {}
                for service in svclist.split('\n'):
                    tokens = service.split()
                    service[tokens[0]] = (1  if 'running...' in tokens  else 0)
                return services

        Red = Redhat # alias

        class CentOS(Redhat):
            pass

        class Fedora(Redhat):
            svc_lst         = 'systemctl list-unit-files -t service'

            @staticmethod
            def parse_svclist(svclist):
                services = {}
                for service in svclist.split('\n'):
                    tokens = service.split()
                    name = tokens[0].partition('.')[0]
                    service[name] = (1 if tokens[1] == 'enabled'  else 0)
                return services


        class Gentoo(Linux):
            grp_add         = 'groupadd [--gid] %s'
            pkg_clean       = 'eclean -q -C distfiles'
            pkg_install     = 'emerge -q --update --newuse %s'
            pkg_inventory   = "equery -q list --format='$name' '*'"
            pkg_remove      = 'emerge --quiet-unmerge-warn --unmerge %s'
            pkg_update      = 'emerge -q --sync'
            # update_time /var/db/pkg ?
            pkg_update_time = 'find /usr/portage/metadata -name "timestamp.x" -daystart -mtime %s'
            pkg_upgrade     = 'emerge -q --update --deep --newuse world'
            # upgrd_time - how to find out if a package was installed?
            # timestamps and/or by parsing the pkg mgr output.
            # see parse_pkg_output above
            pkg_upgrd_time  = 'find /var/tmp -name portage -daystart -mtime +%s'
            pkg_stat_mtime  = 'stat -c %y /var/tmp/portage'

            svc_lst         = 'rc-status -s -C'
            svc_start       = 'rc-service %s start'
            svc_stop        = 'rc-service %s stop'
            svc_disable     = 'rc-update del %s default'

            @staticmethod
            def parse_svclist(svclist):
                services = {}
                for service in svclist.split('\n'):
                    tokens = service.split()
                    services[tokens[0]] = (1 if tokens[2] == 'started' else 0)
                return services


    class Solaris(Unix):
        pass


    class BSD(Unix):
        pass


    if True:

        class Darwin(BSD): # OSX
            home_path   = '/Users'












