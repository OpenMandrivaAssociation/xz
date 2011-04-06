%define	major	5
%define	lname	lzma
%define libname %mklibname %{lname} %{major}
%define libdev  %mklibname -d %{lname}

Summary: 	XZ utils
Name: 		xz
Version: 	5.0.2
Release: 	1
License: 	Public Domain
Group:		Archiving/Compression
Source0:	http://tukaani.org/lzma/%{name}-%{version}.tar.xz
Source1:	xzme
Patch0:		xz-5.0.0-text-tune.patch
Patch1:		xz-5.0.2-fix-leak.patch
Patch2:		xz-5.0.2-open-missing-mode.patch
%rename		lzma
%rename		lzma-utils
# needed by check suite
BuildRequires:	diffutils
URL:		http://tukaani.org/xz/

%description
XZ provides very high compression ratio and fast decompression. The
core of the XZ utils is Igor Pavlov's LZMA SDK containing the actual
LZMA encoder/decoder. LZMA utils add a few scripts which provide
gzip-like command line interface and a couple of other XZ related
tools. Also provides:

- Average compression ratio 30% better than that of gzip and 15%
  better than that of bzip2.

- Decompression speed is only little slower than that of gzip, being
  two to five times faster than bzip2.

- In fast mode, compresses faster than bzip2 with a comparable
  compression ratio.

- Achieving the best compression ratios takes four to even twelve
  times longer than with bzip2. However. this doesn't affect
  decompressing speed.

- Very similar command line interface than what gzip and bzip2 have.

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
%setup -q
%patch0 -p1 -b .text~
%patch1 -p1 -b .leak~
%patch2 -p1 -b .mode~

%build
CFLAGS="%{optflags} -O3 -funroll-loops" \
%configure2_5x
%make

%install
%makeinstall_std
install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

rm -f %{buildroot}%{_libdir}/*.la
%find_lang %{name}

%check
make check

%files -f %{name}.lang
%doc README THANKS
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/lib*.so.%{major}*

%files -n %{libdev}
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/pkgconfig/lib%{lname}.pc
