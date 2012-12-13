%define	major	5
%define	minor	0
%define	micro	99
%define	lname	lzma
%define libname %mklibname %{lname} %{major}
%define libdev  %mklibname -d %{lname}

%bcond_without uclibc
%bcond_without dietlibc

Summary: 	XZ utils
Name: 		xz
Version: 	5.1.2
Release: 	0.alpha.2
License: 	Public Domain
Group:		Archiving/Compression
Source0:	http://tukaani.org/xz/%{name}-%{version}alpha.tar.xz
Source1:	xzme
Patch0:		xz-5.1.1alpha-text-tune.patch
%rename		lzma
%rename		lzma-utils
# needed by check suite
BuildRequires:	diffutils
%if %{with uclibc}
BuildRequires:	uClibc-devel
%endif
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
URL:		http://tukaani.org/xz/

%description
XZ Utils is free general-purpose data compression software with high
compression ratio. XZ Utils were written for POSIX-like systems, but also
work on some not-so-POSIX systems.
XZ Utils are the successor to LZMA Utils.

The core of the XZ Utils compression code is based on LZMA SDK,
but it has been modified quite a lot to be suitable for XZ Utils.
The primary compression algorithm is currently LZMA2, which is used inside
the .xz container format. With typical files, XZ Utils create 30 % smaller
output than gzip and 15 % smaller output than bzip2.

XZ Utils consist of several components:

* liblzma is a compression library with API similar to that of zlib.
* xz is a command line tool with syntax similar to that of gzip.
* xzdec is a decompression-only tool smaller than the full-featured xz tool.
* A set of shell scripts (xzgrep, xzdiff, etc.) have been adapted from gzip to
ease viewing, grepping, and comparing compressed files.
* Emulation of command line tools of LZMA Utils eases transition from LZMA
Utils to XZ Utils.

%package -n	%{libname}
Summary:	Libraries for decoding XZ/LZMA compression
Group:		System/Libraries

%description -n	%{libname}
Libraries for decoding LZMA compression.

%package -n	%{libdev}
Summary:	Devel libraries & headers for liblzma
Group:		Development/C
Provides:	%{lname}-devel = %{version}-%{release}
Provides:	lib%{lname}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n %{libdev}
Devel libraries & headers for liblzma.

%prep
%setup -q -n %{name}-%{version}alpha
%patch0 -p1 -b .text~

%build
export CONFIGURE_TOP=`pwd`
mkdir objs
pushd objs
CFLAGS="%{optflags} -Ofast -funroll-loops" \
%configure2_5x
%make
popd

%if %{with dietlibc}
mkdir objsdietlibc
pushd objsdietlibc
CFLAGS="-Os" CC="diet gcc" \
%configure2_5x	--disable-shared \
		--enable-static \
		--disable-xz \
		--disable-xzdec \
		--disable-lzmadec \
		--disable-lzmainfo \
		--disable-lzma-links \
		--disable-scripts
%make
popd
%endif

%if %{with uclibc}
mkdir objsuclibc
pushd objsuclibc
%uclibc_configure \
		--disable-shared \
		--enable-static \
		--disable-xz \
		--disable-xzdec \
		--disable-lzmadec \
		--disable-lzmainfo \
		--disable-lzma-links \
		--disable-scripts

%make
popd
%endif

%install
%makeinstall_std -C objs

install -d %{buildroot}/%{_lib}
mv %{buildroot}%{_libdir}/*.so.* %{buildroot}/%{_lib}/
ln -sf /%{_lib}/liblzma.so.%{major}.%{minor}.%{micro} %{buildroot}%{_libdir}/liblzma.so

%if %{with uclibc}
install -D objsuclibc/src/liblzma/.libs/liblzma.a -D %{buildroot}%{uclibc_root}%{_libdir}/liblzma.a
%endif
%if %{with dietlibc}
install -D objsdietlibc/src/liblzma/.libs/liblzma.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/liblzma.a
%endif

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

%find_lang %{name}

%check
make check -C objs

%files -f %{name}.lang
%doc README THANKS
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
/%{_lib}/lib*.so.%{major}
/%{_lib}/lib*.so.%{major}.%{minor}.%{micro}

%files -n %{libdev}
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%if %{with dietlibc}
%{_prefix}/lib/dietlibc/lib-%{_arch}/liblzma.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/liblzma.a
%endif
%{_libdir}/pkgconfig/lib%{lname}.pc

%changelog
* Thu Dec 13 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.1.2-0.alpha.2
- use %uclibc_configure macro

* Thu Jul 05 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.1.2-0.alpha.1
+ Revision: 808152
- build with -Ofast
- new version

* Thu Mar 29 2012 Bogdano Arendartchuk <bogdano@mandriva.com> 5.1.1-0.alpha.2
+ Revision: 788234
- remove .la files from the file list

* Fri Oct 14 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.1.1-0.alpha.1
+ Revision: 704723
- fix symlink creation for library moved to /%%{_lib}/
- add missing file to %%files
- s/macro/micro/ typo
- new version
- update description

* Fri Jun 10 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.0.3-2
+ Revision: 684196
- move shared library to /%%{_lib}/ (thx to Shlomi Fish for reporting)
- don't remove libtool library file

* Sun May 22 2011 Funda Wang <fwang@mandriva.org> 5.0.3-1
+ Revision: 676969
- new version 5.0.3

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - build uClibc & diet versions of liblzma

* Wed Apr 06 2011 Funda Wang <fwang@mandriva.org> 5.0.2-2
+ Revision: 651010
- rebuild for lost packages

* Wed Apr 06 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.0.2-1
+ Revision: 650921
- add missing mode to open(2)
- strip redundant buildroot cleaning
- fix leak (P1)
- new version

* Wed Mar 23 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.0.1-1
+ Revision: 648164
- remove unneeded %%defattr & buildroot definition
- use %%rename macro
- drop unneeded zlib-devel buildrequires, document diffutils buildrequires
- new version: 5.0.1
- update url

* Wed Dec 15 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 5.0.0-2mdv2011.0
+ Revision: 621846
- update license
- resurrect --text option patch

* Wed Nov 17 2010 Olivier Faurax <ofaurax@mandriva.org> 5.0.0-1mdv2011.0
+ Revision: 598139
- Bump version to 5.0.0

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 4.999.9beta-2mdv2010.1
+ Revision: 524476
- rebuilt for 2010.1

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - update summary & description due to lzma -> xz name change

* Thu Sep 03 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.9beta-1mdv2010.0
+ Revision: 428978
- update to 4.999.9beta

* Mon Mar 09 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.8beta-0.2mdv2009.1
+ Revision: 353301
- add back recompression tool (xzme, renamed from lzme, now using xz format, fixes #48231)

* Sun Jan 25 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.8beta-0.1mdv2009.1
+ Revision: 333378
- update to latest code from git (contains some fixes required by pyliblzma 0.5.0)

* Thu Jan 08 2009 Funda Wang <fwang@mandriva.org> 4.999.7-0.beta.2mdv2009.1
+ Revision: 327157
- rebuild

* Mon Jan 05 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.7-0.beta.1mdv2009.1
+ Revision: 325129
- update to 4.999.7beta

* Tue Dec 30 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.6-0.alpha.6mdv2009.1
+ Revision: 321391
- add lzme util from older lzma package (should become xzme eventually..)

* Mon Dec 29 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.6-0.alpha.5mdv2009.1
+ Revision: 321121
- rename to 'xz'
- add text tune patch (P1) which provides same --text option as we introduced for
  old tool..
- update source, new tool and format has now been renamed to 'xz'
- rename

* Mon Dec 22 2008 Oden Eriksson <oeriksson@mandriva.com> 4.999.6-0.alpha.4mdv2009.1
+ Revision: 317511
- fix major, he he he, funny!

* Sun Dec 21 2008 Oden Eriksson <oeriksson@mandriva.com> 4.999.6-0.alpha.3mdv2009.1
+ Revision: 317047
- rebuild

* Sun Oct 19 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.6-0.alpha.2mdv2009.1
+ Revision: 295258
- d'oh, bump major again due to lzmalib conflicts

* Fri Oct 17 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.6-0.alpha.1mdv2009.1
+ Revision: 294620
- * new release
  * ditch lzma-4.999.3alpha-use-lzma_alone-format-by-default.patch, this is now the
  default
  * bump major (P1)

* Fri Jul 18 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.3-0.alpha.3mdv2009.0
+ Revision: 238248
- new git snapshot
- drop P1 (fixed upstream)
- drop ldconfig scriptlets since package is new and doesn't exist in older releases

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon May 12 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.3-0.alpha.2mdv2009.0
+ Revision: 206503
- remove help text about options not available for LZMA_Alone (updates P0)
- handle broken pipe (P1)
- build with -O3 & -funroll-loops

* Sun May 04 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.999.3-0.alpha.1mdv2009.0
+ Revision: 201109
- provide liblzma-devel
- import lzma-utils


* Thu Apr 30 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.99.3alpha-1
- initial Mandriva release.
