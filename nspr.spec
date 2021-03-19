%define major 4
%define libname %mklibname nspr %{major}
%define devname %mklibname nspr -d

Summary:	Netscape Portable Runtime
Name:		nspr
Version:	4.30
Release:	1
License:	MPL or GPLv2+ or LGPLv2+
Group:		System/Libraries
Url:		http://www.mozilla.org/projects/nspr/
Source0:	https://ftp.mozilla.org/pub/nspr/releases/v%{version}/src/%{name}-%{version}.tar.gz
Source1:	nspr.pc.in
Source2:	nspr-config-vars.in
Patch1:		nspr-config-pc.patch
Patch2:		nspr-4.8.9-link-flags.patch
#Patch3:		nspr-riscv64.patch

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
%autopatch -p1

cp %{SOURCE2} ./nspr/config/

# Respect LDFLAGS
sed -i -e 's/\$(MKSHLIB) \$(OBJS)/\$(MKSHLIB) \$(LDFLAGS) \$(OBJS)/g' \
	nspr/config/rules.mk

#mv nspr/configure.in nspr/configure.ac
#rm -f nspr/configure
#pushd nspr
#autoreconf -fiv
#popd

%build
%config_update
# partial RELRO support as a security enhancement
LDFLAGS+=-Wl,-z,relro
export LDFLAGS
%setup_compile_flags

# (tpg) don't use macro here
./nspr/configure \
	--build=%{_target_platform} \
	--host=%{_host} \
	--target=%{_target_platform} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--includedir=%{_includedir}/nspr4 \
%ifarch %{x86_64} ppc64 ia64 s390x sparc64 %{aarch64} riscv64
	--enable-64bit \
%endif
	--enable-optimize="%{optflags} -Ofast" \
%ifarch %arm
	--enable-thumb2 \
%endif
	--disable-debug \
	--enable-ipv6 \
	--with-pthreads \
	--with-mozilla

%make_build

%install
# hack
# test\n\remove it on next update
touch pr/src/libnspr4.a
touch lib/ds/libplds4.a
touch lib/libc/src/libplc4.a
%make_install

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

