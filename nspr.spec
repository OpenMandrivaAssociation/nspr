%define major_nspr 4
%define epoch_nspr 2
%define libname %mklibname nspr %{major_nspr}
%define develname %mklibname nspr -d

Summary:	Netscape Portable Runtime
Name:		nspr
Epoch:		%{epoch_nspr}
Version:	4.7.3
Release:	%mkrel 2
License:	MPL/GPL/LGPL
Group:		System/Libraries
URL:		http://www.mozilla.org/projects/nspr/
Source0:	ftp://ftp.mozilla.org/pub/mozilla.org/nspr/releases/v%{version}/src/%{name}-%{version}.tar.gz
Source1:	nspr.pc.in
Source2:	nspr-config-vars.in
Patch1:		nspr-config-pc.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
Virtual package, not built.

%package -n %{libname}
Summary:	Netscape Portable Runtime
Group:		System/Libraries
Obsoletes:	mozilla-nspr
Provides:	nspr = %{epoch_nspr}:%{version}-%{release}
Provides:	mozilla-nspr = %{epoch_nspr}:%{version}-%{release}

%description -n %{libname}
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free) and shared library linking.

%package -n %{develname}
Summary:	Development libraries for the Netscape Portable Runtime
Group:		Development/C++
Requires:	%{libname} = %{epoch_nspr}:%{version}-%{release}
Obsoletes:	mozilla-nspr-devel
Obsoletes:	nspr-devel
Obsoletes:	%{libname}-devel
Provides:	nspr-devel = %{epoch_nspr}:%{version}-%{release}
Provides:	libnspr-devel = %{epoch_nspr}:%{version}-%{release}
# explicitly provides those, since the libs are not in the develpackage
# (and are not symlink so find-provides does not do it magically)
Provides:	devel(libnspr4.so)
Provides:	devel(libplc4.so)
Provides:	devel(libplds4.so)

%description -n %{develname}
Header files for doing development with the Netscape Portable Runtime.

%prep
%setup -q

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be 
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./mozilla/nsprpub/config/nspr-config.in ./mozilla/nsprpub/config/nspr-config-pc.in
%patch1 -p0

cp %{SOURCE2} ./mozilla/nsprpub/config/

%build
./mozilla/nsprpub/configure \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--includedir=%{_includedir}/nspr4 \
%ifarch x86_64 ppc64 ia64 s390x
	--enable-64bit \
%endif
	--enable-optimize="%{optflags}" \
	--disable-debug \
	--enable-ipv6 \
	--with-pthreads \
	--with-mozilla

%make

%install
%makeinstall_std 

NSPR_LIBS=`./config/nspr-config --libs`
NSPR_CFLAGS=`./config/nspr-config --cflags`
NSPR_VERSION=`./config/nspr-config --version`
%{__mkdir_p} %{buildroot}/%{_libdir}/pkgconfig

cat ./config/nspr-config-vars > \
                     %{buildroot}/%{_libdir}/pkgconfig/nspr.pc

cat %{SOURCE1} | sed -e "s,%%libdir%%,%{_libdir},g" \
                     -e "s,%%prefix%%,%{_prefix},g" \
                     -e "s,%%exec_prefix%%,%{_prefix},g" \
                     -e "s,%%includedir%%,%{_includedir}/nspr4,g" \
                     -e "s,%%NSPR_VERSION%%,$NSPR_VERSION,g" \
                     -e "s,%%FULL_NSPR_LIBS%%,$NSPR_LIBS,g" \
                     -e "s,%%FULL_NSPR_CFLAGS%%,$NSPR_CFLAGS,g" >> \
                     %{buildroot}/%{_libdir}/pkgconfig/nspr.pc

%{__mkdir_p} %{buildroot}/%{_bindir}
%{__cp} ./config/nspr-config-pc %{buildroot}/%{_bindir}/nspr-config

# Get rid of the things we don't want installed (per upstream)
%{__rm} -rf \
   %{buildroot}/%{_bindir}/compile-et.pl \
   %{buildroot}/%{_bindir}/prerr.properties \
   %{buildroot}/%{_libdir}/libnspr4.a \
   %{buildroot}/%{_libdir}/libplc4.a \
   %{buildroot}/%{_libdir}/libplds4.a \
   %{buildroot}/%{_datadir}/aclocal/nspr.m4 \
   %{buildroot}/%{_includedir}/nspr4/md

%clean
%{__rm} -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config