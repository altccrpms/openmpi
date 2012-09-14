# AltCCRPMS
%global shortname openmpi

%global _cc_name intel
%global _cc_name_suffix -%{_cc_name}

%global _prefix /opt/%{shortname}-%{_cc_name}/%{version}
%global _sysconfdir %{_prefix}/etc
%global _defaultdocdir %{_prefix}/share/doc
%global _infodir %{_prefix}/share/info
%global _mandir %{_prefix}/share/man

#We don't want to be beholden to the proprietary libraries
%global    _use_internal_dependency_generator 0
%global    __find_requires %{nil}

# Non gcc compilers don't generate build ids
%undefine _missing_build_ids_terminate_build

%global intel_flags -O3 -axSSE2,SSE4.1,SSE4.2

# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%global opt_cc icc
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use
%global opt_cflags %{intel_flags}
%global opt_cxx icpc
%global opt_cxxflags %{intel_flags}
%global opt_f77 ifort
%global opt_fflags %{intel_flags}
%global opt_fc ifort
%global opt_fcflags %{intel_flags}

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
# Optional name suffix to use...we leave it off when compiling with gcc, but
# for other compiled versions to install side by side, it will need a
# suffix in order to keep the names from conflicting.
#global _cc_name_suffix -gcc

Name:			openmpi161%{?_cc_name_suffix}
Version:		1.6.1
Release:		2%{?dist}
Summary:		Open Message Passing Interface
Group:			Development/Libraries
License:		BSD, MIT and Romio
URL:			http://www.open-mpi.org/

# We can't use %{name} here because of _cc_name_suffix
#Source0:		http://www.open-mpi.org/software/ompi/v1.6/downloads/openmpi-%{version}.tar.bz2
# openmpi-%{version}-clean.tar.xz was generated by taking the upstream tarball
# and removing license-incompatible files:
# rm -r opal/mca/backtrace/darwin/MoreBacktrace
Source0:		openmpi-%{version}-clean.tar.xz
Source1:		openmpi.module.in
Source2:		macros.openmpi
# Patch to handle removed items
Patch0:			openmpi-removed.patch

#sparc 64 doesn't have valgrind
%ifnarch %{sparc}
BuildRequires:		valgrind-devel
%endif
BuildRequires:		libibverbs-devel >= 1.1.3, opensm-devel > 3.3.0
BuildRequires:		librdmacm-devel libibcm-devel
%if 0%{?fedora}
BuildRequires:		hwloc-devel
%endif
BuildRequires:		python libtool-ltdl-devel
BuildRequires:		libesmtp-devel

Provides:		mpi
Requires:		environment-modules

# AltCCRPMS
Provides:       %{shortname}%{?_cc_name_suffix} = %{version}-%{release}
Provides:       %{shortname}%{?_cc_name_suffix}%{?_isa} = %{version}-%{release}

# s390 is unlikely to have the hardware we want, and some of the -devel
# packages we require aren't available there.
ExcludeArch: s390 s390x

# Private openmpi libraries
%global __provides_exclude_from %{_libdir}/openmpi/lib/(lib(mca|o|v)|openmpi/).*.so
%global __requires_exclude lib(mca|o|v).*

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
Requires:       %{name} = %{version}-%{release}
Provides:	mpi-devel
# AltCCRPMS
Provides:       %{shortname}%{?_cc_name_suffix}-devel = %{version}-%{release}
Provides:       %{shortname}%{?_cc_name_suffix}-devel%{?_isa} = %{version}-%{release}

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
%global mode 32
%global modeflag -m32
%endif
%ifarch ia64
%global mode 64
%endif
%ifarch x86_64 ppc64 sparc64
%global mode 64
%global modeflag -m64
%endif

# We set this to for convenience, since this is the unique dir we use for this
# particular package, version, compiler
%global namearch openmpi%{?_cc_name_suffix}

%prep
%setup -q -n openmpi-%{version}
%patch0 -p1 -b .removed
# Make sure we don't use the local libltdl library
rm -r opal/libltdl

%build
./configure --prefix=%{_prefix} \
	--libdir=%{_prefix}/%{_lib} \
	--with-openib=/usr \
	--with-sge \
%ifnarch %{sparc}
	--with-valgrind \
	--enable-memchecker \
%endif
	--with-esmtp \
%if 0%{?fedora}
	--with-hwloc=/usr \
%endif
	--with-libltdl=/usr \
	--with-wrapper-cflags="%{?modeflag}" \
	--with-wrapper-cxxflags="%{?modeflag}" \
	--with-wrapper-fflags="%{?modeflag}" \
	--with-wrapper-fcflags="%{?modeflag}" \
	CC=%{opt_cc} CXX=%{opt_cxx} \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="%{?opt_cflags} %{!?opt_cflags:$RPM_OPT_FLAGS}" \
	CXXFLAGS="%{?opt_cxxflags} %{!?opt_cxxflags:$RPM_OPT_FLAGS}" \
	FC=%{opt_fc} FCFLAGS="%{?opt_fcflags} %{!?opt_fcflags:$RPM_OPT_FLAGS}" \
	F77=%{opt_f77} FFLAGS="%{?opt_fflags} %{!?opt_fflags:$RPM_OPT_FLAGS}"
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
rm -fr %{buildroot}%{_libdir}/pkgconfig
find %{buildroot}%{_libdir} -name \*.la | xargs rm
find %{buildroot}%{_mandir} -type f | xargs gzip -9
ln -s mpicc.1.gz %{buildroot}%{_mandir}/man1/mpiCC.1.gz
rm -f %{buildroot}%{_mandir}/man1/mpiCC.1
rm -f %{buildroot}%{_mandir}/man1/orteCC.1*
rm -f %{buildroot}%{_libdir}/%{name}/share/vampirtrace/doc/opari/lacsi01.ps.gz
mkdir %{buildroot}%{_mandir}/man{2,4,5,6,8,9,n}

# Make the environment-modules file
mkdir -p %{buildroot}/etc/modulefiles/mpi/openmpi%{?_cc_name_suffix}/%{version}
# Since we're doing our own substitution here, use our own definitions.
sed 's#@PREFIX@#%{_prefix}#;s#@LIBDIR@#%{_libdir}#g;s#@ETCDIR@#%{_sysconfdir}#g;s#@FMODDIR@#%{_libdir}#g;s#@INCDIR@#%{_includedir}#g;s#@MANDIR@#%{_mandir}#g;s#@PYSITEARCH@#%{python_sitearch}/%{name}#g;s#@COMPILER@#openmpi%{?_cc_name_suffix}#g' < %SOURCE1 > %{buildroot}/etc/modulefiles/mpi/openmpi%{_cc_name_suffix}/%{version}/%{_arch}
# make the rpm config file
mkdir -p %{buildroot}/%{_sysconfdir}/rpm
cp %SOURCE2 %{buildroot}/%{_sysconfdir}/rpm/macros.%{namearch}
mkdir -p %{buildroot}/%{python_sitearch}/%{name}
# Remove extraneous wrapper link libraries (bug 814798)
sed -i -e s/-ldl// -e s/-lhwloc// \
  %{buildroot}%{_bindir}/orte_wrapper_script \
  %{buildroot}%{_datadir}/openmpi/*-wrapper-data.txt


%files
%defattr(-,root,root,-)
%dir %{_libdir}
%dir %{_sysconfdir}
%dir %{_libdir}/openmpi
%dir %{_mandir}
%dir %{_mandir}/man*
%dir %{python_sitearch}/%{name}
%config(noreplace) %{_sysconfdir}/*
%{_bindir}/mpi[er]*
%{_bindir}/ompi*
#%{_bindir}/opal-*
%{_bindir}/opari
%{_bindir}/orte*
%{_bindir}/otf*
%{_libdir}/*.so.*
%{_mandir}/man1/mpi[er]*
%{_mandir}/man1/ompi*
#%{_mandir}/man1/opal-*
%{_mandir}/man1/orte*
%{_mandir}/man7/ompi*
%{_mandir}/man7/orte*
%{_libdir}/openmpi/*
/etc/modulefiles/mpi
#%files common
%dir %{_datadir}/openmpi
%dir %{_libdir}/openmpi
%{_datadir}/openmpi/doc
%{_datadir}/openmpi/amca-param-sets
%{_datadir}/openmpi/help*.txt
%{_datadir}/openmpi/mca-btl-openib-device-params.ini

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}
%dir %{_datadir}/vampirtrace
%{_bindir}/mpi[cCf]*
%{_bindir}/vt*
%{_bindir}/opal_*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/lib*.a
%{_libdir}/mpi.mod
%{_mandir}/man1/mpi[cCf]*
%{_mandir}/man1/opal_*
%{_mandir}/man3/*
%{_mandir}/man7/opal*
%{_datadir}/openmpi/openmpi-valgrind.supp
%{_datadir}/openmpi/mpi*.txt
%{_datadir}/openmpi/orte*.txt
%{_datadir}/vampirtrace/*
%{_sysconfdir}/rpm/macros.%{namearch}

%changelog
* Thu Sep 13 2012 Orion Poplawski <orion@cora.nwra.com> 1.6.1-2
- Drop adding -fPIC, no longer needed
- Set --disable-silent-rules for more verbose build logs
- Don't add opt_*flags to the wrappers
- Only use $RPM_OPT_FLAGS if not using the opt_*flags

* Thu Aug 23 2012 Orion Poplawski <orion@cora.nwra.com> 1.6.1-1
- Update to 1.6.1
- Drop hostfile patch applied upstream

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 15 2012 Orion Poplawski <orion@cora.nwra.com> 1.6-2
- Add patch from upstream to fix default hostfile location

* Tue May 15 2012 Orion Poplawski <orion@cora.nwra.com> 1.6-1
- Update to 1.6
- Drop arm patch, appears to be addressed upstream
- Remove extraneous wrapper link libraries (bug 814798)

* Tue Apr  3 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.5.5-1
- Update to 1.5.5

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.4-5.1
- Rebuilt for c++ ABI breakage

* Wed Feb 22 2012 Orion Poplawski <orion@cora.nwra.com> 1.5.4-4.1
- Rebuild with hwloc 1.4

* Wed Feb 15 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.5.4-4
- Rebuild for hwloc soname bump

* Fri Jan 20 2012 Doug Ledford <dledford@redhat.com> - 1.5.4-3
- Move modules file to mpi directory and make it conflict with any other
  mpi module (bug #651074)

* Sun Jan 8 2012 Orion Poplawski <orion@cora.nwra.com> 1.5.4-2
- Rebuild with gcc 4.7 (bug #772443)

* Thu Nov 17 2011 Orion Poplawski <orion@cora.nwra.com> 1.5.4-1
- Update to 1.5.4
- Drop dt-textrel patch fixed upstream
- Fixup handling removed files (bug #722534)
- Uses hwloc instead of plpa
- Exclude private libraries from provides/requires (bug #741104)
- Drop --enable-mpi-threads & --enable-openib-ibcm, no longer recognized

* Sat Jun 18 2011 Peter Robinson <pbrobinson@gmail.com> 1.5-4
- Exclude ARM platforms due to current lack of "atomic primitives" on the platform

* Thu Mar 17 2011 Jay Fenlason <fenlason@redhat.com> 1.5-3
- Add dt-textrel patch to close
  Resolves: bz679489
- Add memchecker and esmtp support
  Resolves: bz647011

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Oct 18 2010 Jay Fenlason <fenlason@redhat.com> 1.5-1
- set MANPATH in openmpi module file
- Upgrade to 1.5
- Workaround for rhbz#617766 appears to no longer be needed for 1.5
- remove pkgconfig files in instal
- Remove orteCC.1 dangling symlink
- Adjust the files entries for share/openmpi/help* and share/openmpi/mca*
- Adjust the files entries for share/openmpi/mpi*
- Add files entry for share/openmpi/orte*.txt

* Sat Sep 05 2010 Dennis Gilmore <dennis@ausil.us> - 1.4.1-7
- disable valgrind support on sparc arches

* Sat Jul 24 2010 David Malcolm <dmalcolm@redhat.com> - 1.4.1-6
- workaround for rhbz#617766

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 1.4.1-5
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Mon Mar 29 2010 Jay Fenlason <fenlason@redhat.com> - 1.4.1-4
- Update to fix licencing and packaging issues:
  Use the system plpa and ltdl librarires rather than the ones in the tarball
  Remove licence incompatible files from the tarball.
- update module.in to prepend-path		PYTHONPATH

* Tue Mar 9 2010 Jay Fenlason <fenlason@redhat.com> - 1.4.1-3
- remove the pkgconfig file completely like we did in RHEL.

* Tue Jan 26 2010 Jay Fenlason <fenlason@redhat.com> - 1.4.1-2
- BuildRequires: python

* Tue Jan 26 2010 Jay Fenlason <fenlason@redhat.com> - 1.4.1-1
- New upstream version, which includes the changeset_r22324 patch.
- Correct a typo in the Source0 line in this spec file.

* Fri Jan 15 2010 Doug Ledford <dledford@redhat.com> - 1.4-4
- Fix an issue with usage of _cc_name_suffix that cause a broken define in
  our module file

* Fri Jan 15 2010 Doug Ledford <dledford@redhat.com> - 1.4-3
- Fix pkgconfig file substitution
- Bump version so we are later than the equivalent version from Red Hat
  Enterprise Linux

* Wed Jan 13 2010 Doug Ledford <dledford@redhat.com> - 1.4-1
- Update to latest upstream stable version
- Add support for libibcm usage
- Enable sge support via configure options since it's no longer on by default
- Add patch to resolve allreduce issue (bz538199)
- Remove no longer needed patch for Chelsio cards

* Tue Sep 22 2009 Jay Fenlason <fenlason@redhat.com> - 1.3.3-6
- Create and own man* directories for use by dependent packages.

* Wed Sep 16 2009 Jay Fenlason <fenlason@redhat.com> - 1.3.3-5
- Move the module file from %{_datadir}/Modules/modulefiles/%{namearch} to
  %{_sysconfdir}/modulefiles/%{namearch} where it belongs.
- Have the -devel subpackage own the man1 and man7 directories for completeness.
- Add a blank line before the clean section.
- Remove --enable-mpirun-prefix-by-default from configure.

* Wed Sep 9 2009 Jay Fenlason <fenlason@redhat.com> - 1.3.3-4
- Modify packaging to conform to
  https://fedoraproject.org/wiki/PackagingDrafts/MPI (bz521334).
- remove --with-ft=cr from configure, as it was apparently causing problems
  for some people.
- Add librdmacm-devel and librdmacm to BuildRequires (related bz515565).
- Add openmpi-bz515567.patch to add support for the latest Chelsio device IDs
  (related bz515567).
- Add exclude-arch (s390 s390x) because we don't have required -devel packages
  there.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

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

