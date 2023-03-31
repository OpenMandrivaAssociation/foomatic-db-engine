%define debug 0

Name:		foomatic-db-engine
Version:	4.0.13
Release:	7
Summary:        Foomatic database access, printer admin, and printing utils
License:        GPLv2
Group:          System/Servers
Url:            http://www.openprinting.org
Source0:	http://www.openprinting.org/download/foomatic/%{name}-%{version}.tar.gz
#Patch0:		foomatic-db-engine.cat.ppd.patch

BuildRequires:	cups
BuildRequires:	file
BuildRequires:	perl-JSON-PP
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(liblzma)
Requires:       foomatic-filters
Requires(post,preun):       rpm-helper

%description
Foomatic is a comprehensive, spooler-independent database of printers,
printer drivers, and driver descriptions. It contains utilities to
generate PPD (Postscript Printer Description) files and printer queues
for CUPS, LPD, GNUlpr, LPRng, PPR, and PDQ using the database. There
is also the possibility to read the PJL options out of PJL-capable
laser printers and take them into account at the driver description
file generation.

There are spooler-independent command line interfaces to manipulate
queues (foomatic-configure) and to print files/manipulate jobs
(foomatic printjob).
 
This package contains the tools for accessing the Foomatic database,
for printer administration, and for printing.

%prep
# Source trees for installation
%setup -q
%autopatch -p1
chmod -x *.c

%build
#cland doesn't work with the current configure
CC=gcc
CXX=g++
# Change compiler flags for debugging when in debug mode
%if %debug
export DONT_STRIP=1
export CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export RPM_OPT_FLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
%endif

# Makefile generation ("./make_configure" for CVS snapshots)
./make_configure
%configure \
	--libdir=%{_prefix}/lib

# Fix for new library "make install" behaviour of Perl 5.8.1.
sed  -i -e 's/PREFIX=\$\(DESTDIR\)\$\(PERLPREFIX\)/PREFIX=\$\(PERLPREFIX\)/' Makefile

# Final build of Foomatic package
# Use the real file names of the printing utilities to be independent of the
# update-alternatives configuration

# Do not use "make" macro, as parallelized build of Foomatic does not
# work.

make \
	LPD_LPR=%{_bindir}/lpr-lpd \
        LPD_LPQ=%{_bindir}/lpq-lpd \
        LPD_LPRM=%{_bindir}/lprm-lpd \
        LPD_LPC=%{_bindir}/lpc-lpd \
        CUPS_LPR=%{_bindir}/lpr-cups \
        CUPS_LPQ=%{_bindir}/lpq-cups \
        CUPS_LPRM=%{_bindir}/lprm-cups \
        CUPS_LPC=%{_bindir}/lpc-cups \
        CUPS_LP=%{_bindir}/lp-cups \
        CUPS_CANCEL=%{_bindir}/cancel-cups \
        CUPS_LPSTAT=%{_bindir}/lpstat-cups \
        PDQ_PRINTRC=%{_sysconfdir}/pdq/printrc \
        PREFIX=%{_prefix} \
        PERL_INSTALLDIRS=vendor \
        DESTDIR=%{buildroot}

chmod a+rx mkinstalldirs

%install
# Change compiler flags for debugging when in debug mode
%if %debug
export DONT_STRIP=1
export CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export RPM_OPT_FLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
%endif

# Make directories
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libdir}
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_mandir}/man8

# Install program files
eval `perl '-V:installsitelib'`
mkdir -p %{buildroot}/$installsitelib
export INSTALLSITELIB=%{buildroot}/$installsitelib
make \
	PREFIX=%{_prefix} \
        DESTDIR=%{buildroot} \
        INSTALLSITELIB=%{buildroot}/$installsitelib \
        install

# Use update-alternatives to make "foomatic-printjob" also possible through
# the usual printing commands
 
( cd %{buildroot}%{_bindir}
  ln -s foomatic-printjob lpr-foomatic
  ln -s foomatic-printjob lpq-foomatic
  ln -s foomatic-printjob lprm-foomatic
)
( cd %{buildroot}%{_sbindir}
  ln -s %{_bindir}/foomatic-printjob lpc-foomatic
)

# Correct permissions
chmod -R a-X %{buildroot}%{perl_vendorlib}/Foomatic/*.pm

%post -n foomatic-db-engine
# Set up update-alternatives entries
%{_sbindir}/update-alternatives --install %{_bindir}/lpr lpr %{_bindir}/lpr-foomatic 1
%{_sbindir}/update-alternatives --install %{_bindir}/lpq lpq %{_bindir}/lpq-foomatic 1
%{_sbindir}/update-alternatives --install %{_bindir}/lprm lprm %{_bindir}/lprm-foomatic 1
%{_sbindir}/update-alternatives --install %{_sbindir}/lpc lpc %{_sbindir}/lpc-foomatic 1

%preun -n foomatic-db-engine
if [ "$1" -eq "0" ]; then
  # On removal
  # Remove update-alternatives entries
  %{_sbindir}/update-alternatives --remove lpr /usr/bin/lpr-foomatic
  %{_sbindir}/update-alternatives --remove lpq /usr/bin/lpq-foomatic
  %{_sbindir}/update-alternatives --remove lprm /usr/bin/lprm-foomatic
  %{_sbindir}/update-alternatives --remove lpc /usr/sbin/lpc-foomatic
fi

%files
%doc README TODO USAGE Foomatic-Devel-Ideas.txt ChangeLog
%{_bindir}/*
%if "%{_bindir}" != "%{_sbindir}"
%{_sbindir}/*
%endif
%{perl_vendorlib}/Foomatic
%{_datadir}/foomatic/templates
%{_mandir}/man*/*
%{_prefix}/lib/cups/driver/*
