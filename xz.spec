%define	major	2
%define	lname	lzma
%define libname %mklibname %{lname} %{major}
%define libdev  %mklibname -d %{lname}

Summary: 	LZMA utils
Name: 		xz
Version: 	4.999.9beta
Release: 	%mkrel 1
License: 	GPLv2+
Group:		Archiving/Compression
Source0:	http://tukaani.org/lzma/%{name}-%{version}.tar.xz
Source1:	xzme
Patch0:		xz-4.999.9beta-bump-liblzma-major.patch
Patch1:		xz-4.999.9beta-text-tune.patch
Obsoletes:	lzma <= %{version} lzma-utils <= %{version}
Provides:	lzma = %{version}-%{release} lzma-utils = %{version}-%{release}
BuildRequires:	zlib-devel diffutils
URL:		http://tukaani.org/lzma/
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
LZMA provides very high compression ratio and fast decompression. The
core of the LZMA utils is Igor Pavlov's LZMA SDK containing the actual
LZMA encoder/decoder. LZMA utils add a few scripts which provide
gzip-like command line interface and a couple of other LZMA related
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
Summary:	Libraries for decoding LZMA compression
Group:		System/Libraries
License:	LGPLv2.1+

%description -n	%{libname}
Libraries for decoding LZMA compression.

%package -n	%{libdev}
Summary:	Devel libraries & headers for liblzma
Group:		Development/C
License:	LGPLv2.1+
Provides:	%{lname}-devel = %{version}-%{release}
Provides:	lib%{lname}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}

%description -n %{libdev}
Devel libraries & headers for liblzma.

%prep
%setup -q
%patch0 -p1 -b .bumpmajor~
%patch1 -p1 -b .text_tune~

%build
CFLAGS="%{optflags} -O3 -funroll-loops" \
%configure2_5x
%make

%install
rm -rf %{buildroot}
%makeinstall_std
install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xzme

rm -f %{buildroot}%{_libdir}/*.la
%find_lang %{name}

%check
make check

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc README THANKS
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/lib*.so.%{major}*

%files -n %{libdev}
%defattr(644,root,root,755)
%defattr(-,root,root)
%{_includedir}/%{lname}.h
%dir %{_includedir}/%{lname}
%{_includedir}/%{lname}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/pkgconfig/lib%{lname}.pc

