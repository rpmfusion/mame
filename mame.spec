# ldplayer can be disabled by --without ldplayer or by changing to %bcond_with
# if it does not build. The debug build is disabled by default, please use
# --with debug to override
%bcond_with ldplayer
%bcond_with debug

%global baseversion 145
%global sourceupdate 5

Name:           mame
%if 0%{?sourceupdate}
Version:        0.%{baseversion}u%{sourceupdate}
%else
Version:        0.%{baseversion}
%endif
Release:        1%{?dist}
Summary:        Multiple Arcade Machine Emulator

#Files in src/lib/util and src/osd (except src/osd/sdl) are BSD
License:        MAME License
URL:            http://mamedev.org/
Source0:        http://mamedev.org/downloader.php?file=releases/%{name}0%{baseversion}s.exe
%if 0%{?sourceupdate}
#Source updates
Source1:        http://mamedev.org/updates/0%{baseversion}u1_diff.zip
Source2:        http://mamedev.org/updates/0%{baseversion}u2_diff.zip
Source3:        http://mamedev.org/updates/0%{baseversion}u3_diff.zip
Source4:        http://mamedev.org/updates/0%{baseversion}u4_diff.zip
Source5:        http://mamedev.org/updates/0%{baseversion}u5_diff.zip
#Source6:        http://mamedev.org/updates/0%{baseversion}u6_diff.zip
#Source7:        http://mamedev.org/updates/0%{baseversion}u7_diff.zip
#Source8:        http://mamedev.org/updates/0%{baseversion}u8_diff.zip
#Source9:        http://mamedev.org/updates/0%{baseversion}u9_diff.zip
%endif
Patch0:         %{name}-fortify.patch
Patch1:         %{name}-systemlibs.patch
Patch2:         %{name}-verbosebuild.patch

BuildRequires:  expat-devel
BuildRequires:  flac-devel
BuildRequires:  GConf2-devel
BuildRequires:  gtk2-devel
# BuildRequires:  libjpeg-devel
BuildRequires:  p7zip
BuildRequires:  SDL_ttf-devel
BuildRequires:  zlib-devel

Provides:       sdlmame = 0%{baseversion}-%{release}
Provides:       bundled(libjpeg) = 8c
Provides:       bundled(lzma-sdk) = 9.22
Obsoletes:      sdlmame < 0136-2

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
Summary:        Tools used for the MAME package
Group:          Applications/Emulators
Requires:       %{name} = %{version}-%{release}

Provides:       sdlmame-tools = 0%{baseversion}-%{release}
Obsoletes:      sdlmame-tools < 0136-2

%description tools
%{summary}.

%if %{with ldplayer}
%package ldplayer
Summary:        Standalone laserdisc player based on MAME
Group:          Applications/Emulators

Provides:       sdlmame-ldplayer = 0%{baseversion}-%{release}
Obsoletes:      sdlmame-ldplayer < 0136-2

%description ldplayer
%{summary}.
%endif


%prep
%setup -qcT
for sourcefile in %{sources}; do
    7za x $sourcefile
done
find . -type f -not -name *.png -exec sed -i 's/\r//' {} \;
%if 0%{?sourceupdate}
i=1
while [ $i -le %{sourceupdate} ]; do
    patch -p0 -E < 0%{baseversion}u${i}.diff
    i=`expr $i + 1`
done
%endif
%patch0 -p1 -b .fortify
%patch1 -p1 -b .systemlibs
%patch2 -p1 -b .verbosebuild


# Create ini file
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


%build
#these flags are already included in the Makefile
RPM_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | sed -e s/"-O2 -g -pipe -Wall "//)

%if %{with ldplayer}
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 \
    BUILD_JPEG=1 BUILD_FLAC=0 SUFFIX64="" TARGET=ldplayer \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'"
%endif
%if %{with debug}
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 \
    BUILD_JPEG=1 BUILD_FLAC=0 SUFFIX64="" DEBUG=1 \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" all
%else
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 \
    BUILD_JPEG=1 BUILD_FLAC=0 SUFFIX64="" \
    OPT_FLAGS="$RPM_OPT_FLAGS -DINI_PATH='\"%{_sysconfdir}/%{name};\"'" all
%endif


%install
rm -rf $RPM_BUILD_ROOT

# create directories
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/cfg
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/comments
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/diff
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/ini
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/inp
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/memcard
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/nvram
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/snap
install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel/.%{name}/sta
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/artwork
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/chds
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/cheats
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/ctrlr
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/effects
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/fonts
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/hash
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/hlsl
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/keymaps
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/roms
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/samples
install -d $RPM_BUILD_ROOT%{_mandir}/man1

# install files
install -pm 644 %{name}.ini $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
%if %{with ldplayer}
install -pm 755 ldplayer $RPM_BUILD_ROOT%{_bindir}
%endif
%if %{with debug}
install -pm 755 %{name}d $RPM_BUILD_ROOT%{_bindir}
%else
install -pm 755 %{name} $RPM_BUILD_ROOT%{_bindir}
%endif
install -pm 755 chdman jedutil ldresample ldverify \
    romcmp testkeys unidasm $RPM_BUILD_ROOT%{_bindir}
#for tool in regrep runtest split src2html srcclean
for tool in regrep split src2html srcclean
do
install -pm 755 $tool $RPM_BUILD_ROOT%{_bindir}/%{name}-$tool
done
install -pm 644 artwork/* $RPM_BUILD_ROOT%{_datadir}/%{name}/artwork
install -pm 644 hash/* $RPM_BUILD_ROOT%{_datadir}/%{name}/hash
install -pm 644 hlsl/* $RPM_BUILD_ROOT%{_datadir}/%{name}/hlsl
install -pm 644 src/osd/sdl/keymaps/* $RPM_BUILD_ROOT%{_datadir}/%{name}/keymaps
pushd src/osd/sdl/man
%if %{with ldplayer}
install -pm 644 ldplayer.1 $RPM_BUILD_ROOT%{_mandir}/man1
%endif
install -pm 644 chdman.1 jedutil.1 ldverify.1 mame.6 romcmp.1 \
    testkeys.1 $RPM_BUILD_ROOT%{_mandir}/man1
popd


%files
%doc docs/* whatsnew*.txt
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/skel/.%{name}
%if %{with debug}
%{_bindir}/%{name}d
%else
%{_bindir}/%{name}
%endif
%{_datadir}/%{name}
%{_mandir}/man1/mame.6*

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


%changelog
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
