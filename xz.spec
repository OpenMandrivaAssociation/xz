%define major 5
%define lname lzma
%define libname %mklibname %{lname} %{major}
%define libdev %mklibname -d %{lname}

Summary:	XZ utils
Name:		xz
Version:	5.2.4
Release:	4
License:	Public Domain
Group:		Archiving/Compression
URL:		http://tukaani.org/xz/
Source0:	http://tukaani.org/xz/%{name}-%{version}.tar.xz
Source1:	xzme
Source2:	%{name}.rpmlintrc
Patch0:		xz-5.2.0-text-tune.patch
Patch1:		xz-5.1.3alpha-man-page-day.patch
# (tpg) ClearLinux patches
Patch2:		default-threading.patch
Patch3:		io-size.patch
Patch4:		speedup.patch
# (tpg) this works only when __cc is set to clang
# (tpg) enable PGO
%ifnarch riscv64
Patch5:		add-pgo.patch
%endif
%rename		lzma
%rename		lzma-utils
# needed by check suite
BuildRequires:	diffutils

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

%package -n %{libname}
Summary:	Libraries for decoding XZ/LZMA compression
Group:		System/Libraries

%description -n %{libname}
Libraries for decoding LZMA compression.

%package -n %{libdev}
Summary:	Devel libraries & headers for liblzma
Group:		Development/C
Provides:	%{lname}-devel = %{EVRD}
Provides:	lib%{lname}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

%description -n %{libdev}
Devel libraries & headers for liblzma.

%prep
%autosetup -p1

%build
%global optflags %{optflags} -O3 -falign-functions=32 -fno-math-errno -fno-trapping-math

%configure --enable-static \
%ifarch %{ix86} %{x86_64}
    --enable-assume-ram=1024
%endif

%ifnarch riscv64
%make_build pgo-build
%else
%make_build
%endif

%install
%make_install

install -d %{buildroot}/%{_lib}
rm %{buildroot}%{_libdir}/liblzma.so
mv %{buildroot}%{_libdir}/liblzma.so.%{major}* %{buildroot}/%{_lib}
ln -sr %{buildroot}/%{_lib}/liblzma.so.%{major}.* %{buildroot}%{_libdir}/liblzma.so

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

%find_lang %{name}

%check
make check

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
%{_libdir}/pkgconfig/lib%{lname}.pc
