# TODO
# - implement clusters in pld way
Summary:	Multi-Master Replication Manager for MySQL
Name:		mysql-mmm
Version:	2.2.1
Release:	0.6
License:	GPL v2
Group:		Applications/System
URL:		http://www.mysql-mmm.org/
Source0:	http://mysql-mmm.org/_media/mmm2:%{name}-%{version}.tar.gz
# Source0-md5:	f5f8b48bdf89251d3183328f0249461e
Source1:	http://mysql-mmm.org/_media/mmm2:%{name}-%{version}.pdf
# Source1-md5:	180dbb5662fd66291d01913e0fe34842
BuildRequires:	rpm-perlprov >= 4.1-13
Source2:	%{name}.logrotate
Source3:	%{name}-agent.init
Source4:	%{name}-monitor.init
Source5:	mmm_mon_log.conf
Source6:	mmm_agent.conf
Source7:	mmm_mon.conf
Source8:	mmm_tools.conf
Source9:	mmm_common.conf
Obsoletes:	mmm
Obsoletes:	mysql-master-master
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		%{_prefix}/lib

%description
MMM (MySQL Master-Master Replication Manager) is a set of flexible
scripts to perform monitoring/failover and management of MySQL
Master-Master replication configurations (with only one node writable
at any time). The toolset also has the ability to read balance
standard master/slave configurations with any number of slaves, so you
can use it to move virtual IP addresses around a group of servers
depending on whether they are behind in replication. In addition to
that, it also has scripts for data backups, resynchronization between
nodes etc.

%package agent
Summary:	MMM Database Server Agent Daemon and Libraries
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	iproute2
Requires:	perl-Algorithm-Diff >= 1.1902
Requires:	perl-DBD-mysql
Requires:	perl-Net-ARP >= 1.0.6
Obsoletes:	mmm-agent
Obsoletes:	mysql-master-master-agent

%description agent
Agent daemon and libraries which run on each MySQL server and provides
the monitoring node with a simple set of remote services.

%package monitor
Summary:	MMM Monitor Server Daemon and Libraries
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	perl(DBD::mysql)
Obsoletes:	mmm-monitor
Obsoletes:	mysql-master-master-monitor

%description monitor
Monitoring daemon and libraries that do all monitoring work and make
all decisions about roles moving and so on.

%package tools
Summary:	MMM Control Scripts and Libraries
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Obsoletes:	mmm-tools
Obsoletes:	mysql-master-master-tools

%description tools
Scripts and libraries dedicated to management of the mmmd_mon
processes by com- mands.

%prep
%setup -q
cp -a %{SOURCE1} %{name}-%{version}.pdf

grep -rl /usr/bin/env bin sbin | xargs %{__sed} -i -e '1s,^#!.*perl,#!%{__perl},'

# currently the README included with mysql-mmm is zero-length
cat >> README <<EOF
Full documentation can be found at:

    %{_docdir}/%{name}-%{version}/%{name}-%{version}.pdf
EOF

# you'll need this if you cp -a complete dir in source
# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# additional
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig,logrotate.d},%{_localstatedir}/{run,lib}/%{name}}
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/mysql-mmm

# Replace config files
cp -a %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/mmm_mon_log.conf
cp -a %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/mmm_agent.conf
cp -a %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/mmm_mon.conf
cp -a %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/mmm_tools.conf
cp -a %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/mmm_common.conf

# Replace our init scripts
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/init.d/*
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/mysql-mmm-agent
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/rc.d/init.d/mysql-mmm-monitor

# Create defaults files
install -d $RPM_BUILD_ROOT%{_sysconfdir}/default

cat > $RPM_BUILD_ROOT/etc/sysconfig/mysql-mmm-agent <<EOF
# mysql-mmm-agent defaults
ENABLED=1
EOF

cat > $RPM_BUILD_ROOT/etc/sysconfig/mysql-mmm-monitor <<EOF
# mysql-mmm-monitor defaults
ENABLED=1
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post agent
if [ "$1" -eq 1 ]; then
	/sbin/chkconfig --add mysql-mmm-agent
	/sbin/chkconfig mysql-mmm-agent off
elif [ "$1" -ge 2 ]; then
	%service mysql-mmm-agent try-restart
fi

%post monitor
if [ "$1" -eq 1 ]; then
	/sbin/chkconfig --add mysql-mmm-monitor
	/sbin/chkconfig mysql-mmm-monitor off
elif [ "$1" -ge 2 ]; then
	%service mysql-mmm-monitor try-restart
fi

%preun agent
if [ "$1" -eq 0 ]; then
	%service mysql-mmm-agent stop
	/sbin/chkconfig --del mysql-mmm-agent
fi

%preun monitor
if [ "$1" -eq 0 ]; then
	%service mysql-mmm-monitor stop
	/sbin/chkconfig --del mysql-mmm-monitor
fi

%files
%defattr(644,root,root,755)
%doc INSTALL README VERSION %{name}-%{version}.pdf
%dir %{_sysconfdir}/mysql-mmm
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/mysql-mmm
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mmm_common.conf
%dir %{perl_vendorlib}/MMM
%{perl_vendorlib}/MMM/Common
%dir %{_libdir}/%{name}

%dir %{_localstatedir}/lib/mysql-mmm
%dir %{_localstatedir}/run/mysql-mmm
%dir %{_localstatedir}/log/mysql-mmm

%files tools
%defattr(644,root,root,755)
%doc README
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mmm_tools.conf
%attr(755,root,root) %{_sbindir}/mmm_backup
%attr(755,root,root) %{_sbindir}/mmm_clone
%attr(755,root,root) %{_sbindir}/mmm_restore
%{perl_vendorlib}/MMM/Tools
%dir %{_libdir}/%{name}/tools
%attr(755,root,root) %{_libdir}/%{name}/tools/create_snapshot
%attr(755,root,root) %{_libdir}/%{name}/tools/remove_snapshot

%files agent
%defattr(644,root,root,755)
%doc README
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mmm_agent.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mysql-mmm-agent
%attr(754,root,root) /etc/rc.d/init.d/mysql-mmm-agent
%attr(755,root,root) %{_sbindir}/mmm_agentd
%{perl_vendorlib}/MMM/Agent
%dir %{_libdir}/%{name}/agent
%attr(755,root,root) %{_libdir}/%{name}/agent/check_ip
%attr(755,root,root) %{_libdir}/%{name}/agent/clear_ip
%attr(755,root,root) %{_libdir}/%{name}/agent/configure_ip
%attr(755,root,root) %{_libdir}/%{name}/agent/mysql_allow_write
%attr(755,root,root) %{_libdir}/%{name}/agent/mysql_deny_write
%attr(755,root,root) %{_libdir}/%{name}/agent/mysql_may_write
%attr(755,root,root) %{_libdir}/%{name}/agent/set_active_master
%attr(755,root,root) %{_libdir}/%{name}/agent/sync_with_master
%attr(755,root,root) %{_libdir}/%{name}/agent/turn_off_slave
%attr(755,root,root) %{_libdir}/%{name}/agent/turn_on_slave

%files monitor
%defattr(644,root,root,755)
%doc README
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mmm_mon.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/mmm_mon_log.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mysql-mmm-monitor
%attr(754,root,root) /etc/rc.d/init.d/mysql-mmm-monitor
%attr(755,root,root) %{_sbindir}/mmm_mond
%attr(755,root,root) %{_sbindir}/mmm_control
%{perl_vendorlib}/MMM/Monitor
%dir %{_libdir}/%{name}/monitor
%attr(755,root,root) %{_libdir}/%{name}/monitor/checker
