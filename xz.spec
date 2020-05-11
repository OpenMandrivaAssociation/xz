# -fno-lto is a workaround for getting unresolved symbols in
# the 32-bit x86_64 library with gcc 10.0
# We add -flto manually for the 64bit builds, so nothing is lost
%global _disable_lto 1
%global optflags %{optflags} -O3 -falign-functions=32 -fno-math-errno -fno-trapping-math

%define major 5
%define lname lzma
%define libname %mklibname %{lname} %{major}
%define libdev %mklibname -d %{lname}
%define libstatic %mklibname -s -d %{lname}

# liblzma is used by libxml, which in turn is used by wine.
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif
%if %{with compat32}
%define lib32name lib%{lname}%{major}
%define dev32name lib%{lname}-devel
%define static32name lib%{lname}-static-devel
%endif

# (tpg) enable PGO build
%bcond_without pgo

Summary:	XZ utils
Name:		xz
Version:	5.2.5
Release:	2
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
Provides:	xz-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}

%description -n %{libdev}
Devel libraries & headers for liblzma.

%package -n %{libstatic}
Summary:	Static libraries for liblzma
Group:		Development/C
Requires:	%{libdev} = %{EVRD}

%description -n %{libstatic}
Static libraries for liblzma.

%if %{with compat32}
%package -n %{lib32name}
Summary:	Libraries for decoding XZ/LZMA compression (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
Libraries for decoding LZMA compression.

%package -n %{dev32name}
Summary:	Devel libraries & headers for liblzma (32-bit)
Group:		Development/C
Requires:	%{lib32name} = %{EVRD}
Requires:	%{libdev} = %{EVRD}

%description -n %{dev32name}
Devel libraries & headers for liblzma.

%package -n %{static32name}
Summary:	Static libraries for liblzma
Group:		Development/C
Requires:	%{dev32name} = %{EVRD}

%description -n %{static32name}
Static libraries for liblzma.
%endif

%prep
%autosetup -p1

%if %{with compat32}
export CONFIGURE_TOP="$(pwd)"
mkdir build32
cd build32
%configure32 \
	--enable-static \
	--disable-xz \
	--disable-xzdec \
	--disable-lzmadec \
	--disable-lzmainfo \
	--enable-assume-ram=1024

%endif

%build
%if %{with compat32}
%make_build -C build32
%endif

export CONFIGURE_TOP="$(pwd)"
mkdir build
cd build
%if %{with pgo}
CFLAGS_PGO="%{optflags} -flto -fprofile-instr-generate"
CXXFLAGS_PGO="%{optflags} -flto -fprofile-instr-generate"
FFLAGS_PGO="$CFLAGS_PGO"
FCFLAGS_PGO="$CFLAGS_PGO"
LDFLAGS_PGO="%{build_ldflags} -flto -fprofile-instr-generate"
export LLVM_PROFILE_FILE="%{name}-%p.profile.d"
export LD_LIBRARY_PATH="$(pwd)"
%configure --enable-static \
%ifarch %{ix86} %{x86_64}
    --enable-assume-ram=1024
%endif

%make_build check CFLAGS="$CFLAGS_PGO" CXXFLAGS="$CXXFLAGS_PGO" LDFLAGS="$LDFLAGS_PGO"

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile $(find . -type f -name "*.profile.d")
make clean

%make_build check CFLAGS="%{optflags} -flto -fprofile-instr-use=$(realpath %{name}.profile)" CXXFLAGS="%{optflags} -flto -fprofile-instr-use=$(realpath %{name}.profile)" LDFLAGS="%{build_ldflags} -flto -fprofile-instr-use=$(realpath %{name}.profile)"
%else
CFLAGS="%{optflags} -flto" CXXFLAGS="%{optflags} -flto" %configure --enable-static \
%ifarch %{ix86} %{x86_64}
    --enable-assume-ram=1024
%endif

%make_build
%endif

%install
%if %{with compat32}
%make_install -C build32
%endif
%make_install -C build

install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

%find_lang %{name}

%check
%if %{with compat32}
make check -C build32
%endif
make check -C build

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/*/man1/*

%files -n %{libname}
%{_libdir}/liblzma.so.%{major}*

%files -n %{libdev}
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/liblzma.so
%{_libdir}/pkgconfig/lib%{lname}.pc

%files -n %{libstatic}
%{_libdir}/liblzma.a

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/liblzma.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/liblzma.so
%{_prefix}/lib/pkgconfig/lib%{lname}.pc

%files -n %{static32name}
%{_prefix}/lib/liblzma.a
%endif
