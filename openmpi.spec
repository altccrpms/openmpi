# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%define opt_cc gcc
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use
#define opt_cflags
%define opt_cxx g++
#define opt_cxxflags
%define opt_f77 gfortran
#define opt_fflags
%define opt_fc gfortran
#define opt_fcflags

# Optional name suffix to use...we leave it off when compiling with gcc, but
# for other compiled versions to install side by side, it will need a
# suffix in order to keep the names from conflicting.
#define cc_name_suffix -gcc

Name:			openmpi%{?cc_name_suffix}
Version:		1.3.3
Release:		2%{?dist}
Summary:		Open Message Passing Interface
Group:			Development/Libraries
License:		BSD
URL:			http://www.open-mpi.org/
Source0:		http://www.open-mpi.org/software/ompi/v1.3/downloads/%{name}-%{version}.tar.bz2
Source1:		openmpi.pc.in
Source2:		openmpi.module.in
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:		gcc-gfortran, libtool, numactl-devel, valgrind-devel
BuildRequires:		libibverbs-devel, opensm-devel > 3.3.0
#%ifnarch ppc
#BuildRequires:		compat-dapl-devel
#%endif
Provides:		mpi
Requires:		environment-modules
Obsoletes:		openmpi-libs

%description
Open MPI is an open source, freely available implementation of both the 
MPI-1 and MPI-2 standards, combining technologies and resources from
several other projects (FT-MPI, LA-MPI, LAM/MPI, and PACX-MPI) in
order to build the best MPI library available.  A completely new MPI-2
compliant implementation, Open MPI offers advantages for system and
software vendors, application developers, and computer science
researchers. For more information, see http://www.open-mpi.org/ .

%package devel
Summary:        Development files for openmpi
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}, gcc-gfortran
Provides:	mpi-devel

%description devel
Contains development headers and libraries for openmpi

# When dealing with multilib installations, aka the ability to run either
# i386 or x86_64 binaries on x86_64 machines, we install the native i386
# openmpi libs/compilers and the native x86_64 libs/compilers.  Obviously,
# on i386 you can only run i386, so you don't really need the -m32 flag
# to gcc in order to force 32 bit mode.  However, since we use the native
# i386 package to support i386 operation on x86_64, and since on x86_64
# the default is x86_64, the i386 package needs to force i386 mode.  This
# is true of all the multilib arches, hence the non-default arch (aka i386
# on x86_64) must force the non-default mode (aka 32 bit compile) in it's
# native-arch package (aka, when built on i386) so that it will work
# properly on the non-native arch as a multilib package (aka i386 installed
# on x86_64).  Just to be safe, we also force the default mode (aka 64 bit)
# in default arch packages (aka, the x86_64 package).  There are, however,
# some arches that don't support forcing *any* mode, those we just leave
# undefined.
%ifarch %{ix86} ppc sparcv9
%define mode 32
%define modeflag -m32
%endif
%ifarch ia64
%define mode 64
%endif
%ifarch x86_64 ppc64 sparc64
%define mode 64
%define modeflag -m64
%endif

# We set this to for convenience, since this is the unique dir we use for this
# particular package, version, compiler
%define mpidir %{name}/%{version}-%{opt_cc}

%prep
%setup -q
%ifarch x86_64
XFLAGS="-fPIC"
%endif

./configure --prefix=%{_libdir}/%{mpidir} --with-libnuma=/usr \
	--with-openib=/usr --enable-mpirun-prefix-by-default \
	--mandir=%{_libdir}/%{mpidir}/man --enable-mpi-threads \
	--with-ft=cr --with-valgrind \
	--with-wrapper-cflags="%{?opt_cflags} %{?modeflag}" \
	--with-wrapper-cxxflags="%{?opt_cxxflags} %{?modeflag}" \
	--with-wrapper-fflags="%{?opt_fflags} %{?modeflag}" \
	--with-wrapper-fcflags="%{?opt_fcflags} %{?modeflag}" \
	CC=%{opt_cc} CXX=%{opt_cxx} \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="%{?opt_cflags} $RPM_OPT_FLAGS $XFLAGS" \
	CXXFLAGS="%{?opt_cxxflags} $RPM_OPT_FLAGS $XFLAGS" \
	FC=%{opt_fc} FCFLAGS="%{?opt_fcflags} $RPM_OPT_FLAGS $XFLAGS" \
	F77=%{opt_f77} FFLAGS="%{?opt_fflags} $RPM_OPT_FLAGS $XFLAGS"

%build
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
find %{buildroot}%{_libdir}/%{mpidir}/lib -name \*.la | xargs rm
find %{buildroot}%{_libdir}/%{mpidir}/man -type f | xargs gzip -9
ln -s mpicc.1.gz %{buildroot}%{_libdir}/%{mpidir}/man/man1/mpiCC.1.gz
rm -f %{buildroot}%{_libdir}/%{mpidir}/man/man1/mpiCC.1
rm -f %{buildroot}%{_libdir}/%{mpidir}/share/vampirtrace/doc/opari/lacsi01.ps.gz

# Make the pkgconfig file
mkdir -p %{buildroot}%{_libdir}/pkgconfig
sed 's#@NAME@#'%{name}'#g;s#@VERSION@#'%{version}'#g;s#@LIBDIR@#'%{_libdir}'#g;s#@CC@#'%{opt_cc}'#g;s#@MPIDIR@#'%{mpidir}'#g;s#@MODEFLAG@#'%{?modeflag}'#g' < %SOURCE1 > %{buildroot}/%{_libdir}/pkgconfig/%{name}%{?cc_name_suffix}.pc
# Make the environment-modules file
mkdir -p %{buildroot}%{_datadir}/Modules/modulefiles
sed 's#@LIBDIR@#'%{_libdir}'#g;s#@MPIDIR@#'%{mpidir}'#g;s#@MODEFLAG@#'%{?modeflag}'#g' < %SOURCE2 > %{buildroot}/%{_datadir}/Modules/modulefiles/%{name}-%{_arch}%{?cc_name_suffix}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{mpidir}
%dir %{_libdir}/%{mpidir}/etc
%dir %{_libdir}/%{mpidir}/bin
%dir %{_libdir}/%{mpidir}/lib
%dir %{_libdir}/%{mpidir}/lib/openmpi
%dir %{_libdir}/%{mpidir}/man
%dir %{_libdir}/%{mpidir}/man/man1
%dir %{_libdir}/%{mpidir}/man/man7
%dir %{_libdir}/%{mpidir}/share
%dir %{_libdir}/%{mpidir}/share/openmpi
%config(noreplace) %{_libdir}/%{mpidir}/etc/*
%{_libdir}/%{mpidir}/bin/mpi[er]*
%{_libdir}/%{mpidir}/bin/ompi*
%{_libdir}/%{mpidir}/bin/opal-*
%{_libdir}/%{mpidir}/bin/opari
%{_libdir}/%{mpidir}/bin/orte*
%{_libdir}/%{mpidir}/bin/otf*
%{_libdir}/%{mpidir}/lib/openmpi/*
%{_libdir}/%{mpidir}/lib/*.so.*
%{_libdir}/%{mpidir}/man/man1/mpi[er]*
%{_libdir}/%{mpidir}/man/man1/ompi*
%{_libdir}/%{mpidir}/man/man1/opal-*
%{_libdir}/%{mpidir}/man/man1/orte*
%{_libdir}/%{mpidir}/man/man7/ompi*
%{_libdir}/%{mpidir}/man/man7/orte*
%{_libdir}/%{mpidir}/share/openmpi/doc
%{_libdir}/%{mpidir}/share/openmpi/amca-param-sets
%{_libdir}/%{mpidir}/share/openmpi/help*
%{_libdir}/%{mpidir}/share/openmpi/mca*
%{_datadir}/Modules/modulefiles/*

%files devel
%defattr(-,root,root,-)
%dir %{_libdir}/%{mpidir}/include
%dir %{_libdir}/%{mpidir}/man/man3
%dir %{_libdir}/%{mpidir}/share/vampirtrace
%{_libdir}/pkgconfig/%{name}%{?cc_name_suffix}.pc
%{_libdir}/%{mpidir}/bin/mpi[cCf]*
%{_libdir}/%{mpidir}/bin/vt*
%{_libdir}/%{mpidir}/bin/opal_*
%{_libdir}/%{mpidir}/include/*
%{_libdir}/%{mpidir}/lib/*.so
%{_libdir}/%{mpidir}/lib/lib*.a
%{_libdir}/%{mpidir}/lib/mpi.mod
%{_libdir}/%{mpidir}/man/man1/mpi[cCf]*
%{_libdir}/%{mpidir}/man/man1/opal_*
%{_libdir}/%{mpidir}/man/man3/*
%{_libdir}/%{mpidir}/man/man7/opal*
%{_libdir}/%{mpidir}/share/openmpi/mpi*
%{_libdir}/%{mpidir}/share/vampirtrace/*

%changelog
* Tue Jul 21 2009 Doug Ledford <dledford@redhat.com> - 1.3.3-2
- Add MPI_BIN and MPI_LIB to the modules file (related bz511099)

* Tue Jul 21 2009 Doug Ledford <dledford@redhat.com> - 1.3.3-1
- Make sure all created dirs are owned (bz474677)
- Fix loading of pkgconfig file (bz476844)
- Resolve file conflict between us and libotf (bz496131)
- Resolve dangling symlinks issue (bz496909)
- Resolve unexpanded %%{mode} issues (bz496911)
- Restore -devel subpackage (bz499851)
- Make getting the default openmpi devel environment easier (bz504357)
- Make the -devel package pull in the base package (bz459458)
- Make it easier to use alternative compilers to build package (bz246484)

* Sat Jul 18 2009 Jussi Lehtola <jussilehtola@fedoraproject.org> - 1.3.1-4
- Add Provides: openmpi-devel to fix other package builds in rawhide.

* Fri May 08 2009 Lubomir Rintel <lkundrak@v3.sk> - 1.3.1-3
- Treat i586 the same way as i386

* Wed Apr 22 2009 Doug Ledford <dledford@redhat.com> - 1.3.1-2
- fixed broken update
- Resolves: bz496909, bz496131, bz496911

* Tue Apr 14 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 1.3.1-1
- update to 1.3.1, cleanup alternatives, spec, make new vt subpackage

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.2.4-2
- Autorebuild for GCC 4.3

* Wed Oct 17 2007 Doug Ledford <dledford@redhat.com> - 1.2.4-1
- Update to 1.2.4 upstream version
- Build against libtorque
- Pass a valid mode to open
- Resolves: bz189441, bz265141

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.2.3-5
- Rebuild for selinux ppc32 issue.

* Mon Jul 16 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-4
- Fix a directory permission problem on the base openmpi directories

* Thu Jul 12 2007 Florian La Roche <laroche@redhat.com> - 1.2.3-3
- requires alternatives for various sub-rpms

* Mon Jul 02 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-2
- Fix dangling symlink issue caused by a bad macro usage
- Resolves: bz246450

* Wed Jun 27 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-1
- Update to latest upstream version
- Fix file ownership on -libs package
- Take a swing at solving the multi-install compatibility issues

* Mon Feb 19 2007 Doug Ledford <dledford@redhat.com> - 1.1.1-7
- Bump version to be at least as high as the RHEL4U5 openmpi
- Integrate fixes made in RHEL4 openmpi into RHEL5 (fix a multilib conflict
  for the openmpi.module file by moving from _datadir to _libdir, make sure
  all sed replacements have the g flag so they replace all instances of
  the marker per line, not just the first, and add a %%defattr tag to the
  files section of the -libs package to avoid install errors about
  brewbuilder not being a user or group)
- Resolves: bz229298

* Wed Jan 17 2007 Doug Ledford <dledford@redhat.com> - 1.1.1-5
- Remove the FORTIFY_SOURCE and stack protect options
- Related: bz213075

* Fri Oct 20 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-4
- Bump and build against the final openib-1.1 package

* Wed Oct 18 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-3
- Fix an snprintf length bug in opal/util/cmd_line.c
- RESOLVES: rhbz#210714

* Wed Oct 18 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-2
- Bump and build against openib-1.1-0.pre1.1 instead of 1.0

* Tue Oct 17 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-1
- Update to upstream 1.1.1 version

* Fri Oct 13 2006 Doug Ledford <dledford@redhat.com> - 1.1-7
- ia64 can't take -m64 on the gcc command line, so don't set it there

* Wed Oct 11 2006 Doug Ledford <dledford@redhat.com> - 1.1-6
- Bump rev to match fc6 rev
- Fixup some issue with alternatives support
- Split the 32bit and 64bit libs ld.so.conf.d files into two files so
  multilib or single lib installs both work properly
- Put libs into their own package
- Add symlinks to /usr/share/openmpi/bin%%{mode} so that opal_wrapper-%%{mode}
  can be called even if it isn't the currently selected default method in
  the alternatives setup (opal_wrapper needs to be called by mpicc, mpic++,
  etc. in order to determine compile mode from argv[0]).

* Sun Aug 27 2006 Doug Ledford <dledford@redhat.com> - 1.1-4
- Make sure the post/preun scripts only add/remove alternatives on initial
  install and final removal, otherwise don't touch.

* Fri Aug 25 2006 Doug Ledford <dledford@redhat.com> - 1.1-3
- Don't ghost the mpi.conf file as that means it will get removed when
  you remove 1 out of a number of alternatives based packages
- Put the .mod file in -devel

* Mon Aug  7 2006 Doug Ledford <dledford@redhat.com> - 1.1-2
- Various lint cleanups
- Switch to using the standard alternatives mechanism instead of a home
  grown one

* Wed Aug  2 2006 Doug Ledford <dledford@redhat.com> - 1.1-1
- Upgrade to 1.1
- Build with Infiniband support via openib

* Mon Jun 12 2006 Jason Vas Dias <jvdias@redhat.com> - 1.0.2-1
- Upgrade to 1.0.2

* Wed Feb 15 2006 Jason Vas Dias <jvdias@redhat.com> - 1.0.1-1
- Import into Fedora Core
- Resolve LAM clashes 

* Wed Jan 25 2006 Orion Poplawski <orion@cora.nwra.com> - 1.0.1-2
- Use configure options to install includes and libraries
- Add ld.so.conf.d file to find libraries
- Add -fPIC for x86_64

* Tue Jan 24 2006 Orion Poplawski <orion@cora.nwra.com> - 1.0.1-1
- 1.0.1
- Use alternatives

* Sat Nov 19 2005 Ed Hill <ed@eh3.com> - 1.0-2
- fix lam conflicts

* Fri Nov 18 2005 Ed Hill <ed@eh3.com> - 1.0-1
- initial specfile created

