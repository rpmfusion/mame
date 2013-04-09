# ldplayer can be disabled by --without ldplayer or by changing to %bcond_with
# if it does not build. The debug build is disabled by default, please use
# --with debug to override
%bcond_without ldplayer
%bcond_with debug

%global baseversion 148
%global sourceupdate 3
#global svn 21418

%if 0%{?svn}
%global svnrelease .%{svn}svn
%endif

# work around low memory on the RPM Fusion builder
%bcond_without lowmem
%if %{with lowmem}
%global _find_debuginfo_dwz_opts %{nil}
%endif

Name:           mame
%if 0%{?sourceupdate}
Version:        0.%{baseversion}u%{sourceupdate}
%else
Version:        0.%{baseversion}
%endif

Release:        1%{?svnrelease}%{?dist}
Summary:        Multiple Arcade Machine Emulator

#Files in src/lib/util and src/osd (except src/osd/sdl) are BSD
License:        MAME License
URL:            http://mamedev.org/
%if 0%{?svn}
Source0:        %{name}-svn%{svn}.tar.xz
%else
Source0:        http://mamedev.org/downloader.php?file=releases/%{name}0%{baseversion}s.exe
#Source100:      whatsnew.zip
%if 0%{?sourceupdate}
#Source updates
Source1:        http://mamedev.org/updates/0%{baseversion}u1_diff.zip
Source2:        http://mamedev.org/updates/0%{baseversion}u2_diff.zip
Source3:        http://mamedev.org/updates/0%{baseversion}u3_diff.zip
#Source4:        http://mamedev.org/updates/0%{baseversion}u4_diff.zip
#Source5:        http://mamedev.org/updates/0%{baseversion}u5_diff.zip
#Source6:        http://mamedev.org/updates/0%{baseversion}u6_diff.zip
#Source7:        http://mamedev.org/updates/0%{baseversion}u7_diff.zip
#Source8:        http://mamedev.org/updates/0%{baseversion}u8_diff.zip
#Source9:        http://mamedev.org/updates/0%{baseversion}u9_diff.zip
%endif
%endif
Patch0:         %{name}-fortify.patch
Patch2:         %{name}-verbosebuild.patch

BuildRequires:  expat-devel
BuildRequires:  flac-devel
%if 0%{?fedora} >= 18
BuildRequires:  libjpeg-turbo-devel
%endif
%if !0%{?svn}
BuildRequires:  p7zip
%endif
BuildRequires:  python
BuildRequires:  qt-devel
BuildRequires:  SDL_ttf-devel
BuildRequires:  zlib-devel
Requires:       %{name}-data = %{version}-%{release}

%if 0%{?fedora} < 18
Provides:       bundled(libjpeg) = 8c
%endif
Provides:       bundled(lzma-sdk) = 9.22

%description
MAME stands for Multiple Arcade Machine Emulator.  When used in conjunction
with an arcade game's data files (ROMs), MAME will more or less faithfully
reproduce that game on a PC.

The ROM images that MAME utilizes are "dumped" from arcade games' original
circuit-board ROM chips.  MAME becomes the "hardware" for the games, taking
the place of their original CPUs and support chips.  Therefore, these games
are NOT simulations, but the actual, original games that appeared in arcades.

MAME's purpose is to preserve these decades of video-game history.  As gaming
technology continues to rush forward, MAME prevents these important "vintage"
games from being lost and forgotten.  This is achieved by documenting the
hardware and how it functions, thanks to the talent of programmers from the
MAME team and from other contributors.  Being able to play the games is just
a nice side-effect, which doesn't happen all the time.  MAME strives for
emulating the games faithfully.

%package tools
Summary:        Additional tools for MAME
Requires:       %{name} = %{version}-%{release}

%description tools
%{summary}.

%if %{with ldplayer}
%package ldplayer
Summary:        Standalone laserdisc player based on MAME

%description ldplayer
%{summary}.
%endif

%package -n mess
Summary:        Multi Emulator Super System
Requires:       mess-data = %{version}-%{release}

%if 0%{?fedora} < 18
Provides:       bundled(libjpeg) = 8c
%endif
Provides:       bundled(lzma-sdk) = 9.22

%description -n mess
MESS is an acronym that stands for Multi Emulator Super System. MESS will
more or less faithfully reproduce computer and console systems on a PC.

MESS emulates the hardware of the systems and sometimes utilizes ROM images to
load programs and games.  Therefore, these systems are NOT simulations, but
the actual emulations of the hardware.

%package -n mess-tools
Summary:        Additional tools for MESS
Requires:       mess = %{version}-%{release}

%description -n mess-tools
%{summary}.

%package data
Summary:        Data files used by both MAME and MESS

Provides:       mess-data = %{version}-%{release}

BuildArch:      noarch

%description data
%{summary}.

%package data-software-lists
Summary:        Software lists used by both MAME and MESS
Requires:       %{name}-data = %{version}-%{release}

Provides:       mess-data-software-lists = %{version}-%{release}
Obsoletes:      mess-data < 0.146-2

BuildArch:      noarch

%description data-software-lists
%{summary}. These are split from the main -data subpackage due to relatively
large size.


%prep
%if 0%{?svn}
%setup -qn %{name}-export
%else
%setup -qcT
for sourcefile in %{sources}; do
    7za x $sourcefile
done
sed -i '2157d' src/mess/mess.mak
find . -type f -not -name *.png -exec sed -i 's/\r//' {} \;
%if 0%{?sourceupdate}
i=1
while [ $i -le %{sourceupdate} ]; do
    patch -p0 -E < 0%{baseversion}u${i}.diff
    i=`expr $i + 1`
done
%endif
%endif
%patch0 -p1 -b .fortify
%patch2 -p1 -b .verbosebuild


# Create ini files
cat > %{name}.ini << EOF
# Define multi-user paths
artpath            %{_datadir}/%{name}/artwork;%{_datadir}/%{name}/effects
cheatpath          %{_datadir}/%{name}/cheats
ctrlrpath          %{_datadir}/%{name}/ctrlr
fontpath           %{_datadir}/%{name}/fonts
hashpath           %{_datadir}/%{name}/hash
rompath            %{_datadir}/%{name}/roms;%{_datadir}/%{name}/chds
samplepath         %{_datadir}/%{name}/samples

# Allow user to override ini settings
inipath            \$HOME/.%{name}/ini;%{_sysconfdir}/%{name}

# Set paths for local storage
cfg_directory      \$HOME/.%{name}/cfg
comment_directory  \$HOME/.%{name}/comments
diff_directory     \$HOME/.%{name}/diff
input_directory    \$HOME/.%{name}/inp
memcard_directory  \$HOME/.%{name}/memcard
nvram_directory    \$HOME/.%{name}/nvram
snapshot_directory \$HOME/.%{name}/snap
state_directory    \$HOME/.%{name}/sta

# Fedora custom defaults
video              opengl
autosave           1
EOF

#make a copy for MESS
sed 's/%{name}/mess/g' %{name}.ini > mess.ini


%build
#these flags are already included in the Makefile
RPM_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | sed -e s/"-O2 -g -pipe -Wall "//)

#save some space
MAME_FLAGS="NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 \
    BUILD_FLAC=0 SUFFIX64="

%if 0%{?fedora} >= 18
MAME_FLAGS="$MAME_FLAGS BUILD_JPEGLIB=0"
%else
MAME_FLAGS="$MAME_FLAGS BUILD_JPEGLIB=1"
%endif

%if %{with ldplayer}
make %{?_smp_mflags} $MAME_FLAGS TARGET=ldplayer \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'"
%endif
%if %{with debug}
make %{?_smp_mflags} $MAME_FLAGS DEBUG=1 \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" all
find obj -type f -not -name \*.lh -and -not -name drivlist.c -exec rm {} \;
make %{?_smp_mflags} $MAME_FLAGS DEBUG=1 TARGET=mess \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/mess;\"'" all
%else
make %{?_smp_mflags} $MAME_FLAGS \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" all
find obj -type f -not -name \*.lh -and -not -name drivlist.c -exec rm {} \;
make %{?_smp_mflags} $MAME_FLAGS TARGET=mess\
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/mess;\"'" all
%endif


%install
rm -rf $RPM_BUILD_ROOT

# create directories
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/mess
for folder in cfg comments diff ini inp memcard nvram snap sta
do
    install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/$folder
    install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.mess/$folder
done
install -d $RPM_BUILD_ROOT%{_bindir}
for folder in artwork chds cheats ctrlr effects fonts hash hlsl keymaps roms \
    samples shader
do
    install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/$folder
done
for folder in artwork chds cheats ctrlr effects fonts hash hlsl keymaps roms \
    samples shader software
do
    install -d $RPM_BUILD_ROOT%{_datadir}/mess/$folder
done
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install -d $RPM_BUILD_ROOT%{_mandir}/man6

# install files
install -pm 644 %{name}.ini $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -pm 644 mess.ini $RPM_BUILD_ROOT%{_sysconfdir}/mess
%if %{with ldplayer}
install -pm 755 ldplayer $RPM_BUILD_ROOT%{_bindir}
%endif
%if %{with debug}
install -pm 755 %{name}d $RPM_BUILD_ROOT%{_bindir}
install -pm 755 messd $RPM_BUILD_ROOT%{_bindir}
%else
install -pm 755 %{name} $RPM_BUILD_ROOT%{_bindir}
install -pm 755 mess $RPM_BUILD_ROOT%{_bindir}
%endif
install -pm 755 chdman jedutil ldresample ldverify romcmp testkeys unidasm \
    castool floptool imgtool $RPM_BUILD_ROOT%{_bindir}
#for tool in regrep runtest split src2html srcclean
for tool in regrep split src2html srcclean
do
    install -pm 755 $tool $RPM_BUILD_ROOT%{_bindir}/%{name}-$tool
done
install -pm 644 artwork/* $RPM_BUILD_ROOT%{_datadir}/%{name}/artwork
install -pm 644 hash/* $RPM_BUILD_ROOT%{_datadir}/%{name}/hash
install -pm 644 hlsl/* $RPM_BUILD_ROOT%{_datadir}/%{name}/hlsl
install -pm 644 keymaps/* $RPM_BUILD_ROOT%{_datadir}/%{name}/keymaps
pushd src/osd/sdl
install -pm 644 shader/*.?sh $RPM_BUILD_ROOT%{_datadir}/%{name}/shader
for folder in artwork hash hlsl keymaps shader
do
    pushd $RPM_BUILD_ROOT%{_datadir}/%{name}/$folder
    for i in *
    do
        ln -s ../../%{name}/$folder/$i ../../mess/$folder/$i
    done
    popd
done
pushd man
%if %{with ldplayer}
install -pm 644 ldplayer.1 $RPM_BUILD_ROOT%{_mandir}/man1
%endif
install -pm 644 chdman.1 jedutil.1 ldverify.1 romcmp.1 testkeys.1 \
    $RPM_BUILD_ROOT%{_mandir}/man1
install -pm 644 mame.6 $RPM_BUILD_ROOT%{_mandir}/man6
popd
popd


%files
%doc docs/config.txt docs/hlsl.txt docs/license.txt docs/mame.txt
%doc docs/newvideo.txt docs/nscsi.txt
%if !0%{?svn}
%doc whatsnew*.txt
%endif
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/skel/.%{name}
%if %{with debug}
%{_bindir}/%{name}d
%else
%{_bindir}/%{name}
%endif
%{_mandir}/man6/mame.6*

%files tools
%{_bindir}/chdman
%{_bindir}/jedutil
%{_bindir}/ldresample
%{_bindir}/ldverify
%{_bindir}/%{name}-regrep
%{_bindir}/romcmp
#%{_bindir}/%{name}-runtest
%{_bindir}/%{name}-split
%{_bindir}/%{name}-src2html
%{_bindir}/%{name}-srcclean
%{_bindir}/testkeys
%{_bindir}/unidasm
%{_mandir}/man1/chdman.1*
%{_mandir}/man1/jedutil.1*
%{_mandir}/man1/ldverify.1*
%{_mandir}/man1/romcmp.1*
%{_mandir}/man1/testkeys.1*

%if %{with ldplayer}
%files ldplayer
%{_bindir}/ldplayer
%{_mandir}/man1/ldplayer.1*
%endif

%files -n mess
%if !0%{?svn}
%doc messnew*.txt
%endif
%config(noreplace) %{_sysconfdir}/mess/mess.ini
%dir %{_sysconfdir}/mess
%{_sysconfdir}/skel/.mess
%if %{with debug}
%{_bindir}/messd
%else
%{_bindir}/mess
%endif

%files -n mess-tools
%doc docs/imgtool.txt
%{_bindir}/castool
%{_bindir}/floptool
%{_bindir}/imgtool

%files data
%{_datadir}/%{name}
%exclude %{_datadir}/%{name}/hash/*
%{_datadir}/mess
%exclude %{_datadir}/mess/hash/*

%files data-software-lists
%{_datadir}/%{name}/hash/*
%{_datadir}/mess/hash/*


%changelog
* Tue Apr 09 2013 Julian Sikorski <belegdol@fedoraproject.org> - 0.148u3-1
- Updated to 0.148u3

* Tue Mar 19 2013 Julian Sikorski <belegdol@fedoraproject.org> - 0.148u2-1
- Updated to 0.148u2
- Switched to the qt debugger and adjusted BR accordingly
- Made it easy to build an svn snapshot

* Mon Feb 11 2013 Julian Sikorski <belegdol@fedoraproject.org> - 0.148u1-1
- Updated to 0.148u1
- Use system libjpeg on Fedora 18 too (RH bug #854695)

* Sat Jan 12 2013 Julian Sikorski <belegdol@fedoraproject.org> - 0.148-1
- Updated to 0.148

* Mon Dec 17 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147u4-1
- Updated to 0.147u4
- Updated the lowmem workaround - the linker is not the culprit, dwz is
- BR: libjpeg-devel → libjpeg-turbo-devel
- Updated the verbosebuild patch

* Mon Nov 19 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147u3-1
- Updated to 0.147u3

* Tue Oct 30 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147u2-1
- Updated to 0.147u2
- Conditionalised the low memory workaround
- Use system libjpeg-turbo on Fedora 19 and above
- Do not delete the entire obj/, leave the bits needed by the -debuginfo package

* Sat Oct 27 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147u1-2
- Work around low memory on the RPM Fusion builder

* Mon Oct 08 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147u1-1
- Updated to 0.147u1
- Dropped missing whatsnew.txt workaround
- Fixed incorrect paths in mess.ini
- Remove the object tree between mame and mess builds to prevent mess using /etc/mame

* Fri Sep 21 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.147-1
- Updated to 0.147
- Merged with mess
- Streamlined the directories installation
- Worked around missing whatsnew.txt
- Fixed mame.6 installation location
- Re-enabled ldplayer
- Cleaned-up ancient Obsoletes/Provides

* Mon Aug 20 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146u5-1
- Updated to 0.146u5

* Mon Jul 30 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146u4-1
- Updated to 0.146u4

* Sun Jul 15 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146u3-1
- Updated to 0.146u3

* Mon Jul 02 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146u2-1
- Updated to 0.146u2

* Mon Jun 11 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146u1-1
- Updated to 0.146u1

* Tue May 22 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.146-1
- Updated to 0.146
- Added GLSL shaders to the installed files

* Mon May 07 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u8-1
- Updated to 0.145u8

* Sun Apr 22 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u7-1
- Updated to 0.145u7

* Sun Apr 08 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u6-1
- Updated to 0.154u6
- Dropped the systemlibs patch (no longer necessary)

* Sun Mar 25 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u5-1
- Updated to 0.145u5
- mame.1 → mame.6

* Sun Mar 11 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u4-1
- Updated to 0.145u4
- Updated the systemlibs patch (FLAC++ was removed)

* Mon Feb 27 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u3-1
- Updated to 0.145u3

* Sun Feb 26 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u2-1
- Updated to 0.145u2
- Re-enabled ldresample and ldverify

* Sun Feb 19 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145u1-1
- Updated to 0.145u1
- Added artwork/* and hlsl/* to the installed files
- Fixed the line ending fix to spare all the *.png files
- Added bundled(libjpeg) and bundled(lzma-sdk) Provides
- Temporarily disabled ldresample and ldverify

* Mon Feb 06 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.145-1
- Updated to 0.145
- Updated the systemlibs patch

* Mon Jan 30 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u7-1
- Updated to 0.144u7
- Dropped upstreamed gcc-4.7 patch
- Patched to use system libflac, libjpeg needs more work

* Mon Jan 16 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u6-1
- Updated to 0.144u6

* Tue Jan 10 2012 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u5-1
- Updated to 0.144u5
- Fixed building with gcc-4.7

* Sun Dec 25 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u4-1
- Updated to 0.144u4

* Wed Dec 14 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u3-1
- Updated to 0.144u3
- Dropped obsolete Group, Buildroot, %%clean and %%defattr

* Sun Dec 04 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u2-1
- Updated to 0.144u2

* Sun Nov 27 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144u1-1
- Updated to 0.144u1

* Tue Nov 15 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.144-1
- Updated to 0.144
- Fixed whatsnew.txt encoding (cp1252 → utf-8)
- Updated Source0 URL

* Thu Oct 27 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u9-1
- Updated to 0.143u9

* Sun Oct 23 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u8-1
- Updated to 0.143u8

* Tue Oct 11 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u7-1
- Updated to 0.143u7

* Thu Sep 22 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u6-1
- Updated to 0.143u6
- Dropped upstreamed stacksmash patch

* Tue Sep 06 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u5-1
- Updated to 0.143u5
- Fixed stack smash in m68kmake.c

* Thu Aug 25 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u4-1
- Updated to 0.143u4

* Mon Aug 15 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u3-1
- Updated to 0.143u3

* Wed Jul 27 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u2-1
- Updated to 0.143u2

* Fri Jul 15 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143u1-1
- Updated to 0.143u1

* Wed Jun 29 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.143-1
- Updated to 0.143

* Sun Jun 19 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u6-1
- Updated to 0.142u6

* Mon Jun 06 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u5-1
- Updated to 0.142u5

* Tue May 24 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u4-1
- Updated to 0.142u4

* Sun May 08 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u3-1
- Updated to 0.142u3
- Disabled ldplayer

* Mon Apr 25 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u2-1
- Updated to 0.142u2

* Tue Apr 19 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142u1-1
- Updated to 0.142u1
- Updated the verbosebuild patch

* Sun Apr 03 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.142-1
- Updated to 0.142

* Fri Mar 25 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141u4-1
- Updated to 0.141u4
- Re-enabled ldplayer
- Added support for hash files
- Sorted the %%install section alphabetically

* Mon Feb 28 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141u3-1
- Updated to 0.141u3
- Filtered out redundant $RPM_OPT_FLAGS
- No longer enable joystick by default
- Provided an easy way to disable ldplayer
- Dropped upstreamed gcc-4.6 patch

* Wed Feb 09 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141u2-1
- Updated to 0.141u2

* Mon Jan 24 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141u1-1
- Updated to 0.141u1
- Re-enabled the fortify patch
- Fixed building with gcc-4.6

* Thu Jan 13 2011 Julian Sikorski <belegdol@fedoraproject.org> - 0.141-1
- Updated to 0.141
- Temporarily dropped the fortify patch

* Thu Dec 09 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.140u2-1
- Updated to 0.140u2
- Added SDL_ttf-devel to BuildRequires, removed explicit SDL-devel

* Mon Nov 08 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.140u1-1
- Updated to 0.140u1

* Thu Oct 21 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.140-1
- Updated to 0.140
- Re-enabled ldplayer

* Sat Oct 16 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139u4-1
- Updated to 0.139u4

* Thu Oct 14 2010 Nicolas Chauvet <kwizart@gmail.com> - 0.139u3-2
- Rebuilt for gcc bug

* Sun Sep 19 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139u3-1
- Updated to 0.139u3
- Updated the verbosebuild patch

* Tue Aug 31 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139u2-1
- Updated to 0.139u2

* Fri Aug 13 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139u1-1
- Updated to 0.139u1

* Thu Jul 29 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.139
- Updated to 0.139

* Thu Jul 22 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138u4-1
- Updated to 0.138u4
- Install the new manpages

* Thu Jul 08 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138u3-1
- Updated to 0.138u3
- Updated the verbosebuild patch
- Disabled ldplayer since it does not build ATM (mametesters #3930)

* Thu Jun 17 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138u2-1
- Updated to 0.138u2
- Adjusted the license tag - it concerns the binary, not the source

* Fri May 28 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138u1-1
- Updated to 0.138u1

* Sun May 16 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.138-1
- Updated to 0.138

* Wed May 05 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137u4-1
- Updated to 0137u4

* Thu Apr 22 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137u3-1
- Updated to 0137u3
- Dropped upstreamed ppc64 patch
- Moved rpm patches application after upstream ones

* Fri Apr 09 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137u2-1
- Updated to 0137u2

* Sun Mar 21 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137-4
- Stripped @ from the commands to make the build more verbose

* Sun Mar 21 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137-3
- Dropped suffix64
- Added ppc64 autodetection support
- Re-diffed the fortify patch

* Sat Mar 20 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0.137-2
- Changed the versioning scheme to include the dot
- Changed the source URL to point to aarongiles.com mirror directly
- Added missing application of the fortify patch
- Added sparc64 and s390 to architectures getting suffix64
- Removed duplicate license.txt

* Thu Mar 11 2010 Julian Sikorski <belegdol@fedoraproject.org> - 0137-1
- Initial package based on sdlmame
