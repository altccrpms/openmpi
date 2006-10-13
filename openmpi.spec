Name:           openmpi
Version:        1.1
Release:        6%{?dist}
Summary:        Open Message Passing Interface

Group:          Development/Libraries
License:        BSD
URL:            http://www.open-mpi.org/
Source0:       	http://www.open-mpi.org/software/ompi/v1.1/downloads/%{name}-%{version}.tar.bz2
Source1:	openmpi.pc.in
Source2:	openmpi.module.in
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  gcc-gfortran, autoconf, automake, libtool
#BuildRequires:  libibverbs-devel, opensm-devel, libsysfs-devel
Requires(post): /sbin/ldconfig, /usr/sbin/alternatives
Requires:	%{name}-libs = %{version}-%{release}
ExclusiveArch: i386 x86_64 ia64 ppc ppc64

%package libs
Summary:	Libraries used by openmpi programs
Group:		Development/Libraries

%package devel
Summary:        Development files for openmpi
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description
Open MPI is an open source, freely available implementation of both the 
MPI-1 and MPI-2 standards, combining technologies and resources from
several other projects (FT-MPI, LA-MPI, LAM/MPI, and PACX-MPI) in
order to build the best MPI library available.  A completely new MPI-2
compliant implementation, Open MPI offers advantages for system and
software vendors, application developers, and computer science
researchers. For more information, see http://www.open-mpi.org/ .

%description libs
Contains shared libraries used by openmpi applications

%description devel
Contains development headers and libraries for openmpi

%ifarch i386 ppc
%define mode 32
%else
  %ifarch s390
  %define mode 31
  %else
  %define mode 64
  %endif
%endif
%ifarch i386 ppc64 s390
%define priority 10
%else
%define priority 11
%endif

%prep
%setup -q
%ifarch x86_64
XCFLAGS="$RPM_OPT_FLAGS -fPIC"
XCXXFLAGS="$RPM_OPT_FLAGS -fPIC"
XFFLAGS="$RPM_OPT_FLAGS -fPIC"
%endif
#%ifarch i386 x86_64 ia64 ppc ppc64 # arches with openib support
#%configure \
#	--includedir=%{_includedir}/%{name} \
#	--libdir=%{_libdir}/%{name} \
#	--datadir=%{_datadir}/%{name}/help%{mode} \
#	--with-openib=/usr \
#	LDFLAGS='-Wl,-z,noexecstack' \
#	CFLAGS="$CFLAGS $XCFLAGS" \
#	CXXFLAGS="$CFLAGS $XCFLAGS" \
#	FFLAGS="$FFLAGS $XFLAGS";
#%else # no openib support, but plain tcp/ip still works and is usefull
%configure \
	--includedir=%{_includedir}/%{name} \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name}/help%{mode} \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="$CFLAGS $XCFLAGS" \
	CXXFLAGS="$CFLAGS $XCFLAGS" \
	FFLAGS="$FFLAGS $XFLAGS";
#%endif
# ${datadir}/openmpi will be used ONLY for the english help*.txt files

%build
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
make install DESTDIR=${RPM_BUILD_ROOT}

# The three installed man pages are all identical and could be hard links.
# Doesn't really matter though, since we are using alternatives to do
# master and slave linking, remove the man page that goes with the common
# name and link to the uncommon man page via alternatives.
rm ${RPM_BUILD_ROOT}%{_mandir}/man1/mpiexec.1
rm ${RPM_BUILD_ROOT}%{_mandir}/man1/mpirun.1

# Remove the symlinks from common names to the unique name in /usr/bin too
rm ${RPM_BUILD_ROOT}%{_bindir}/mpi*
# Remove the unnecessary compiler common names
rm ${RPM_BUILD_ROOT}%{_bindir}/*{cc,c++,CC}
# Move the wrapper program to a name that denotes the mode it compiles
mv ${RPM_BUILD_ROOT}%{_bindir}/opal_wrapper{,-%{mode}}
# But, opal_wrapper needs to be called by a name that denotes the compiler
# type in order to work, so in order to leave it functional even when it isn't
# the currently selected system wide default via the alternatives program,
# make the proper symlinks from %{_datadir}/%{name}/bin to the wrapper
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}/bin%{mode}
for i in mpicc mpic++ mpicxx mpiCC mpif77 mpif90 opalcc opalc++ opalCC ortecc ortec++ orteCC; do
  ln -s %{_bindir}/opal_wrapper-%{mode} \
  	${RPM_BUILD_ROOT}%{_datadir}/%{name}/bin%{mode}/$i
done
# The fortran include file differs between 32/64bit environments, so make
# two copies
mkdir -p ${RPM_BUILD_ROOT}%{_includedir}/%{name}/%{mode}
mv ${RPM_BUILD_ROOT}%{_includedir}/%{name}/{mpif-config.h,%{mode}}
# and have the wrapper include the right one by using the wrapper-data.txt
# files for the fortran modes to signal the extra include dir
for i in ${RPM_BUILD_ROOT}%{_datadir}/%{name}/help%{mode}/openmpi/mpif{77,90}-wrapper-data.txt; do
  sed -e 's#extra_includes=#extra_includes='%{mode}' #' < $i > $i.out
  mv $i.out $i
done
# and we also need to force the compile mode via the wrapper-data.txt files
for i in ${RPM_BUILD_ROOT}%{_datadir}/%{name}/help%{mode}/openmpi/*wrapper-data.txt; do
  sed -e 's#compiler_flags=#compiler_flags=-m'%{mode}' #' < $i > $i.out
  mv $i.out $i
done

echo %{_libdir}/%{name} > ${RPM_BUILD_ROOT}%{_libdir}/%{name}/%{name}.ld.conf
# Make the pkgconfig files
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig;
sed 's#@NAME@#'%{name}'#;s#@VERSION@#'%{version}'#;s#@LIBDIR@#'%{_libdir}'#;s#@INCLUDEDIR@#'%{_includedir}'#;s#@MODE@#'%{mode}'#' < %SOURCE1 > ${RPM_BUILD_ROOT}/%{_libdir}/pkgconfig/%{name}.pc;
sed 's#@DATADIR@#'%{_datadir}'#;s#@NAME@#'%{name}'#;s#@LIBDIR@#'%{_libdir}'#;s#@INCLUDEDIR@#'%{_includedir}'#;s#@MODE@#'%{mode}'#' < %SOURCE2 > ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/%{name}.module


%clean
[ ! -z "${RPM_BUILD_ROOT}" ] && rm -rf ${RPM_BUILD_ROOT}

%post
alternatives --install %{_bindir}/mpirun mpi-run %{_bindir}/orterun \
		%{priority} \
	--slave %{_bindir}/mpiexec mpi-exec %{_bindir}/orterun \
	--slave %{_mandir}/man1/mpirun.1.gz mpi-run-man \
		%{_mandir}/man1/orterun.1.gz \
	--slave %{_mandir}/man1/mpiexec.1.gz mpi-exec-man \
		%{_mandir}/man1/orterun.1.gz

%preun
if [ "$1" -eq 0 ]; then
	alternatives --remove mpi-run %{_bindir}/orterun
fi

%post libs
alternatives --install %{_sysconfdir}/ld.so.conf.d/mpi%{mode}.conf \
		mpilibs%{mode} %{_libdir}/openmpi/openmpi.ld.conf %{priority}
/sbin/ldconfig

%preun libs
alternatives --remove mpilibs%{mode} %{_libdir}/openmpi/openmpi.ld.conf

%postun libs -p /sbin/ldconfig

%post devel
alternatives --install  %{_bindir}/mpicc mpicc \
			%{_bindir}/opal_wrapper-%{mode} %{priority} \
	--slave %{_bindir}/mpic++ mpic++ %{_bindir}/opal_wrapper-%{mode} \
	--slave %{_bindir}/mpiCC mpiCC %{_bindir}/opal_wrapper-%{mode} \
	--slave %{_bindir}/mpicxx mpicxx %{_bindir}/opal_wrapper-%{mode} \
	--slave %{_bindir}/mpif77 mpif77 %{_bindir}/opal_wrapper-%{mode} \
	--slave %{_bindir}/mpif90 mpif90 %{_bindir}/opal_wrapper-%{mode}

%preun devel
alternatives --remove mpicc %{_bindir}/opal_wrapper-%{mode}

%postun devel -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc LICENSE README
%config(noreplace) %{_sysconfdir}/openmpi-*
%{_bindir}/orteconsole
%{_bindir}/orted
%{_bindir}/orteprobe
%{_bindir}/orterun
%{_bindir}/ompi_info
%{_bindir}/openmpi
%{_mandir}
%{_datadir}/%{name}
%exclude %{_datadir}/%{name}/bin%{mode}
%exclude %{_datadir}/%{name}/help%{mode}/openmpi/*-wrapper-data.txt

%files libs
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/%{name}
%{_libdir}/%{name}/*.so.*
%{_libdir}/%{name}/%{name}/*.so
%{_libdir}/%{name}/*.conf

%files devel
%defattr(-,root,root,-)
%{_bindir}/opal_wrapper-%{mode}
%dir %{_includedir}/%{name}
%{_datadir}/%{name}/bin%{mode}
%{_datadir}/%{name}/help%{mode}/openmpi/*-wrapper-data.txt
%{_includedir}/%{name}/*
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/*.a
%{_libdir}/%{name}/*.la
%{_libdir}/%{name}/%{name}/*.la
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/%{name}/*.mod


%changelog
* Wed Oct 11 2006 Doug Ledford <dledford@redhat.com> - 1.1-6
- Bump rev to match fc6 rev
- Fixup some issue with alternatives support
- Split the 32bit and 64bit libs ld.so.conf.d files into two files so
  multilib or single lib installs both work properly
- Put libs into their own package
- Add symlinks to /usr/share/openmpi/bin%{mode} so that opal_wrapper-%{mode}
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

