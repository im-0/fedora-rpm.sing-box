# debuginfo seems to only work with gccgo.
%global debug_package %{nil}

%global tarball_version %%( echo %{version} | sed -E "s,~([^0-9]+)([0-9]+)$,-\\1.\\2," )

Name:       sing-box
Version:    1.12.10
Release:    1%{?dist}
Summary:    The universal proxy platform

License:    GPL-3.0-or-later
URL:        https://github.com/SagerNet/sing-box
Source0:    https://github.com/SagerNet/sing-box/archive/v%{tarball_version}/%{name}-%{tarball_version}.tar.gz

# $ GOPROXY=https://proxy.golang.org go mod vendor -v
# Contains $name-$tarball_version/vendor/*.
Source1:    %{name}-%{tarball_version}.go-mod-vendor.tar.xz

Source2:    sing-box@.service

BuildRequires:  systemd-rpm-macros
BuildRequires:  golang >= 1.23.1


%description
The universal proxy platform.


%prep
%setup -q -D -T -b0 -n %{name}-%{tarball_version}
%setup -q -D -T -b1 -n %{name}-%{tarball_version}


%build
go build -v \
        -trimpath \
        -ldflags "-X 'github.com/sagernet/sing-box/constant.Version=%{version}-%{release}.%{_build_arch}' -s -w -buildid=0x$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n')" \
        -tags "with_gvisor,with_dhcp,with_wireguard,with_clash_api,with_quic,with_utls,with_grpc,with_v2ray_api,with_acme,with_tailscale" \
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
        useradd -r -s /sbin/nologin -d %{_sharedstatedir}/%{name} -M \
        -c 'sing-box, The universal proxy platform' -g %{name} %{name}
exit 0


%post
%systemd_post %{name}@.service


%preun
%systemd_preun '%{name}@*.service'


%postun
%systemd_postun_with_restart '%{name}@*.service'


%changelog
* Thu Oct 16 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.10-1
- Update to 1.12.10

* Tue Oct 7 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.9-1
- Update to 1.12.9

* Tue Sep 16 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.8-1
- Update to 1.12.8

* Thu Sep 11 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.5-1
- Update to 1.12.5

* Fri Aug 29 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.4-1
- Update to 1.12.4

* Sat Aug 23 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.3-1
- Update to 1.12.3

* Mon Aug 11 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.12.1-1
- Update to 1.12.1

* Tue May 20 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.11-1
- Update to 1.11.11

* Mon May 05 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.10-1
- Update to 1.11.10

* Mon Apr 28 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.9-1
- Update to 1.11.9

* Sat Apr 19 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.8-1
- Update to 1.11.8

* Tue Apr 8 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.7-1
- Update to 1.11.7

* Thu Mar 27 2025 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.6-1
- Update to 1.11.6

* Sat Oct 19 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.11.5-1
- Update to 1.11.5

* Sat Oct 19 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.1-2
- Better patches to support name resolution within rules

* Thu Oct 17 2024 Ivan Mironov <mironov.ivan@gmail.com> - 1.10.1-1
- Update to 1.10.1
- Allow FakeIP while resolving names in inbound

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
