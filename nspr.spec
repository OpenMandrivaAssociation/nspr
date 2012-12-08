%define major_nspr 4
%define epoch_nspr 2
%define libname %mklibname nspr %{major_nspr}
%define develname %mklibname nspr -d

Summary:	Netscape Portable Runtime
Name:		nspr
Epoch:		%{epoch_nspr}
Version:	4.9.2
Release:	1
License:	MPL or GPLv2+ or LGPLv2+
Group:		System/Libraries
URL:		http://www.mozilla.org/projects/nspr/
Source0:	https://ftp.mozilla.org/pub/mozilla.org/%{name}/releases/v%{version}/src/%{name}-%{version}.tar.gz
Source1:	nspr.pc.in
Source2:	nspr-config-vars.in
Patch1:		nspr-config-pc.patch

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

%package -n %{develname}
Summary:	Development libraries for the Netscape Portable Runtime
Group:		Development/C++
Requires:	%{libname} = %{epoch_nspr}:%{version}-%{release}
Provides:	nspr-devel = %{epoch_nspr}:%{version}-%{release}
Provides:	libnspr-devel = %{epoch_nspr}:%{version}-%{release}
Conflicts:	%{libname} < 2:4.7.3-3
%rename mozilla-nspr-devel
%rename %{libname}-devel

%description -n %{develname}
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

cp ./mozilla/nsprpub/config/nspr-config.in ./mozilla/nsprpub/config/nspr-config-pc.in
%patch1 -p1

cp %{SOURCE2} ./mozilla/nsprpub/config/

%build
%setup_compile_flags

# (tpg) don't use macro here
./mozilla/nsprpub/configure \
	--build=%{_target_platform} \
	--host=%{_host} \
	--target=%{_target_platform} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--includedir=%{_includedir}/nspr4 \
%ifarch x86_64 ppc64 ia64 s390x sparc64
	--enable-64bit \
%endif
	--enable-optimize="-O2" \
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

%{__mkdir_p} %{buildroot}%{_bindir}
%{__mkdir_p} %{buildroot}/%{_lib}
install -m755 -D ./config/nspr-config-pc %{buildroot}/%{_bindir}/nspr-config

# Get rid of the things we don't want installed (per upstream)
%{__rm} -rf \
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
%defattr(-,root,root)
/%{_lib}/libnspr4.so
/%{_lib}/libplc4.so
/%{_lib}/libplds4.so

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config


%changelog
* Tue Jun 05 2012 Oden Eriksson <oeriksson@mandriva.com> 2:4.9.1-1mdv2012.0
+ Revision: 802605
- 4.9.1

* Sat Mar 17 2012 Oden Eriksson <oeriksson@mandriva.com> 2:4.9.0-2
+ Revision: 785446
- revert rpm5 only crap
- the version is really 4.9.0

* Tue Feb 21 2012 Dmitry Mikhirev <dmikhirev@mandriva.org> 2:4.9-1
+ Revision: 778604
- new version 4.9

* Fri Aug 12 2011 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.9-1
+ Revision: 694116
- 4.8.9

* Mon May 09 2011 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.8-1
+ Revision: 672998
- 4.8.8

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.7-4
+ Revision: 666626
- mass rebuild

* Sat Feb 26 2011 Funda Wang <fwang@mandriva.org> 2:4.8.7-3
+ Revision: 639990
- rebuild

* Tue Jan 18 2011 Funda Wang <fwang@mandriva.org> 2:4.8.7-2
+ Revision: 631403
- fix perm

* Fri Jan 14 2011 Funda Wang <fwang@mandriva.org> 2:4.8.7-1
+ Revision: 631032
- 4.8.7 final

* Wed Jan 05 2011 Funda Wang <fwang@mandriva.org> 2:4.8.7-0.beta2.1mdv2011.0
+ Revision: 628683
- sync with fedora's 4.8.7 beta2

* Thu Sep 09 2010 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.6-2mdv2011.0
+ Revision: 576967
- fix backporting to older products

* Sat Aug 21 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.8.6-1mdv2011.0
+ Revision: 571549
- update to new version 4.8.6

* Tue Apr 13 2010 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.4-2mdv2010.1
+ Revision: 534195
- added backporting magic for updates

* Sat Mar 06 2010 Oden Eriksson <oeriksson@mandriva.com> 2:4.8.4-1mdv2010.1
+ Revision: 515286
- 4.8.4

* Wed Nov 11 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.8.2-1mdv2010.1
+ Revision: 464879
- update to new version 4.8.2

* Sat May 30 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.8-1mdv2010.0
+ Revision: 381476
- update to new version 4.8
- enable-optimise takes only one value i.e -O2

* Fri May 01 2009 Funda Wang <fwang@mandriva.org> 2:4.7.4-1mdv2010.0
+ Revision: 369465
- New version 4.7.4

* Mon Dec 22 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.7.3-5mdv2009.1
+ Revision: 317684
- compile with %%setup_compile_flags
- spec file clean

* Mon Dec 08 2008 Funda Wang <fwang@mandriva.org> 2:4.7.3-4mdv2009.1
+ Revision: 311802
- add conflicts fo ease upgrading
- clearify license

* Mon Dec 08 2008 Pixel <pixel@mandriva.com> 2:4.7.3-3mdv2009.1
+ Revision: 311733
- sync with fedora (gives automatic devel(xxx) provides) (thanks fwang)

* Fri Dec 05 2008 Pixel <pixel@mandriva.com> 2:4.7.3-2mdv2009.1
+ Revision: 310748
- add explicit devel(libnspr4.so) devel(libplc4.so) devel(libplds4.so)
  (since find-provides do not handle these non standard libs)

* Thu Nov 13 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.7.3-1mdv2009.1
+ Revision: 302797
- update to new version 4.7.3

* Thu Aug 07 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2:4.7.1-1mdv2009.0
+ Revision: 265433
- update to new version 4.7.1
- drop patch 2, fixed upstream
- enable ipv6 and pthreads support

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 2:4.6.8-2mdv2009.0
+ Revision: 223349
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed Feb 13 2008 Marcelo Ricardo Leitner <mrl@mandriva.com> 2:4.6.8-1mdv2008.1
+ Revision: 167163
- New upstream: 4.6.8

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Jul 20 2007 Funda Wang <fwang@mandriva.org> 2:4.6.7-1mdv2008.0
+ Revision: 53835
- New version


* Thu Mar 01 2007 Götz Waschk <waschk@mandriva.org> 4.6.5-4mdv2007.0
+ Revision: 130285
- rebuild to fix pkgconfig provides

* Sun Feb 18 2007 Christiaan Welvaart <cjw@daneel.dyndns.org> 2:4.6.5-3mdv2007.1
+ Revision: 122384
- rebuild to fix automatic pkgconfig() provides

* Fri Feb 09 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 2:4.6.5-2mdv2007.1
+ Revision: 118426
- Bumped rel.

* Thu Feb 08 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 2:4.6.5-1mdv2007.1
+ Revision: 117830
- Adapted to Mandriva.
- Import nspr

* Mon Jan 22 2007 Wan-Teh Chang <wtchang@redhat.com> - 4.6.5-1
- Update to 4.6.5

* Tue Jan 16 2007 Kai Engert <kengert@redhat.com> - 4.6.4-2
- Include upstream patch to fix ipv6 support (rhbz 222554)

* Tue Nov 21 2006 Kai Engert <kengert@redhat.com> - 4.6.4-1
- Update to 4.6.4

* Fri Sep 15 2006 Kai Engert <kengert@redhat.com> - 4.6.3-1
- Update to 4.6.3

* Thu Jul 13 2006 Jesse Keating <jkeating@redhat.com> - 4.6.2-1.1
- rebuild

* Sat May 27 2006 Kai Engert <kengert@redhat.com> - 4.6.2-1
- Update to 4.6.2
- Tweak nspr-config to be identical on all platforms.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4.6.1-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.6.1-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Jan 05 2006 Kai Engert <kengert@redhat.com> 4.6.1-2
- Do not use -ansi when compiling, because of a compilation
  problem with latest glibc and anonymous unions.
  See also bugzilla.mozilla.org # 322427.

* Wed Jan 04 2006 Kai Engert <kengert@redhat.com>
- Add an upstream patch to fix gcc visibility issues.

* Tue Jan 03 2006 Christopher Aillon <caillon@redhat.com>
- Stop shipping static libraries; NSS and dependencies no longer
  require static libraries to build.

* Thu Dec 15 2005 Christopher Aillon <caillon@redhat.com> 4.6.1-1
- Update to 4.6.1

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sat Jul 16 2005 Christopher Aillon <caillon@redhat.com> 4.6-4
- Use the NSPR version numbering scheme reported by NSPR,
  which unfortunately is not exactly the same as the real
  version (4.6 != 4.6.0 according to RPM and pkgconfig).

* Sat Jul 16 2005 Christopher Aillon <caillon@redhat.com> 4.6-3
- Correct the CFLAGS reported by pkgconfig

* Wed Jul 13 2005 Christopher Aillon <caillon@redhat.com> 4.6-2
- Temporarily include the static libraries allowing nss and 
  its dependencies to build.

* Wed Jul 13 2005 Christopher Aillon <caillon@redhat.com> 4.6-1
- Update to NSPR 4.6

* Thu Apr 21 2005 Christopher Aillon <caillon@redhat.com> 4.4.1-2
- NSPR doesn't have make install, but it has make real_install.  Use it.

* Fri Apr 15 2005 Christopher Aillon <caillon@redhat.com> 4.4.1-1
- Let's make an RPM.

