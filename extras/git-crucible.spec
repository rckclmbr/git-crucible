%define name python26-crucible
%define version 0.1.1
%define unmangled_version 0.1.1
%define unmangled_version 0.1.1
%define release 1

Summary: Git extension that creates reviews in Crucible straight from the command line.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: BSD
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Josh Braegger <rckclmbr@gmail.com>
Requires: python26-argparse python26
Url: http://github.com/rckclmbr/git-crucible
Distribution: python26-gitcrucible

%description
Git extension that creates reviews in Crucible straight from the command line.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
#! /bin/sh
#
# This file becomes the install section of the generated spec file.
#

/usr/bin/env python2.6 setup.py install --single-version-externally-managed --root=${RPM_BUILD_ROOT} --record="INSTALLED_FILES"

# Sort the filelist so that directories appear before files. This avoids
# duplicate filename problems on some systems.
touch DIRS
for i in `cat INSTALLED_FILES`; do
if [ -f ${RPM_BUILD_ROOT}/$i ]; then
echo $i >>FILES
  fi
if [ -d ${RPM_BUILD_ROOT}/$i ]; then
echo %dir $i >>DIRS
  fi
done

# Make sure we match foo.pyo and foo.pyc along with foo.py (but only once each)
sed -e "/\.py[co]$/d" -e "s/\.py$/.py*/" DIRS FILES >INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc docs extras AUTHORS INSTALL LICENSE README.rst
