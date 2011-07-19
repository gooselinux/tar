%if %{?WITH_SELINUX:0}%{!?WITH_SELINUX:1}
%define WITH_SELINUX 1
%endif
Summary: A GNU file archiving program
Name: tar
Epoch: 2
Version: 1.23
Release: 3%{?dist}
License: GPLv3+
Group: Applications/Archiving
URL: http://www.gnu.org/software/tar/
Source0: ftp://ftp.gnu.org/pub/gnu/tar/tar-%{version}.tar.bz2
Source1: ftp://ftp.gnu.org/pub/gnu/tar/tar-%{version}.tar.bz2.sig
#Manpage for tar and gtar, a bit modified help2man generated manpage
Source2: tar.1
#Stop issuing lone zero block warnings
Patch1: tar-1.14-loneZeroWarning.patch
#Fix extracting sparse files to a filesystem like vfat,
#when ftruncate may fail to grow the size of a file.(#179507)
Patch2: tar-1.15.1-vfatTruncate.patch
#Add support for selinux, acl and extended attributes
Patch3: tar-1.23-xattrs.patch
#change inclusion defaults of tar to "--wildcards --anchored
#--wildcards-match-slash" for compatibility reasons (#206841)
Patch4: tar-1.17-wildcards.patch
#ignore errors from setting utime() for source file
#on read-only filesystem (#500742)
Patch5: tar-1.22-atime-rofs.patch
#Do not sigabrt with new gcc/glibc because of writing to
#struct members of gnutar header at once via strcpy
Patch6: tar-1.22-fortifysourcessigabrt.patch
#fix support for --old-archive long option
Patch7: tar-1.23-oldarchive.patch
Requires: info
BuildRequires: autoconf automake gzip texinfo gettext libacl-devel gawk rsh
%if %{WITH_SELINUX}
BuildRequires: libselinux-devel
%endif
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

%description
The GNU tar program saves many files together in one archive and can
restore individual files (or all of the files) from that archive. Tar
can also be used to add supplemental files to an archive and to update
or list files in the archive. Tar includes multivolume support,
automatic archive compression/decompression, the ability to perform
remote archives, and the ability to perform incremental and full
backups.

If you want to use tar for remote backups, you also need to install
the rmt package.

%prep
%setup -q
%patch1 -p1 -b .loneZeroWarning
%patch2 -p1 -b .vfatTruncate
%patch3 -p1 -b .xattrs
%patch4 -p1 -b .wildcards
%patch5 -p1 -b .rofs
%patch6 -p1 -b .fortify
%patch7 -p1 -b .oldarchive
autoreconf

%build
%configure --bindir=/bin --libexecdir=/sbin \
%if %{WITH_SELINUX}
  --enable-selinux
%endif
make

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT bindir=/bin libexecdir=/sbin install

ln -s tar ${RPM_BUILD_ROOT}/bin/gtar
rm -f $RPM_BUILD_ROOT/%{_infodir}/dir
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/man1
install -c -p -m 0644 %{SOURCE2} ${RPM_BUILD_ROOT}%{_mandir}/man1
ln -s tar.1.gz ${RPM_BUILD_ROOT}%{_mandir}/man1/gtar.1

# XXX Nuke unpackaged files.
rm -f ${RPM_BUILD_ROOT}/sbin/rmt

%find_lang %name

%check
rm -f ${RPM_BUILD_ROOT}/test/testsuite
make check

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
if [ -f %{_infodir}/tar.info.gz ]; then
   /sbin/install-info %{_infodir}/tar.info.gz %{_infodir}/dir || :
fi

%preun
if [ $1 = 0 ]; then
   if [ -f %{_infodir}/tar.info.gz ]; then
      /sbin/install-info --delete %{_infodir}/tar.info.gz %{_infodir}/dir || :
   fi
fi

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS ChangeLog ChangeLog.1 NEWS README THANKS TODO
%ifos linux
/bin/tar
/bin/gtar
%{_mandir}/man1/tar.1*
%{_mandir}/man1/gtar.1*
%else
%{_bindir}/*
%{_libexecdir}/*
%{_mandir}/man*/*
%endif

%{_infodir}/tar.info*

%changelog
* Tue Jul 19 2011 Mike Adams <shalkie@gooseproject.org> 2:1.23-3
- Initial rebuild for GoOSe Linux 6

* Thu Jul 08 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.23-3
- recognize old-archive/portability options(#594044)

* Tue Jun 01 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.23-2
- allow storing of extended attributes for fifo and block
  or character devices files(#598456)

* Mon Mar 15 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.23-1
- new upstream release 1.23(#573662), remove applied patches
- update help2maned manpage

* Thu Mar 11 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.22-15
- CVE-2010-0624 tar, cpio: Heap-based buffer overflow
  by expanding a specially-crafted archive (#571842)
- realloc within check_exclusion_tags() caused invalid write
  (#571523)
- not closing file descriptors for excluded files/dirs with
  exlude-tag... options could cause descriptor exhaustion
  (#571523)
- support for "lustre.*" extended attributes (#572442)
- allow build without SELinux support

* Thu Feb 04 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.22-14
- fix segfault with corrupted metadata in code_ns_fraction
  (#531441)

* Tue Jan 05 2010 Ondrej Vasik <ovasik@redhat.com> 2:1.22-13
- do not fail with POSIX 2008 glibc futimens()
- temporarily disable fix for #531441, causing stack smashing
  with newer glibc

* Fri Dec 18 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-12
- use Requires instead of Prereq to silence rpmlint

* Tue Dec 08 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-11
- fix segfault with corrupted metadata in code_ns_fraction
  (#531441)
- commented patches and sources

* Fri Nov 27 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-10
- store xattrs for symlinks (#525992) - by Kamil Dudka
- update tar(1) manpage (#539787)
- fix memory leak in xheader (#518079)

* Wed Nov 18 2009 Kamil Dudka <kdudka@redhat.com> 2:1.22-9
- store SELinux context for symlinks (#525992)

* Thu Aug 27 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-8
- provide symlink manpage for gtar

* Thu Aug 06 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-7
- do process install-info only without --excludedocs(#515923)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.22-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 16 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-5
- Fix restoring of directory default acls(#511145)
- Do not patch generated autotools files

* Thu Jun 25 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-4
- Report record size only if the archive refers to a device
  (#487760)
- Do not sigabrt with new gcc/glibc because of writing to
  struct members of gnutar header at once via strcpy

* Fri May 15 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-3
- ignore errors from setting utime() for source file
  on read-only filesystem (#500742)

* Fri Mar 06 2009 Kamil Dudka <kdudka@redhat.com> 2:1.22-2
- improve tar-1.14-loneZeroWarning.patch (#487315)

* Mon Mar 02 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.22-1
- New upstream release 1.22, removed applied patch

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.21-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 05 2009 Ondrej Vasik <ovasik@redhat.com> 2:1.21-1
- New upstream release 1.21, removed applied patches
- add support for -I option, fix testsuite failure

* Thu Dec 11 2008 Ondrej Vasik <ovasik@redhat.com> 2:1.20-6
- add BuildRequires for rsh (#475950)

* Fri Nov 21 2008 Ondrej Vasik <ovasik@redhat.com> 2:1.20-5
- fix off-by-one errors in xattrs patch (#472355)

* Mon Nov 10 2008 Kamil Dudka <kdudka@redhat.com> 2:1.20-4
- fixed bug #465803: labels with --multi-volume (upstream patch)

* Fri Oct 10 2008 Ondrej Vasik <ovasik@redhat.com> 2:1.20-3
- Fixed wrong documentation for xattrs options (#466517)
- fixed bug with null file terminator and change dirs
  (upstream)

* Fri Aug 29 2008 Ondrej Vasik <ovasik@redhat.com> 2:1.20-2
- patch fuzz clean up

* Mon May 26 2008 Ondrej Vasik <ovasik@redhat.com> 2:1.20-1
- new upstream release 1.20 (lzma support, few new options
  and bugfixes)
- heavily modified xattrs patches(as tar-1.20 now uses automake
  1.10.1)

* Tue Feb 12 2008 Radek Brich <rbrich@redhat.com> 2:1.19-3
- do not print getfilecon/setfilecon warnings when SELinux is disabled
  or SELinux data are not available (bz#431879)
- fix for GCC 4.3

* Mon Jan 21 2008 Radek Brich <rbrich@redhat.com> 2:1.19-2
- fix errors in man page
  * fix definition of --occurrence (bz#416661, patch by Jonathan Wakely)
  * update meaning of -l: it has changed from --one-filesystem
    to --check-links (bz#426717)
- update license tag, tar 1.19 is GPLv3+

* Mon Dec 17 2007 Radek Brich <rbrich@redhat.com> 2:1.19-1
- upgrade to 1.19
- updated xattrs patch, removed 3 upstream patches

* Wed Dec 12 2007 Radek Brich <rbrich@redhat.com> 2:1.17-5
- fix (non)detection of xattrs
- move configure stuff from -xattrs patch to -xattrs-conf,
  so the original patch could be easily read
- fix -xattrs patch to work with zero length files and show
  warnings when xattrs not available (fixes by James Antill)
- possible corruption (#408621) - add warning to man page
  for now, may be actually fixed later, depending on upstream

* Tue Oct 23 2007 Radek Brich <rbrich@redhat.com> 2:1.17-4
- upstream patch for CVE-2007-4476
  (tar stack crashing in safer_name_suffix)

* Tue Aug 28 2007 Radek Brich <rbrich@redhat.com> 2:1.17-3
- gawk build dependency

* Tue Aug 28 2007 Radek Brich <rbrich@redhat.com> 2:1.17-2
- updated license tag
- fixed CVE-2007-4131 tar directory traversal vulnerability (#251921)

* Thu Jun 28 2007 Radek Brich <rbrich@redhat.com> 2:1.17-1
- new upstream version
- patch for wildcards (#206841), restoring old behavior
- patch for testsuite
- update -xattrs patch
- drop 13 obsolete patches

* Tue Feb 06 2007 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-26
- fix spec file to meet Fedora standards (#226478)

* Mon Jan 03 2007 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-25
- fix non-failsafe install-info use in scriptlets (#223718)

* Wed Jan 03 2007 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-24
- supply tar man page (#219375)

* Tue Dec 12 2006 Florian La Roche <laroche@redhat.com> 2:1.15.1-23
- fix CVE-2006-6097 GNU tar directory traversal (#216937)

* Sat Dec 10 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-22
- fix some rpmlint spec file issues

* Wed Oct 25 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-21
- build with dist-tag

* Mon Oct 09 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-20
- another fix of tar-1.15.1-xattrs.patch from James Antill

* Wed Oct 04 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-19
- another fix of tar-1.15.1-xattrs.patch from James Antill

* Sun Oct 01 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-18
- fix tar-1.15.1-xattrs.patch (#208701)

* Tue Sep 19 2006 Peter Vrabec <pvrabec@redhat.com> 2:1.15.1-17
- start new epoch, downgrade to solid stable 1.15.1-16 (#206979), 
- all patches are backported

* Tue Sep 19 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.91-2
- apply patches, which were forgotten during upgrade

* Wed Sep 13 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.91-1
- upgrade, which also fix incremental backup (#206121)

* Fri Sep 08 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-7
- fix tar-debuginfo package (#205615)

* Thu Aug 10 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-6
- add xattr support (#200925), patch from james.antill@redhat.com

* Mon Jul 24 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-5
- fix incompatibilities in appending files to the end 
  of an archive (#199515)

* Tue Jul 18 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-4
- fix problem with unpacking archives in a directory for which 
  one has write permission but does not own (such as /tmp) (#149686)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.15.90-3.1
- rebuild

* Thu Jun 29 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-3
- fix typo in tar.1 man page

* Tue Apr 25 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-2
- exclude listed02.at from testsuite again, because it 
  still fails on s390

* Tue Apr 25 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.90-1
- upgrade

* Mon Apr 24 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.1-16
- fix problem when options at the end of command line were 
  not recognized (#188707)

* Thu Apr 13 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.1-15
- fix segmentation faul introduced with hugeSparse.patch

* Wed Mar 22 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.1-14
- fix problems with extracting large sparse archive members (#185460)

* Fri Feb 17 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.1-13
- fix heap overlfow bug CVE-2006-0300 (#181773)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.15.1-12.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.15.1-12.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb 06 2006 Peter Vrabec <pvrabec@redhat.com> 1.15.1-12
- fix extracting sparse files to a filesystem like vfat,
  when ftruncate may fail to grow the size of a file.(#179507)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 04 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-11
- correctly pad archive members that shrunk during archiving (#172373)

* Tue Sep 06 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-10
- provide man page (#163709, #54243, #56041)

* Mon Aug 15 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-9
- silence newer option (#164902)

* Wed Jul 27 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-8
- A file is dumpable if it is sparse and both --sparse
  and --totals are specified (#154882)
 
* Tue Jul 26 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-7
- exclude listed02.at from testsuite

* Fri Jul 22 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-6
- remove tar-1.14-err.patch, not needed (158743)

* Fri Apr 15 2005 Peter Vrabec <pvrabec@redhat.com> 1.15.1-5
- extract sparse files even if the output fd is not seekable.(#154882)
- (sparse_scan_file): Bugfix. offset had incorrect type.

* Mon Mar 14 2005 Peter Vrabec <pvrabec@redhat.com>
- gcc4 fix (#150993) 1.15.1-4

* Mon Jan 31 2005 Peter Vrabec <pvrabec@redhat.com>
- rebuild 1.15.1-3

* Mon Jan 17 2005 Peter Vrabec <pvrabec@redhat.com>
- fix tests/testsuite

* Fri Jan 07 2005 Peter Vrabec <pvrabec@redhat.com>
- upgrade to 1.15.1

* Mon Oct 11 2004 Peter Vrabec <pvrabec@redhat.com>
- patch to stop issuing lone zero block warnings
- rebuilt

* Mon Oct 11 2004 Peter Vrabec <pvrabec@redhat.com>
- URL added to spec file
- spec file clean up

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun  7 2004 Jeff Johnson <jbj@jbj.org> 1.14-1
- upgrade to 1.14.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun 17 2003 Jeff Johnson <jbj@redhat.com> 1.13.25-13
- rebuilt because of crt breakage on ppc64.
- dump automake15 requirement.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Nov 29 2002 Tim Powers <timp@redhat.com> 1.13.25-10
- fix broken buildrquires on autoconf253

* Thu Nov  7 2002 Jeff Johnson <jbj@redhat.com> 1.13.25-9
- rebuild from CVS.

* Fri Aug 23 2002 Phil Knirsch <pknirsch@redhat.com> 1.13.25-8
- Included security patch from errata release.

* Mon Jul  1 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.25-7
- Fix argv NULL termination (#64869)

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Apr  9 2002 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.25-4
- Fix build with autoconf253 (LIBOBJ change; autoconf252 worked)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Oct 23 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.25-2
- Don't include hardlinks to sockets in a tar file (#54827)

* Thu Sep 27 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.25-1
- 1.13.25

* Tue Sep 18 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.22-1
- Update to 1.13.22, adapt patches

* Mon Aug 27 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.19-6
- Fix #52084

* Thu May 17 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.13.19-5
- Fix build with current autoconf (stricter checking on AC_DEFINE)
- Fix segfault when tarring directories without having read permissions
  (#40802)

* Tue Mar  6 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Don't depend on librt.

* Fri Feb 23 2001 Trond Eivind Glomsröd <teg@redhat.com>
- langify

* Thu Feb 22 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up the man page (#28915)

* Wed Feb 21 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.3.19, nukes -I and fixes up -N
- Add -I back in as an alias to -j with a nice loud warning

* Mon Oct 30 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.3.18
- Update man page to reflect changes

* Thu Oct  5 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix the "ignore failed read" option (Bug #8330)

* Mon Sep 25 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- fix hang on tar tvzf - <something.tar.gz, introduced by
  exit code fix (Bug #15448), Patch from Tim Waugh <twaugh@redhat.com>

* Fri Aug 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- really fix exit code (Bug #15448)

* Mon Aug  7 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- fix exit code (Bug #15448), patch from Tim Waugh <twaugh@redhat.com>

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 19 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- FHSify

* Fri Apr 28 2000 Bill Nottingham <notting@redhat.com>
- fix for ia64

* Wed Feb  9 2000 Bernhard Rosenkränzer <bero@redhat.com>
- Fix the exclude bug (#9201)

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- man pages are compressed
- fix description
- fix fnmatch build problems

* Sun Jan  9 2000 Bernhard Rosenkränzer <bero@redhat.com>
- 1.13.17
- remove dotbug patch (fixed in base)
- update download URL

* Fri Jan  7 2000 Bernhard Rosenkränzer <bero@redhat.com>
- Fix a severe bug (tar xf any_package_containing_. would delete the
  current directory)

* Wed Jan  5 2000 Bernhard Rosenkränzer <bero@redhat.com>
- 1.3.16
- unset LINGUAS before running configure

* Tue Nov  9 1999 Bernhard Rosenkränzer <bero@redhat.com>
- 1.13.14
- Update man page to know about -I / --bzip
- Remove dependancy on rmt - tar can be used for anything local
  without it.

* Fri Aug 27 1999 Preston Brown <pbrown@redhat.com>
- upgrade to 1.13.11.

* Wed Aug 18 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.13.9.

* Thu Aug 12 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.13.6.
- support -y --bzip2 options for bzip2 compression (#2415).

* Fri Jul 23 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.13.5.

* Tue Jul 13 1999 Bill Nottingham <notting@redhat.com>
- update to 1.13

* Sat Jun 26 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.12.64014.
- pipe patch corrected for remote tars now merged in.

* Sun Jun 20 1999 Jeff Johnson <jbj@redhat.com>
- update to tar-1.12.64013.
- subtract (and reopen #2415) bzip2 support using -y.
- move gtar to /bin.

* Tue Jun 15 1999 Jeff Johnson <jbj@redhat.com>
- upgrade to tar-1.12.64011 to
-   add bzip2 support (#2415)
-   fix filename bug (#3479)

* Mon Mar 29 1999 Jeff Johnson <jbj@redhat.com>
- fix suspended tar with compression over pipe produces error (#390).

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 8)

* Mon Mar 08 1999 Michael Maher <mike@redhat.com>
- added patch for bad name cache. 
- FIXES BUG 320

* Wed Feb 24 1999 Preston Brown <pbrown@redhat.com>
- Injected new description and group.

* Fri Dec 18 1998 Preston Brown <pbrown@redhat.com>
- bumped spec number for initial rh 6.0 build

* Tue Aug  4 1998 Jeff Johnson <jbj@redhat.com>
- add /usr/bin/gtar symlink (change #421)

* Tue Jul 14 1998 Jeff Johnson <jbj@redhat.com>
- Fiddle bindir/libexecdir to get RH install correct.
- Don't include /sbin/rmt -- use the rmt from dump.
- Turn on nls.

* Mon Apr 27 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Thu Oct 16 1997 Donnie Barnes <djb@redhat.com>
- updated from 1.11.8 to 1.12
- various spec file cleanups
- /sbin/install-info support

* Thu Jun 19 1997 Erik Troan <ewt@redhat.com>
- built against glibc

* Thu May 29 1997 Michael Fulbright <msf@redhat.com>
- Fixed to include rmt
