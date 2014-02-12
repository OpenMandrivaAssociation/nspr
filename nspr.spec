%define major 4
%define libname %mklibname nspr %{major}
%define devname %mklibname nspr -d

Summary:	Netscape Portable Runtime
Name:		nspr
Epoch:		2
Version:	4.10.3
Release:	1
License:	MPL or GPLv2+ or LGPLv2+
Group:		System/Libraries
Url:		http://www.mozilla.org/projects/nspr/
Source0:	https://ftp.mozilla.org/pub/mozilla.org/%{name}/releases/v%{version}/src/%{name}-%{version}.tar.gz
Source1:	nspr.pc.in
Source2:	nspr-config-vars.in
Patch1:		nspr-config-pc.patch
Patch2:		fix-config-sg-aarch64.patch
Patch3:		nspr-prcpucfg-aarch64.patch

%description
Virtual package, not built.

%package -n %{libname}
Summary:	Netscape Portable Runtime
Group:		System/Libraries
Provides:	nspr = %{EVRD}
%rename	mozilla-nspr

%description -n %{libname}
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free) and shared library linking.

%package -n %{devname}
Summary:	Development libraries for the Netscape Portable Runtime
Group:		Development/C++
Requires:	%{libname} = %{EVRD}
Provides:	nspr-devel = %{EVRD}

%description -n %{devname}
Header files for doing development with the Netscape Portable Runtime.

%prep
%setup -q

chmod -R a+r *
find . -name '*.h' -executable -exec chmod -x {} \;

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be 
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./nspr/config/nspr-config.in ./nspr/config/nspr-config-pc.in
%patch1 -p1
%patch2 -p1
%patch3 -p1

cp %{SOURCE2} ./nspr/config/

%build
# partial RELRO support as a security enhancement
LDFLAGS+=-Wl,-z,relro
export LDFLAGS
%setup_compile_flags

# (tpg) don't use macro here
./nspr/configure \
	--build=%{_host_platform} \
	--host=%{_target_platform} \
	--target=%{_target_platform} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--includedir=%{_includedir}/nspr4 \
	--host=%{_host_platform} \
%ifarch x86_64 ppc64 ia64 s390x sparc64 aarch64
	--enable-64bit \
%endif
	--enable-optimize="-O2" \
%ifarch armv7l armv7hl armv7nhl
	--enable-thumb2 \
%endif
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
mkdir -p %{buildroot}/%{_libdir}/pkgconfig

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

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}/%{_lib}
install -m755 -D ./config/nspr-config-pc %{buildroot}/%{_bindir}/nspr-config

# Get rid of the things we don't want installed (per upstream)
rm -rf \
   %{buildroot}%{_bindir}/compile-et.pl \
   %{buildroot}%{_bindir}/prerr.properties \
   %{buildroot}%{_libdir}/libnspr4.a \
   %{buildroot}%{_libdir}/libplc4.a \
   %{buildroot}%{_libdir}/libplds4.a \
   %{buildroot}%{_datadir}/aclocal/nspr.m4 \
   %{buildroot}%{_includedir}/nspr4/md

# nb: those symlinks helps having devel(xxx) provides (through find-provides)
for file in libnspr4.so libplc4.so libplds4.so
do
  mv -f %{buildroot}%{_libdir}/$file %{buildroot}/%{_lib}/$file
  ln -sf ../../%{_lib}/$file %{buildroot}%{_libdir}/$file
done

%files -n %{libname}
/%{_lib}/libnspr4.so
/%{_lib}/libplc4.so
/%{_lib}/libplds4.so

%files -n %{devname}
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config

