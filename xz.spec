%define major 5
%define lname lzma
%define libname %mklibname %{lname} %{major}
%define libdev %mklibname -d %{lname}

# (tpg) enable PGO build
%bcond_without pgo

Summary:	XZ utils
Name:		xz
Version:	5.2.4
Release:	7
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
Provides:	xz-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

%description -n %{libdev}
Devel libraries & headers for liblzma.

%prep
%autosetup -p1

%build
%global optflags %{optflags} -O3 -falign-functions=32 -fno-math-errno -fno-trapping-math

%if %{with pgo}
export LLVM_PROFILE_FILE="%{name}-%p.profile.d"
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" \
%configure --enable-static \
%ifarch %{ix86} %{x86_64}
    --enable-assume-ram=1024
%endif

%make_build check

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile $(find . -type f -name "*.profile.d")
make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%configure --enable-static \
%ifarch %{ix86} %{x86_64}
    --enable-assume-ram=1024
%endif

%make_build

%install
%make_install

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

%find_lang %{name}

%check
make check

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/liblzma.so.%{major}*

%files -n %{libdev}
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/liblzma.so
%{_libdir}/liblzma.a
%{_libdir}/pkgconfig/lib%{lname}.pc
