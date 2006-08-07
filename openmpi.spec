Name:           openmpi
Version:        1.1
Release:        1%{?dist}
Summary:        Open Message Passing Interface

Group:          Development/Libraries
License:        BSD
URL:            http://www.open-mpi.org/
Source0:       	http://www.open-mpi.org/software/ompi/v1.1/downloads/%{name}-%{version}.tar.bz2
Source1:	relpath.sh
Source2:	openmpi.pc.in
Source3:	mpi_alternatives.in
Source4:	openmpi.module.in
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  gcc-gfortran, autoconf, automake, libtool
BuildRequires:  libibverbs-devel, opensm-devel, libsysfs-devel
Requires(post): /sbin/ldconfig
ExclusiveArch: i386 x86_64 ia64 ppc ppc64

%package devel
Summary:        Development files for openmpi
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description
Open MPI provides a programming and runtime environment for  
parallel and/or distributed networked multi-computer systems .
MPI stands for the Message Passing Interface. Written by the MPI Forum,
MPI is a standardized API typically used for parallel and/or distributed 
computing - see http://www.mpi-forum.org/ .
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
	--mandir=%{_datadir}/%{name}/man \
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
	--mandir=%{_datadir}/%{name}/man \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="$CFLAGS $XCFLAGS" \
	CXXFLAGS="$CFLAGS $XCFLAGS" \
	FFLAGS="$FFLAGS $XFLAGS";
%endif
# ${datadir}/openmpi will be used ONLY for the english help*.txt files
make %{?_smp_mflags}

%{?!OMbinpfx: %define OMbinpfx om-}   # prefix for OpenMPI binaries that clash with LAM
%{?!LAMbinpfx: %define LAMbinpfx lam-} # prefix for LAM binaries that clash with OpenMPI

%install
rm -rf ${RPM_BUILD_ROOT}
make install DESTDIR=${RPM_BUILD_ROOT} 
#
# Resolve LAM clashes and create %{_datadir}/openmpi/{bin,lib,include} :
. %SOURCE1
# ^- provides "relpath" function
rpath=`relpath ${RPM_BUILD_ROOT}/%{_bindir} ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin`;
mkdir -p ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin;
mkdir -p ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/man;
ln -s `relpath ${RPM_BUILD_ROOT}/%{_libdir}/%{name} ${RPM_BUILD_ROOT}/%{_datadir}/%{name}` ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/lib;
ln -s `relpath ${RPM_BUILD_ROOT}/%{_includedir}/%{name} ${RPM_BUILD_ROOT}/%{_datadir}/%{name}` ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/include;
# Links: (mpiCC,mpicxx)->mpicc,  (mpiexec,mpirun)->orterun
# Clashes with LAM: mpic++ mpicc mpif77 mpif90 mpiexec mpirun
rm -f ${RPM_BUILD_ROOT}/%{_bindir}/{mpiCC,mpicxx,mpiexec,mpirun}
(cd ${RPM_BUILD_ROOT}/%{_bindir}; ls) | egrep -v '^(mpic\+\+|mpicc|mpif77|mpif90)$' |
while read b; do
  ln -s ${rpath}/${b} ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/${b};
done;
for b in mpic++ mpicc mpif77 mpif90; do 
  mv ${RPM_BUILD_ROOT}/%{_bindir}/$b  ${RPM_BUILD_ROOT}/%{_bindir}/%{OMbinpfx}$b;
  ln -s ${rpath}/%{OMbinpfx}$b ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/$b;
done
ln -s ./%{OMbinpfx}mpif90 ${RPM_BUILD_ROOT}/%{_bindir}/mpif90
ln -s ${rpath}/%{OMbinpfx}mpic++ ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/mpiCC
ln -s ./%{OMbinpfx}mpic++ ${RPM_BUILD_ROOT}/%{_bindir}/%{OMbinpfx}mpiCC
ln -s ${rpath}/%{OMbinpfx}mpic++ ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/mpicxx
ln -s ./%{OMbinpfx}mpic++ ${RPM_BUILD_ROOT}/%{_bindir}/%{OMbinpfx}mpicxx
ln -s ${rpath}/orterun   ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/mpirun
ln -s ./orterun ${RPM_BUILD_ROOT}/%{_bindir}/%{OMbinpfx}mpirun
ln -s ${rpath}/orterun   ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/bin/mpiexec
ln -s ./orterun ${RPM_BUILD_ROOT}/%{_bindir}/%{OMbinpfx}mpiexec
mkdir -p ${RPM_BUILD_ROOT}/%{_sysconfdir}/ld.so.conf.d
# Create ld.so config file for selection with mpi_alternatives:
echo %{_libdir}/%{name} > ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/ld.conf
# Create ghost mpi.conf ld.so config file:
touch ${RPM_BUILD_ROOT}/%{_sysconfdir}/ld.so.conf.d/mpi.conf
# We don't like .la files
find ${RPM_BUILD_ROOT}%{_libdir} -name \*.la | xargs rm
# Make the pkgconfig files
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig;
sed 's#@VERSION@#'%{version}'#;s#@LIBDIR@#'%{_libdir}/%{name}'#;s#@INCLUDEDIR@#'%{_includedir}/%{name}'#' < %SOURCE2 > ${RPM_BUILD_ROOT}/%{_libdir}/pkgconfig/%{name}.pc;
# Make the alternatives utility script:
mkdir -p ${RPM_BUILD_ROOT}/%{_sbindir}
sed 's#@BINDIR@#'%{_bindir}'#;s#@OMBINPFX@#'%{OMbinpfx}'#;s#@LAMBINPFX@#'%{LAMbinpfx}'#;s#@DATADIR@#'%{_datadir}'#;s#@SYSCONFDIR@#'%{_sysconfdir}'#'  < %SOURCE3 > ${RPM_BUILD_ROOT}/%{_sbindir}/mpi_alternatives;
chmod +x ${RPM_BUILD_ROOT}/%{_sbindir}/mpi_alternatives;
sed 's#@DATADIR@#'%{_datadir}/%{name}'#;s#@NAME@#'%{name}'#' < %SOURCE4 > ${RPM_BUILD_ROOT}/%{_datadir}/%{name}/%{name}.module
:;

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
if [ "$1" -ge 1 ]; then
   if [ ! -e %{_sysconfdir}/ld.so.conf.d/mpi.conf ]; then
   # handle the case where openmpi is installed without lam:
	ln -s %{_datadir}/%{name}/ld.conf %{_sysconfdir}/ld.so.conf.d/mpi.conf;
   fi;
fi;
/sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel -p /sbin/ldconfig

%postun devel -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc LICENSE README
%ghost  %{_sysconfdir}/ld.so.conf.d/mpi.conf
%config(noreplace) %{_sysconfdir}/openmpi-*
%{_bindir}/orte*
#%{_bindir}/*run
%{_bindir}/*exec
%{_bindir}/*info
%{_sbindir}/mpi_alternatives
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/%{name}
%{_libdir}/%{name}/*.so.*
%{_libdir}/%{name}/%{name}/*.so
%{_libdir}/%{name}/*.mod
%{_datadir}/%{name}/bin
%{_datadir}/%{name}/lib
%{_datadir}/%{name}/man
%{_datadir}/%{name}/help
%{_datadir}/%{name}/%{name}.module
%{_datadir}/%{name}/ld.conf

%files devel
%defattr(-,root,root,-)
%{_bindir}/*
%exclude %{_bindir}/orte*
%exclude %{_bindir}/*run
%exclude %{_bindir}/*exec
%exclude %{_bindir}/*info
%{_includedir}/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/*.a
%{_libdir}/pkgconfig/%{name}.pc
%{_datadir}/%{name}/include


%changelog
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

