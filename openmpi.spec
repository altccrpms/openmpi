Name:           openmpi
Version:        1.1
Release:        4%{?dist}
Summary:        Open Message Passing Interface

Group:          Development/Libraries
License:        BSD
URL:            http://www.open-mpi.org/
Source0:       	http://www.open-mpi.org/software/ompi/v1.1/downloads/%{name}-%{version}.tar.bz2
Source1:	openmpi.pc.in
Source2:	openmpi.module.in
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  gcc-gfortran, autoconf, automake, libtool
BuildRequires:  libibverbs-devel, opensm-devel, libsysfs-devel
Requires(post): /sbin/ldconfig, /usr/sbin/alternatives
ExclusiveArch: i386 x86_64 ia64 ppc ppc64

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

%description devel
Contains development headers and libraries for openmpi

%prep
%setup -q

%build
%ifarch x86_64
XCFLAGS="$RPM_OPT_FLAGS -fPIC"
XCXXFLAGS="$RPM_OPT_FLAGS -fPIC"
XFFLAGS="$RPM_OPT_FLAGS -fPIC"
%endif
%ifarch i386 x86_64 ia64 ppc ppc64 # arches with openib support
%configure \
	--includedir=%{_includedir}/%{name} \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name}/help \
	--with-openib=/usr \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="$CFLAGS $XCFLAGS" \
	CXXFLAGS="$CFLAGS $XCFLAGS" \
	FFLAGS="$FFLAGS $XFLAGS";
%else # no openib support, but plain tcp/ip still works and is usefull
%configure \
	--includedir=%{_includedir}/%{name} \
	--libdir=%{_libdir}/%{name} \
	--datadir=%{_datadir}/%{name}/help \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="$CFLAGS $XCFLAGS" \
	CXXFLAGS="$CFLAGS $XCFLAGS" \
	FFLAGS="$FFLAGS $XFLAGS";
%endif
# ${datadir}/openmpi will be used ONLY for the english help*.txt files
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

echo %{_libdir}/%{name} > ${RPM_BUILD_ROOT}%{_libdir}/%{name}/%{name}.ld.conf
# Make the pkgconfig files
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig;
sed 's#@VERSION@#'%{version}'#;s#@LIBDIR@#'%{_libdir}/%{name}'#;s#@INCLUDEDIR@#'%{_includedir}/%{name}'#' < %SOURCE1 > ${RPM_BUILD_ROOT}/%{_libdir}/pkgconfig/%{name}.pc;
sed 's#@DATADIR@#'%{_datadir}/%{name}'#;s#@NAME@#'%{name}'#' < %SOURCE2 > ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/%{name}.module

%clean
[ ! -z "${RPM_BUILD_ROOT}" ] && rm -rf ${RPM_BUILD_ROOT}

%post
if [ "$1" -eq 1 ]; then
	alternatives --install %{_sysconfdir}/ld.so.conf.d/mpi.conf mpi \
				%{_libdir}/openmpi/openmpi.ld.conf 10 \
		--slave %{_bindir}/mpirun mpi-run %{_bindir}/orterun \
		--slave %{_bindir}/mpiexec mpi-exec %{_bindir}/orterun \
		--slave %{_mandir}/man1/mpirun.1.gz mpi-run-man \
			%{_mandir}/man1/orterun.1.gz \
		--slave %{_mandir}/man1/mpiexec.1.gz mpi-exec-man \
			%{_mandir}/man1/orterun.1.gz
fi;
/sbin/ldconfig

%preun
if [ "$1" -eq 0 ]; then
	alternatives --remove mpi %{_libdir}/openmpi/openmpi.ld.conf
fi

%postun -p /sbin/ldconfig

%post devel
if [ "$1" -eq 1 ]; then
	alternatives --install  %{_bindir}/mpicc mpicc \
				%{_bindir}/opal_wrapper 10 \
		--slave %{_bindir}/mpic++ mpic++ %{_bindir}/opal_wrapper \
		--slave %{_bindir}/mpiCC mpiCC %{_bindir}/opal_wrapper \
		--slave %{_bindir}/mpicxx mpicxx %{_bindir}/opal_wrapper \
		--slave %{_bindir}/mpif77 mpif77 %{_bindir}/opal_wrapper \
		--slave %{_bindir}/mpif90 mpif90 %{_bindir}/opal_wrapper
fi

%preun devel
if [ "$1" -eq 0 ]; then
	alternatives --remove mpicc %{_bindir}/opal_wrapper
fi

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
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/%{name}
%{_libdir}/%{name}/*.so.*
%{_libdir}/%{name}/%{name}/*.so
%{_libdir}/%{name}/*.conf
%{_mandir}/man1/*
%{_datadir}/%{name}

%files devel
%defattr(-,root,root,-)
%{_bindir}/opal_wrapper
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/*.a
%{_libdir}/%{name}/*.la
%{_libdir}/%{name}/%{name}/*.la
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/%{name}/*.mod


%changelog
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

