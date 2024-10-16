# debuginfo seems to only work with gccgo.
%global debug_package %{nil}

%global tarball_version %%( echo %{version} | sed -E "s,~([^0-9]+)([0-9]+)$,-\\1.\\2," )

Name:       sing-box
Version:    1.10.0
Release:    1%{?dist}
Summary:    The universal proxy platform 

License:    GPL-3.0-or-later
URL:        https://github.com/SagerNet/sing-box
Source0:    https://github.com/SagerNet/sing-box/archive/v%{tarball_version}/%{name}-%{tarball_version}.tar.gz

# $ GOPROXY=https://proxy.golang.org go mod vendor -v
# Contains %{name}-%{tarball_version}/vendor/*.
Source1:    %{name}-%{tarball_version}.go-mod-vendor.tar.xz

Source2:    sing-box@.service

BuildRequires:  systemd-rpm-macros
BuildRequires:  golang >= 1.21.0


%description
The universal proxy platform.


%prep
%setup -q -D -T -b0 -n %{name}-%{tarball_version}
%setup -q -D -T -b1 -n %{name}-%{tarball_version}


%build
go build -v \
        -trimpath \
        -ldflags "-X 'github.com/sagernet/sing-box/constant.Version=%{version}-%{release}.%{_build_arch}' -s -w -buildid=0x$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n')" \
        -tags "with_gvisor,with_dhcp,with_wireguard,with_reality_server,with_clash_api,with_quic,with_utls,with_ech,with_grpc,with_v2ray_api" \
        ./cmd/sing-box

./sing-box completion bash >%{name}.bash
./sing-box completion fish >%{name}.fish
./sing-box completion zsh >%{name}.zsh


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions
mkdir -p %{buildroot}%{_datadir}/fish/vendor_completions.d
mkdir -p %{buildroot}%{_datadir}/zsh/vendor-completions
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp %{SOURCE2} %{buildroot}/%{_unitdir}/
mv %{name} %{buildroot}/%{_bindir}/

mv %{name}.bash %{buildroot}%{_datadir}/bash-completion/completions/
mv %{name}.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/
mv %{name}.zsh %{buildroot}%{_datadir}/zsh/vendor-completions/_%{name}


%files
%{_bindir}/%{name}
%{_unitdir}/%{name}@.service
%{_datadir}/bash-completion/completions/%{name}.bash
%{_datadir}/fish/vendor_completions.d/%{name}.fish
%{_datadir}/zsh/vendor-completions/_%{name}
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
* Wed Oct 16 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Wed Oct 16 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.0~rc1-3
- Allow read-write access to /dev/net/tun

* Tue Oct 15 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.0~rc1-2
- Create /var/lib/sing-box/$CONN_NAME before starting the service

* Mon Oct 14 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.0~rc1-1
- Update to 1.10.0-rc.1

* Mon Oct 14 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.9.7-1
- Initial packaging
