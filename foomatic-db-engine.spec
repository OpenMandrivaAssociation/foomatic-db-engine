%define version 4.0.8
%define releasedate 0
%if %{releasedate}
%define release 5
%define tarname %{name}-%{version}-%{releasedate}
%else
%define release 5
%define tarname %{name}-%{version}
%endif

%define debug 0

##### GENERAL DEFINITIONS

Name:		foomatic-db-engine
Version:	%{version}
Release:	%{release}
Summary:        Foomatic database access, printer admin, and printing utils
License:        GPLv2
Group:          System/Servers
Url:            http://www.linuxprinting.org/
Requires:       foomatic-filters >= 3.0.2-1.20050816.1mdk perl-base >= 2:5.8.8

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cups
BuildRequires:	perl-devel
BuildRequires:	file
BuildRequires:	libxml2-devel
BuildRequires:	perl-JSON-PP
Source0:		http://www.linuxprinting.org/download/foomatic/%{tarname}.tar.gz
Patch0:			foomatic-db-engine.cat.ppd.patch

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
%setup -q -n %{tarname}
chmod -x *.c

# foomatic-db-engine.cat.ppd.patch
%patch0 -p1

%build

# Change compiler flags for debugging when in debug mode
%if %debug
export DONT_STRIP=1
export CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export RPM_OPT_FLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
%endif


# Makefile generation ("./make_configure" for CVS snapshots)
./make_configure
%configure --libdir=%{_prefix}/lib

# Fix for new library "make install" behaviour of Perl 5.8.1.
perl -p -i -e 's/PREFIX=\$\(DESTDIR\)\$\(PERLPREFIX\)/PREFIX=\$\(PERLPREFIX\)/' Makefile

# Final build of Foomatic package
# Use the real file names of the printing utilities to be independent of the
# update-alternatives configuration

# Do not use "make" macro, as parallelized build of Foomatic does not
# work.

make	LPD_LPR=/usr/bin/lpr-lpd \
        LPD_LPQ=/usr/bin/lpq-lpd \
        LPD_LPRM=/usr/bin/lprm-lpd \
        LPD_LPC=/usr/sbin/lpc-lpd \
        CUPS_LPR=/usr/bin/lpr-cups \
        CUPS_LPQ=/usr/bin/lpq-cups \
        CUPS_LPRM=/usr/bin/lprm-cups \
        CUPS_LPC=/usr/sbin/lpc-cups \
        CUPS_LP=/usr/bin/lp-cups \
        CUPS_CANCEL=/usr/bin/cancel-cups \
        CUPS_LPSTAT=/usr/bin/lpstat-cups \
        PDQ_PRINTRC=/etc/pdq/printrc \
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
make	PREFIX=%{_prefix} \
        DESTDIR=%buildroot \
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
%_bindir/*
%_sbindir/*
%perl_vendorlib/Foomatic
%_datadir/foomatic/templates
%{_mandir}/man*/*
%{_prefix}/lib/cups/driver/*


%changelog
* Sun Aug 14 2011 Oden Eriksson <oeriksson@mandriva.com> 4.0.8-2mdv2011.0
+ Revision: 694543
- bump release
- "fix" build
- 4.0.8

* Tue Aug 09 2011 Alexander Barakin <abarakin@mandriva.org> 4.0.7-2
+ Revision: 693768
- foomatic instead of ppd returns error for many printers
  see https://qa.mandriva.com/show_bug.cgi?id=63882

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 4.0.7-1
+ Revision: 664403
- 4.0.7
- mass rebuild

* Thu Jul 22 2010 Funda Wang <fwang@mandriva.org> 4.0.4-1mdv2011.0
+ Revision: 557027
- rebuild

* Mon Feb 15 2010 Frederik Himpe <fhimpe@mandriva.org> 4.0.4-1mdv2010.1
+ Revision: 506411
- update to new version 4.0.4

* Wed Oct 14 2009 Oden Eriksson <oeriksson@mandriva.com> 4.0.3-1mdv2010.0
+ Revision: 457367
- 4.0.3

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 4.0.1-1mdv2010.0
+ Revision: 424468
- rebuild

* Mon Apr 20 2009 Gustavo De Nardin <gustavodn@mandriva.com> 4.0.1-1mdv2009.1
+ Revision: 368357
- new version 4.0.1, only differs from previous 4.0-20090316 by fixing
  foomatic-compiledb "-d" option

* Mon Mar 16 2009 Frederik Himpe <fhimpe@mandriva.org> 4.0-0.20090316.1mdv2009.1
+ Revision: 355828
- Update to 20090316 snapshot of 4.0 branch (bug fixes)

* Sun Feb 08 2009 Frederik Himpe <fhimpe@mandriva.org> 4.0-0.20090208.1mdv2009.1
+ Revision: 338512
- Update to version 4.0 20090208 snapshot
- rebuild

* Sat Jan 03 2009 Frederik Himpe <fhimpe@mandriva.org> 3.0.2-3.20090103.1mdv2009.1
+ Revision: 323843
- Update to new version 20090103

* Mon Dec 29 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0.2-3.20080810.2mdv2009.1
+ Revision: 321106
- rebuild

* Sun Aug 10 2008 Frederik Himpe <fhimpe@mandriva.org> 3.0.2-3.20080810.1mdv2009.0
+ Revision: 270314
- Update to new version 20080810

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 3.0.2-3.20080518.2mdv2009.0
+ Revision: 264479
- rebuild early 2009.0 package (before pixel changes)

* Sun May 18 2008 Frederik Himpe <fhimpe@mandriva.org> 3.0.2-1.20080518.2mdv2009.0
+ Revision: 208621
- New version
- Adapt to new license policy

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - fix description

* Thu Dec 20 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 3.0.2-1.20071218.2mdv2008.1
+ Revision: 135803
- New upstream: 2070820

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 3.0.2-1.20070820.2mdv2008.1
+ Revision: 125174
- kill re-definition of %%buildroot on Pixel's request

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - rebuild

  + Marcelo Ricardo Leitner <mrl@mandriva.com>
    - New upstream: 2070820

* Thu Jun 28 2007 Adam Williamson <awilliamson@mandriva.org> 3.0.2-1.20070627.1mdv2008.0
+ Revision: 45332
- new snapshot 20070627, spec clean


* Mon Mar 19 2007 Thierry Vignaud <tvignaud@mandriva.com> 3.0.2-1.20060711.2mdv2007.1
+ Revision: 146589
- Import foomatic-db-engine

* Mon Mar 19 2007 Thierry Vignaud <tvignaud@mandriva.com> 3.0.2-1.20060711.2mdv2007.1
- do not package useless big ChangeLog

* Wed Jul 12 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060711.1mdv2007.0
- Updated foomatic-db-engine to the state of the 11/07/2006 (When reading PPD
  files decode the UI strings according to the encoding of the PPD file. This
  way printerdrake displays the option and choice names always correctly,
  thanks to Florian Festi from Red Hat for this patch).

* Tue May 23 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060522.2mdk
- Updated foomatic-db-engine to the state of the 22/05/2006 (Fixed call of 
  CUPS commands "enable", "disable", "accept", "reject").

* Tue May 23 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060522.1mdk
- Updated foomatic-db-engine to the state of the 22/05/2006 (When generating
  PPD files from Foomatic XML data and the option XML files contain
  "<arg_order>" tags with different values, the options get ordered by the 
  "<arg_order>" values within their group).

* Sat May 20 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060519.1mdk
- Updated foomatic-db-engine to the state of the 19/05/2006 (Let PPD file
  generation with cups-driverd also work if the driver name contains dashes,
  as in Gutenprint).

* Wed May 03 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060422.2mdk
- Added "BuildRequires: cups" to assure that CUPS PPD generator
  (/usr/lib/cups/driver/foomatic) gets installed.

* Sun Apr 23 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060422.1mdk
- Updated foomatic-db-engine to the state of the 22/04/2006 (Let more
  info be queried from /etc/cups/printers.conf, especially setting for
  sharing the print queues and for the error policy).

* Sat Apr 22 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060421.1mdk
- Updated foomatic-db-engine to the state of the 21/04/2006 (Eliminated
  some warnings, let foomatic-configure not set up an HPLIP fax queue
  with the beh backend wrapper).

* Fri Apr 21 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060420.2mdk
- Moved CUPS binary directory from /usr/lib64/cups to /usr/lib/cups on 
  64-bit systems.

* Tue Feb 28 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060420.1mdk
- Updated foomatic-db-engine to the state of the 20/04/2006 (Support
  on-the-fly building of PPDs with the cups-driverd of CUPS 1.2, so all
  Foomatic PPDs get visible in the web interface without pre-building 
  them).

* Tue Feb 28 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060228.1mdk
- Updated foomatic-db-engine to the state of the 28/02/2006 (Treat a 
  missing /etc/cups/printers.conf as an empty file because CUPS 1.2 allows 
  printers.conf missing in case of no local printers. Suppress warnings if 
  the list of available CUPS queues is requested but no default printer
  set).

* Fri Feb 17 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060217.1mdk
- Updated foomatic-db-engine to the state of the 17/02/2006 (Do not try 
  to delete the "." file in the driver-XML-file directory; Generate PPD 
  files correctly where an enumerated-choice option has "0" as default;
  thanks to Tim Waugh from Red Hat for these fixes).

* Mon Jan 09 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060109.2mdk
- Updated foomatic-db-engine to the state of the 09/01/2006 (Let PPD files 
  with "*CloseGroup" without group name being parsed correctly, eliminate
  warning about uninitialized variable when a PPD file is built out of
  Foomatic data).
- Updated perl-base dependency version number.

* Mon Jan 09 2006 Till Kamppeter <till@mandriva.com> 3.0.2-1.20060109.1mdk
- Updated foomatic-db-engine to the state of the 09/01/2006 (Fixed
  foomatic-cleandb to really remove all driver XML files without command
  line prototype, updated to work with current aclocal and autoconf).
- Introduced %%mkrel.
- Rebuilt for CUPS 1.2.

* Thu Oct 27 2005 Till Kamppeter <till@mandriva.com> 3.0.2-1.20051027.1mdk
- Updated foomatic-db-engine to the state of the 27/10/2005
  (foomatic-configure, foomatic-ppdfile, and foomatic-compiledb use ready-
  made PPD files if they are available in foomatic-db).

* Wed Aug 24 2005 Till Kamppeter <till@mandriva.com> 3.0.2-1.20050823.1mdk
- Updated foomatic-db-engine to the state of the 23/08/2005 (Output of
  "foomatic-configure -O" now also contains the links to the available
  ready-made PPDs).

* Tue Aug 16 2005 Till Kamppeter <till@mandriva.com> 3.0.2-1.20050816.1mdk
- Updated foomatic-db-engine to the state of the 16/08/2005 (Support for
  the new "beh" CUPS backend in foomatic-filters).

* Wed Aug 03 2005 Till Kamppeter <till@mandriva.com> 3.0.2-1.20050802.1mdk
- Updated foomatic-db-engine to the state of the 02/08/2005 (Fixed Adobe
  link in README file).

* Mon May 30 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050530.1mdk
- Updated foomatic-db-engine to the state of the 30/05/2005 (Added support
  for PPD file names with spaces, bug 16172).

* Fri May 20 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 3.0.2-1.20050224.5mdk
- Don't require a specific version of perl-base, to make upgrades possible

* Wed Feb 23 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050224.4mdk
- Rebuild as previous build was messed up.

* Wed Feb 23 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050224.3mdk
- Updated foomatic-db-engine to the state of the 28/01/2005 (Bug fixes on
  modifying print queues with non-Foomatic PPD files).

* Tue Feb 01 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050128.3mdk
- Added versioned requirement of perl-base.

* Fri Jan 28 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050128.2mdk
- Let previous build directory be deleted when building this RPM.
- Include "foomatic-cleanupdrivers".

* Fri Jan 28 2005 Till Kamppeter <till@mandrakesoft.com> 3.0.2-1.20050128.1mdk
- Updated foomatic-db-engine to the state of the 28/01/2005.

