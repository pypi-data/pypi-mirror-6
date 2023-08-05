
Summary: The libvirt virtualization API python binding
Name: libvirt-python
Version: 1.2.0
Release: 1%{?dist}%{?extra_release}
Source0: http://libvirt.org/sources/python/%{name}-%{version}.tar.gz
Url: http://libvirt.org
License: LGPLv2+
Group: Development/Libraries
BuildRequires: libvirt-devel >= 0.9.11
BuildRequires: python-devel

# Don't want provides for python shared objects
%{?filter_provides_in: %filter_provides_in %{python_sitearch}/.*\.so}
%{?filter_setup}

%description
The libvirt-python package contains a module that permits applications
written in the Python programming language to use the interface
supplied by the libvirt library to use the virtualization capabilities
of recent versions of Linux (and other OSes).

%prep
%setup -q

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root=%{buildroot}
rm -f %{buildroot}%{_libdir}/python*/site-packages/*egg-info

%files
%defattr(-,root,root)
%doc ChangeLog AUTHORS NEWS README COPYING COPYING.LESSER examples/
%{_libdir}/python*/site-packages/libvirt.py*
%{_libdir}/python*/site-packages/libvirt_qemu.py*
%{_libdir}/python*/site-packages/libvirt_lxc.py*
%{_libdir}/python*/site-packages/libvirtmod*

%changelog
