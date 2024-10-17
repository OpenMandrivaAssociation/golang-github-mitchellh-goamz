%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 0
# ec2,elb failing locally
# rds,iam,route53,s3,autoscaling,aws,exp/mturk,exp/sdb,exp/sns locally ok
%global with_check 0
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         mitchellh
%global repo            goamz
# https://github.com/mitchellh/goamz
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          caaaea8b30ee15616494ee68abd5d8ebbbef05cf
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0
Release:        0.16.git%{shortcommit}%{?dist}
Summary:        An Amazon Library for Go
License:        LGPLv3+
URL:            https://%{import_path}
Source0:        https://github.com/%{project}/%{repo}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
BuildRequires: golang(github.com/motain/gocheck)
BuildRequires: golang(github.com/vaughan0/go-ini)
%endif

Requires:      golang(github.com/motain/gocheck)
Requires:      golang(github.com/vaughan0/go-ini)

Provides:      golang(%{import_path}/autoscaling) = %{version}-%{release}
Provides:      golang(%{import_path}/aws) = %{version}-%{release}
Provides:      golang(%{import_path}/ec2) = %{version}-%{release}
Provides:      golang(%{import_path}/ec2/ec2test) = %{version}-%{release}
Provides:      golang(%{import_path}/elb) = %{version}-%{release}
Provides:      golang(%{import_path}/exp/mturk) = %{version}-%{release}
Provides:      golang(%{import_path}/exp/sdb) = %{version}-%{release}
Provides:      golang(%{import_path}/exp/sns) = %{version}-%{release}
Provides:      golang(%{import_path}/iam) = %{version}-%{release}
Provides:      golang(%{import_path}/iam/iamtest) = %{version}-%{release}
Provides:      golang(%{import_path}/rds) = %{version}-%{release}
Provides:      golang(%{import_path}/route53) = %{version}-%{release}
Provides:      golang(%{import_path}/s3) = %{version}-%{release}
Provides:      golang(%{import_path}/s3/s3test) = %{version}-%{release}
Provides:      golang(%{import_path}/testutil) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}/autoscaling
%gotest %{import_path}/aws
%gotest %{import_path}/ec2
%gotest %{import_path}/elb
%gotest %{import_path}/exp/mturk
%gotest %{import_path}/exp/sdb
%gotest %{import_path}/exp/sns
%gotest %{import_path}/iam
%gotest %{import_path}/rds
%gotest %{import_path}/route53
%gotest %{import_path}/s3
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc CHANGES.md README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test -f unit-test.file-list
%license LICENSE
%doc CHANGES.md README.md
%endif

%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.16.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.15.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.14.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.13.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.12.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.11.gitcaaaea8
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.10.gitcaaaea8
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.9.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 12 2015 jchaloup <jchaloup@redhat.com> - 0-0.8.gitcaaaea8
- Update to spec-2.1
  related: #1223451

* Fri Aug 07 2015 Fridolin Pokorny <fpokorny@redhat.com> - 0-0.7.gitcaaaea8
- Update spec file to spec-2.0
  resolves: #1223451

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.6.gitcaaaea8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.5.gitcaaaea8
- Bump to upstream caaaea8b30ee15616494ee68abd5d8ebbbef05cf
- Add license macro
- Remove runtime dependency on golang
  resolves: #1223451

* Tue Jan 13 2015 jchaloup <jchaloup@redhat.com> - 0-0.4.git32d1910
- Bump to upstream 32d1910e654ead1308d9073d8ccdd42d6922ee39
  related: #1142399

* Fri Oct 10 2014 jchaloup <jchaloup@redhat.com> - 0-0.3.git9cad7da
- Add dependencies, replace motain/gocheck with check.v1
  related: #1142399

* Fri Sep 19 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.2.git9cad7da
- Resolves: rhbz#1142399 - initial package upload
- don't redefine gopath
- don't own dirs owned by golang
- preserve timestamps of copied files
- devel package buildrequires golang
- noarch
- correct package name format

* Mon Sep 15 2014 Eric Paris <eparis@redhat.com - 0.0.0-0.1.git9cad7da
- Bump to upstream 9cad7da945e699385c1a3e115aa255211921c9bb


