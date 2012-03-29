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
Version: 	5.1.1
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
CFLAGS="%{optflags} -O3 -funroll-loops" \
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
CFLAGS="%{uclibc_cflags}" LDFLAGS="%{?ldflags}" CC="%{uclibc_cc}" \
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
