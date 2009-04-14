Name:			openmpi
Version:		1.3.1
Release:		1%{?dist}
Summary:		Open Message Passing Interface
Group:			Development/Libraries
License:		BSD
URL:			http://www.open-mpi.org/
Source0:		http://www.open-mpi.org/software/ompi/v1.3/downloads/%{name}-%{version}.tar.bz2
Source1:		openmpi.pc.in
Source2:		openmpi.module.in
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:		gcc-gfortran, libtool, numactl-devel, libtorque-devel
#BuildRequires:		libibverbs-devel, opensm-devel
#%ifnarch ppc
#BuildRequires:		dapl-devel
#%endif
Requires(post):		/sbin/ldconfig
Requires(post):		%{_sbindir}/update-alternatives
Requires(preun):	%{_sbindir}/update-alternatives
Requires:		%{name}-libs = %{version}-%{release}

%description
Open MPI is an open source, freely available implementation of both the
MPI-1 and MPI-2 standards, combining technologies and resources from
several other projects (FT-MPI, LA-MPI, LAM/MPI, and PACX-MPI) in
order to build the best MPI library available.  A completely new MPI-2
compliant implementation, Open MPI offers advantages for system and
software vendors, application developers, and computer science
researchers. For more information, see http://www.open-mpi.org/ .

%package libs
Summary:		Libraries used by openmpi programs
Group:			Development/Libraries
Requires(post):		%{_sbindir}/update-alternatives
Requires(preun):	%{_sbindir}/update-alternatives

%description libs
Contains shared libraries used by openmpi applications.

%package devel
Summary:		Development files for openmpi
Group:			Development/Libraries
Requires:		%{name}-libs = %{version}-%{release}
Provides:		mpi-devel = %{version}-%{release}
Requires(post):		%{_sbindir}/update-alternatives
Requires(preun):	%{_sbindir}/update-alternatives

%description devel
Contains development headers and libraries for openmpi.

%package vt
Summary:		VampirTrace versions of openmpi programs
Group:			Development/Libraries
Requires:		%{name}-libs = %{version}-%{release}

%description vt
VampirTrace consists of a tool set and a run-time library for instrumentation 
and tracing of software applications. In particular, it is tailored towards 
parallel and distributed High Performance Computing (HPC) applications.
The instrumentation part modifies a given application in order to inject 
additional measurement calls during run-time. The tracing part provides the 
actual measurement functionality used by the instrumentation calls. By this 
means, a variety of detailed performance properties can be collected and 
recorded during run-time. This package contains the openmpi programs 
with VampirTrace enabled.

# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%define opt_cc gcc
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use
#define opt_cc_cflags

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
%ifarch i386 ppc sparcv9
%define mode 32
%define modeflag -m32
%endif
%ifarch ia64
%define mode 64
%endif
%ifarch s390
%define mode 31
%endif
%ifarch s390x
%define mode 64
%endif
%ifarch x86_64 ppc64 sparc64
%define mode 64
%define modeflag -m64
%endif

# That alternatives system selects the highest priority item as the default.
# Usually, that means 64bit preferred over 32bit on multilib, but ppc is an
# exception in that 32bit is preferred over 64bit.  So, the priority values
# selected here make that happen.
%ifarch i386 ppc64 s390 sparc64
%define priority 10
%else
%define priority 11
%endif

# We set this to for convenience, since this is the unique dir we use for this
# particular package, version, compiler
%define mpidir %{name}/%{version}-%{opt_cc}

%prep
%setup -q

%ifarch x86_64
XFLAGS="-fPIC"
%endif
%configure \
	--includedir=%{_includedir}/%{mpidir} \
	--libdir=%{_libdir}/%{mpidir} \
	--datadir=%{_datadir}/%{mpidir}/help%{mode} \
	--mandir=%{_datadir}/%{mpidir}/man \
	--with-threads=posix \
	--with-tm \
	CC=%{opt_cc} \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="%{?opt_cc_cflags} $RPM_OPT_FLAGS $XFLAGS" \
	CXXFLAGS="$RPM_OPT_FLAGS $XFLAGS" \
	FFLAGS="$RPM_OPT_FLAGS $XFLAGS";
# ${datadir}/openmpi will be used ONLY for the english help*.txt files

%build
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
make install DESTDIR=${RPM_BUILD_ROOT}

# Because no package owns the base openmpi directories, the install sets
# the mode wrong.  This will cause problems when the first copy of openmpi
# is installed on a system.  Correct the directory permissions here.
chmod 755 ${RPM_BUILD_ROOT}/%{_libdir}/openmpi
chmod 755 ${RPM_BUILD_ROOT}/%{_includedir}/openmpi
chmod 755 ${RPM_BUILD_ROOT}/%{_datadir}/openmpi

# Remove the symlinks from common names to the unique name in /usr/bin too
rm ${RPM_BUILD_ROOT}%{_bindir}/mpi*
# Move the wrapper program to a name that denotes the mode it compiles
mv ${RPM_BUILD_ROOT}%{_bindir}/opal_wrapper{,-%{version}-%{opt_cc}-%{mode}}
# But, opal_wrapper needs to be called by a name that denotes the compiler
# type in order to work, so in order to leave it functional even when it isn't
# the currently selected system wide default via the alternatives program,
# make the proper symlinks from %{_datadir}/%{name}/bin to the wrapper
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{mpidir}/bin%{mode}
for i in mpicc mpic++ mpicxx mpiCC mpif77 mpif90 ; do
  ln -s %{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
	${RPM_BUILD_ROOT}%{_datadir}/%{mpidir}/bin%{mode}/$i
done
# The fortran include file differs between 32/64bit environments, so make
# two copies
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}/%{mpidir}/%{mode}
mv ${RPM_BUILD_ROOT}%{_includedir}/%{mpidir}/{mpif-config.h,%{mode}}
# and have the wrapper include the right one by using the wrapper-data.txt
# files for the fortran modes to signal the extra include dir
for i in ${RPM_BUILD_ROOT}%{_datadir}/%{mpidir}/help%{mode}/openmpi/mpif{77,90}-wrapper-data.txt; do
  sed -e 's#extra_includes=#extra_includes='%{mode}' #' < $i > $i.out
  mv $i.out $i
done
# and we also need to force the compile mode via the wrapper-data.txt files
# (except on ia64 where the -m64 flag is not allowed by gcc)
%ifnarch ia64
for i in ${RPM_BUILD_ROOT}%{_datadir}/%{mpidir}/help%{mode}/openmpi/*wrapper-data.txt; do
  sed -e 's#compiler_flags=#compiler_flags='%{?modeflag}' #' < $i > $i.out
  mv $i.out $i
done
%endif

echo %{_libdir}/%{mpidir} > ${RPM_BUILD_ROOT}%{_libdir}/%{mpidir}/%{name}.ld.conf
# Make the pkgconfig files
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig;
sed 's#@NAME@#'%{name}'#g;s#@VERSION@#'%{version}'#g;s#@LIBDIR@#'%{_libdir}'#g;s#@INCLUDEDIR@#'%{_includedir}'#g;s#@MODE@#'%{mode}'#g;s#@CC@#'%{opt_cc}'#g;s#@MPIDIR@#'%{mpidir}'#g;s#@MODEFLAG@#'%{?modeflag}'#g' < %SOURCE1 > ${RPM_BUILD_ROOT}/%{_libdir}/pkgconfig/%{name}-%{version}-%{opt_cc}-%{mode}.pc;
sed 's#@NAME@#'%{name}'#g;s#@VERSION@#'%{version}'#g;s#@LIBDIR@#'%{_libdir}'#g;s#@INCLUDEDIR@#'%{_includedir}'#g;s#@DATADIR@#'%{_datadir}'#g;s#@MODE@#'%{mode}'#g;s#@CC@#'%{opt_cc}'#g;s#@MPIDIR@#'%{mpidir}'#g;s#@MODEFLAG@#'%{?modeflag}'#g' < %SOURCE2 > ${RPM_BUILD_ROOT}/%{_libdir}/%{mpidir}/%{name}.module;

# Ghost files for alternatives
touch ${RPM_BUILD_ROOT}%{_bindir}/mpirun
touch ${RPM_BUILD_ROOT}%{_bindir}/mpiexec
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1/
touch ${RPM_BUILD_ROOT}%{_mandir}/man1/mpirun.1.gz
touch ${RPM_BUILD_ROOT}%{_mandir}/man1/mpiexec.1.gz
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/ld.so.conf.d/
touch ${RPM_BUILD_ROOT}%{_sysconfdir}/ld.so.conf.d/mpi%{mode}.conf
touch ${RPM_BUILD_ROOT}%{_bindir}/mpicc
touch ${RPM_BUILD_ROOT}%{_bindir}/mpic++
touch ${RPM_BUILD_ROOT}%{_bindir}/mpiCC
touch ${RPM_BUILD_ROOT}%{_bindir}/mpicxx
touch ${RPM_BUILD_ROOT}%{_bindir}/mpif77
touch ${RPM_BUILD_ROOT}%{_bindir}/mpif90

# Clean up static libs
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/%{mpidir}/*.a

# This file is corrupt, don't try to package it.
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/vampirtrace/doc/opari/lacsi01.ps.gz

# Clean up long names
pushd ${RPM_BUILD_ROOT}%{_bindir}
for i in otfaux otfcompress otfconfig otfdump otfmerge; do
	ln -s %{_arch}-redhat-linux-gnu-$i $i;
done
popd

%clean
[ ! -z "${RPM_BUILD_ROOT}" ] && rm -rf ${RPM_BUILD_ROOT}

%post
%{_sbindir}/update-alternatives --install %{_bindir}/mpirun mpi-run %{_bindir}/orterun \
		%{priority} \
	--slave %{_bindir}/mpiexec mpi-exec %{_bindir}/orterun \
	--slave %{_mandir}/man1/mpirun.1.gz mpi-run-man \
		%{_datadir}/%{mpidir}/man/man1/mpirun.1.gz \
	--slave %{_mandir}/man1/mpiexec.1.gz mpi-exec-man \
		%{_datadir}/%{mpidir}/man/man1/orterun.1.gz

%preun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove mpi-run %{_bindir}/orterun
fi


%post libs
%{_sbindir}/update-alternatives --install %{_sysconfdir}/ld.so.conf.d/mpi%{mode}.conf \
		mpilibs%{mode} %{_libdir}/%{mpidir}/%{name}.ld.conf %{priority}
/sbin/ldconfig

%preun libs
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove mpilibs%{mode} %{_libdir}/%{mpidir}/%{name}.ld.conf
fi

%postun libs -p /sbin/ldconfig

%post devel
%{_sbindir}/update-alternatives --install %{_bindir}/mpicc mpicc \
			%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
			%{priority} \
	--slave %{_bindir}/mpic++ mpic++ \
		%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
	--slave %{_bindir}/mpiCC mpiCC \
		%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
	--slave %{_bindir}/mpicxx mpicxx \
		%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
	--slave %{_bindir}/mpif77 mpif77 \
		%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode} \
	--slave %{_bindir}/mpif90 mpif90 \
		%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode}

%preun devel
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove mpicc %{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode}
fi

%postun devel -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc LICENSE README
%config(noreplace) %{_sysconfdir}/openmpi-*
%dir %{_datadir}/%{mpidir}
%{_bindir}/ompi-clean
%{_bindir}/ompi-ps
%{_bindir}/ompi-server
%{_bindir}/opari
%{_bindir}/orte-clean
%{_bindir}/orte-iof
%{_bindir}/orte-ps
%{_bindir}/orted
%{_bindir}/orterun
%{_bindir}/ompi_info
%{_bindir}/*otf*
%ghost %{_bindir}/mpirun
%ghost %{_bindir}/mpiexec
%ghost %{_mandir}/man1/mpirun.1.gz
%ghost %{_mandir}/man1/mpiexec.1.gz
%{_datadir}/%{mpidir}/*
%exclude %{_datadir}/%{mpidir}/bin%{mode}
%exclude %{_datadir}/%{mpidir}/help%{mode}/openmpi/*-wrapper-data.txt
%exclude %{_datadir}/%{mpidir}/man/man3

%files libs
%defattr(-,root,root,-)
%dir %{_libdir}/%{mpidir}
%dir %{_libdir}/%{mpidir}/%{name}
%ghost %{_sysconfdir}/ld.so.conf.d/mpi%{mode}.conf
%{_libdir}/%{mpidir}/*.so.*
%{_libdir}/%{mpidir}/%{name}/*.so
%{_libdir}/%{mpidir}/*.conf

%files devel
%defattr(-,root,root,-)
%{_bindir}/opal_wrapper-%{version}-%{opt_cc}-%{mode}
%ghost %{_bindir}/mpicc
%ghost %{_bindir}/mpic++
%ghost %{_bindir}/mpiCC
%ghost %{_bindir}/mpicxx
%ghost %{_bindir}/mpif77
%ghost %{_bindir}/mpif90
%{_datadir}/%{mpidir}/bin%{mode}/
%{_datadir}/%{mpidir}/help%{mode}/openmpi/*-wrapper-data.txt
%{_includedir}/%{mpidir}/
%{_datadir}/%{mpidir}/man/man3/
%{_libdir}/%{mpidir}/*.so
%{_libdir}/%{mpidir}/*.la
%{_libdir}/%{mpidir}/%{name}/*.la
%{_libdir}/pkgconfig/%{name}-%{version}-%{opt_cc}-%{mode}.pc
%{_libdir}/%{mpidir}/*.mod
%{_libdir}/%{mpidir}/*.module

%files vt
%defattr(-,root,root,-)
%{_bindir}/vtcc
%{_bindir}/vtcxx
%{_bindir}/vtf77
%{_bindir}/vtf90
%{_bindir}/vtfilter
%{_bindir}/vtunify
%{_datadir}/vampirtrace/


%changelog
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

