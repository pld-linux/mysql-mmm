# TODO
# - find source for bundled 32bit elfs: bin/sys/*
# - pldize initscript, logrotate, etc
%include	/usr/lib/rpm/macros.perl
Summary:	MySQL Master-Master Replication Manager
Name:		mysql-mmm
Version:	1.2.3
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	http://mysql-master-master.googlecode.com/files/mysql-master-master-%{version}.tar.gz
# Source0-md5:	2d0492222441ddae061a84bbfe23777a
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}

%description
MMM (MySQL Master-Master Replication Manager) is a set of flexible
scripts to perform monitoring/failover and management of MySQL
Master-Master replication configurations (with only one node writable
at any time). The toolset also has the ability to read balance
standard master/slave configurations with any number of slaves, so you
can use it to move virtual IP addresses around a group of servers
depending on whether they are behind in replication.

%prep
%setup -q -n mysql-master-master-%{version}

grep -rl /usr/bin/env bin sbin | xargs %{__sed} -i -e '1s,^#!.*perl,#!%{__perl},'

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,logrotate.d}
./install.pl \
	--prefix=$RPM_BUILD_ROOT%{_appdir} \
	--sbin-dir=$RPM_BUILD_ROOT%{_sbindir} \
	--man-dir=$RPM_BUILD_ROOT%{_mandir} \
	--skip-checks

# Install init scripts and logrotate conf
install -p scripts/init.d/mmm_agent $RPM_BUILD_ROOT/etc/rc.d/init.d/mmm_agent
install -p scripts/init.d/mmm_mon $RPM_BUILD_ROOT/etc/rc.d/init.d/mmm_mon
cp -a scripts/logrotate.d/mmm $RPM_BUILD_ROOT/etc/logrotate.d/mmm

# fix symlinks
for a in $RPM_BUILD_ROOT%{_sbindir}/*; do
	l=$(readlink $a)
	l=../${l#$RPM_BUILD_ROOT%{_prefix}/}
	ln -sf $l $a
done

# relocate manuals
install -d $RPM_BUILD_ROOT%{_mandir}/man1
mv $RPM_BUILD_ROOT%{_appdir}/man/man1/* $RPM_BUILD_ROOT%{_mandir}/man1

# relocate examples
install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
for a in $RPM_BUILD_ROOT%{_appdir}%{_sysconfdir}/examples/*; do
	mv $a $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}/$(basename $a .example)
done

# bundled 32bit ELF
rm -f $RPM_BUILD_ROOT%{_appdir}/bin/sys/*

# Remove unpackaged files/dirs
rm -f $RPM_BUILD_ROOT%{_appdir}/debug*.list
rm -r $RPM_BUILD_ROOT%{_appdir}/scripts \
       $RPM_BUILD_ROOT%{_appdir}/install.pl \
       $RPM_BUILD_ROOT%{_appdir}/contrib \
       $RPM_BUILD_ROOT%{_appdir}/man/src \
       $RPM_BUILD_ROOT%{_appdir}/CHANGES \
       $RPM_BUILD_ROOT%{_appdir}/COPYING \
       $RPM_BUILD_ROOT%{_appdir}/INSTALL \
       $RPM_BUILD_ROOT%{_appdir}/README \
       $RPM_BUILD_ROOT%{_appdir}/VERSION

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add mmm_agent
%service mmm_agent restart
/sbin/chkconfig --add mmm_mon
%service mmm_mon restart

%preun
if [ "$1" = "0" ]; then
	%service mmm_agent stop
	/sbin/chkconfig --del mmm_agent
	%service mmm_mon stop
	/sbin/chkconfig --del mmm_mon
fi

%files
%defattr(644,root,root,755)
%doc CHANGES INSTALL README VERSION
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/mmm
%attr(754,root,root) /etc/rc.d/init.d/mmm_agent
%attr(754,root,root) /etc/rc.d/init.d/mmm_mon
%attr(755,root,root) %{_sbindir}/mmm_backup
%attr(755,root,root) %{_sbindir}/mmm_clone
%attr(755,root,root) %{_sbindir}/mmm_control
%attr(755,root,root) %{_sbindir}/mmm_get_dump
%attr(755,root,root) %{_sbindir}/mmm_restore
%attr(755,root,root) %{_sbindir}/mmmd_agent
%attr(755,root,root) %{_sbindir}/mmmd_angel
%attr(755,root,root) %{_sbindir}/mmmd_mon
%{_mandir}/man1/mmm_backup.1*
%{_mandir}/man1/mmm_clone.1*
%{_mandir}/man1/mmm_control.1*
%{_mandir}/man1/mmm_get_dump.1*
%{_mandir}/man1/mmm_restore.1*
%{_mandir}/man1/mmmd_agent.1*
%{_mandir}/man1/mmmd_angel.1*
%{_mandir}/man1/mmmd_mon.1*

%dir %{_appdir}
%{_appdir}/lib
%dir %{_appdir}/sbin
%attr(755,root,root) %{_appdir}/sbin/*

%dir %{_appdir}/bin
%dir %{_appdir}/bin/agent
%dir %{_appdir}/bin/check
%dir %{_appdir}/bin/lvm
%dir %{_appdir}/bin/sys
%attr(755,root,root) %{_appdir}/bin/agent/add_role
%attr(755,root,root) %{_appdir}/bin/agent/check_role
%attr(755,root,root) %{_appdir}/bin/agent/del_role
%attr(755,root,root) %{_appdir}/bin/agent/set_active_master
%attr(755,root,root) %{_appdir}/bin/agent/set_state
%attr(755,root,root) %{_appdir}/bin/check/checker
%attr(755,root,root) %{_appdir}/bin/check_ip
%attr(755,root,root) %{_appdir}/bin/clear_ip
%attr(755,root,root) %{_appdir}/bin/limit_run
%attr(755,root,root) %{_appdir}/bin/lvm/create_snapshot
%attr(755,root,root) %{_appdir}/bin/lvm/remove_snapshot
%attr(755,root,root) %{_appdir}/bin/mysql_allow_write
%attr(755,root,root) %{_appdir}/bin/mysql_deny_write
%attr(755,root,root) %{_appdir}/bin/sync_with_master
#%attr(755,root,root) %{_appdir}/bin/sys/fping
#%attr(755,root,root) %{_appdir}/bin/sys/send_arp
%attr(755,root,root) %{_appdir}/bin/turn_off_slave
%attr(755,root,root) %{_appdir}/bin/turn_on_slave

%{_examplesdir}/%{name}-%{version}
