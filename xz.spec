%define major 5
%define lname lzma
%define libname %mklibname %{lname} %{major}
%define libdev %mklibname -d %{lname}

%bcond_with dietlibc

Summary:	XZ utils
Name:		xz
Version:	5.2.3
%define	gitdate	%{nil}
%if "%{gitdate}" != ""
Release:	0.beta.%{gitdate}.1
Source0:	http://tukaani.org/xz/%{name}-%{version}beta.tar.xz
%else
Release:	4
Source0:	http://tukaani.org/xz/%{name}-%{version}.tar.xz
%endif
License:	Public Domain
Group:		Archiving/Compression
Source1:	xzme
Source2:	%{name}.rpmlintrc
Patch0:		xz-5.2.0-text-tune.patch
Patch1:		xz-5.1.3alpha-man-page-day.patch
# (tpg) ClearLinux patches
Patch2:		default-threading.patch
Patch3:		io-size.patch
Patch4:		speedup.patch
%rename		lzma
%rename		lzma-utils
# needed by check suite
BuildRequires:	diffutils
%if %{with dietlibc}
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
%if "%{gitdate}" != ""
%setup -q -n %{name}-%{version}beta
%else
%setup -q
%endif

%apply_patches

%build
export CONFIGURE_TOP="$PWD"

%if %{with dietlibc}
mkdir -p objsdietlibc
pushd objsdietlibc
CFLAGS="-Os" CC="diet gcc" \
%configure	--disable-shared \
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

mkdir -p objs
pushd objs
%global optflags %{optflags} -Ofast -funroll-loops
%configure --enable-static
%make
popd

%install
%if %{with dietlibc}
install -D objsdietlibc/src/liblzma/.libs/liblzma.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/liblzma.a
%endif

%makeinstall_std -C objs

install -d %{buildroot}/%{_lib}
rm %{buildroot}%{_libdir}/liblzma.so
mv %{buildroot}%{_libdir}/liblzma.so.%{major}* %{buildroot}/%{_lib}
ln -sr %{buildroot}/%{_lib}/liblzma.so.%{major}.* %{buildroot}%{_libdir}/liblzma.so

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

%find_lang %{name}

%check
make check -C objs

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
/%{_lib}/liblzma.so.%{major}*

%files -n %{libdev}
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/liblzma.so
%{_libdir}/liblzma.a
%if %{with dietlibc}
%{_prefix}/lib/dietlibc/lib-%{_arch}/liblzma.a
%endif
%{_libdir}/pkgconfig/lib%{lname}.pc
