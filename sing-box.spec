# debuginfo seems to only work with gccgo.
%global debug_package %{nil}

Name:       sing-box
Version:    1.9.7
Release:    1%{?dist}
Summary:    The universal proxy platform 

License:    GPL-3.0-or-later
URL:        https://github.com/SagerNet/sing-box
Source0:    https://github.com/SagerNet/sing-box/archive/v%{version}/%{name}-%{version}.tar.gz

# $ GOPROXY=https://proxy.golang.org go mod vendor -v
# Contains %{name}-%{version}/vendor/*.
Source1:    %{name}-%{version}.go-mod-vendor.tar.xz

Source2:    sing-box@.service

BuildRequires:  systemd-rpm-macros
BuildRequires:  golang >= 1.21.0


%description
The universal proxy platform.


%prep
%setup -q -D -T -b0 -n %{name}-%{version}
%setup -q -D -T -b1 -n %{name}-%{version}


%build
go build -v \
        -trimpath \
        -ldflags "-X 'github.com/sagernet/sing-box/constant.Version=%{version}-%{release}%{?dist}' -s -w -buildid=0x$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n')" \
        -tags "with_gvisor,with_dhcp,with_wireguard,with_reality_server,with_clash_api,with_quic,with_utls,with_ech,with_grpc,with_v2ray_api" \
        ./cmd/sing-box


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp %{SOURCE2} %{buildroot}/%{_unitdir}/
mv %{name} %{buildroot}/%{_bindir}/


%files
%{_bindir}/%{name}
%{_unitdir}/%{name}@.service
%attr(0750,root,%{name}) %dir %{_sysconfdir}/%{name}
%attr(0750,%{name},%{name}) %dir %{_sharedstatedir}/%{name}


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
        useradd -r -s /sbin/nologin -d %{_sysconfdir}/%{name} -M \
        -c 'sing-box, The universal proxy platform' -g %{name} %{name}
exit 0


%post
%systemd_post %{name}@.service


%preun
%systemd_preun '%{name}@*.service'


%postun
%systemd_postun_with_restart '%{name}@*.service'


%changelog
* Mon Oct 14 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.7-1
- Initial packaging
