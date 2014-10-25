Name:           livetool
Version:        1.0
Release:        1%{?dist}
Summary:        Live tools for backup and restore

License:        GPLv2+
URL:            http://mojpardaz.com/
Source0:        livetool.tar.gz
Source1:	livetool-graphical.service

BuildRequires: gettext
BuildRequires: python-devel
BuildRequires: systemd-units
Requires: pygtk2, python
Requires: python-meh
Requires(post): systemd-units systemd-sysv chkconfig
Requires(preun): systemd-units
Requires(postun): systemd-units


%description
Livetool for creating backup and restore.

%prep
%setup -q -c

%install 
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_unitdir} 
mkdir -p %{buildroot}/usr/share/livetool
mkdir -p %{buildroot}/usr/sbin
mv livetool/service/livetool.sh ${RPM_BUILD_ROOT}/usr/sbin/
rsync -r --exclude=".git" livetool/ ${RPM_BUILD_ROOT}/usr/share/livetool/

chmod +x ${RPM_BUILD_ROOT}/usr/sbin/livetool.sh

install -p -m 644 livetool/service/livetool-graphical.service %{buildroot}%{_unitdir}/%{name}.service

%files
%{_sbindir}/livetool.sh
%_datadir/livetool/*
%attr(0644,root,root) %{_unitdir}/%{name}.service


%changelog

* Fri Aug 23 2013 Mola Pahnadayan <mola.mp@gmail.com>
- Initial RPM release.
