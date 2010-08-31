# the debug build is disabled by default, please use --with debug to override
%bcond_with debug

%global baseversion 139
%global sourceupdate 2

Name:           mame
%if 0%{?sourceupdate}
Version:        0.%{baseversion}u%{sourceupdate}
%else
Version:        0.%{baseversion}
%endif
Release:        1%{?dist}
Summary:        Multiple Arcade Machine Emulator

Group:          Applications/Emulators
#Files in src/lib/util and src/osd (except src/osd/sdl) are BSD
License:        MAME License
URL:            http://mamedev.org/
Source0:        http://www.aarongiles.com/mirror/releases/%{name}0%{baseversion}s.exe
#ui.bdc generated from ui.bdf
#Source1:        ui.bdc
%if 0%{?sourceupdate}
#Source updates
Source1:        http://mamedev.org/updates/0%{baseversion}u1_diff.zip
Source2:        http://mamedev.org/updates/0%{baseversion}u2_diff.zip
#Source3:        http://mamedev.org/updates/0%{baseversion}u3_diff.zip
#Source4:        http://mamedev.org/updates/0%{baseversion}u4_diff.zip
%endif
Patch0:         %{name}-fortify.patch
Patch2:         %{name}-verbosebuild.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  expat-devel
BuildRequires:  GConf2-devel
BuildRequires:  gtk2-devel
BuildRequires:  p7zip
BuildRequires:  SDL-devel
BuildRequires:  zlib-devel

Provides:       sdlmame = 0%{baseversion}-%{release}
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

#%package ldplayer
#Summary:        Standalone laserdisc player based on MAME
#Group:          Applications/Emulators

#Provides:       sdlmame-ldplayer = 0%{baseversion}-%{release}
#Obsoletes:      sdlmame-ldplayer < 0136-2

#%description ldplayer
#%{summary}.


%prep
%setup -qcT
for sourcefile in %{sources}; do
    7za x $sourcefile
done
find . -type f -not -name uismall.png -exec sed -i 's/\r//' {} \;
%if 0%{?sourceupdate}
i=1
while [ $i -le %{sourceupdate} ]; do
    patch -p0 -E < 0%{baseversion}u${i}.diff
    i=`expr $i + 1`
done
%endif
%patch0 -p1 -b .fortify
%patch2 -p1 -b .verbosebuild

# Create ini file
cat > %{name}.ini << EOF
# Define multi-user paths
artpath            %{_datadir}/%{name}/artwork;%{_datadir}/%{name}/effects
ctrlrpath          %{_datadir}/%{name}/ctrlr
fontpath           %{_datadir}/%{name}/fonts
rompath            %{_datadir}/%{name}/roms;%{_datadir}/%{name}/chds
samplepath         %{_datadir}/%{name}/samples
cheatpath          %{_datadir}/%{name}/cheats

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
joystick           1
EOF


%build
#make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
#    OPT_FLAGS='%{optflags} -DINI_PATH="\"%{_sysconfdir}/%{name};\""' TARGET=ldplayer
%if %{with debug}
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS='%{optflags} -DINI_PATH="\"%{_sysconfdir}/%{name};\""' DEBUG=1 all
%else
make %{?_smp_mflags} NOWERROR=1 SYMBOLS=1 OPTIMIZE=2 BUILD_EXPAT=0 BUILD_ZLIB=0 SUFFIX64="" \
    OPT_FLAGS='%{optflags} -DINI_PATH="\"%{_sysconfdir}/%{name};\""' all
%endif


%install
rm -rf %{buildroot}

# create directories
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/%{name}/artwork
install -d %{buildroot}%{_datadir}/%{name}/chds
install -d %{buildroot}%{_datadir}/%{name}/ctrlr
install -d %{buildroot}%{_datadir}/%{name}/effects
install -d %{buildroot}%{_datadir}/%{name}/fonts
install -d %{buildroot}%{_datadir}/%{name}/keymaps
install -d %{buildroot}%{_datadir}/%{name}/roms
install -d %{buildroot}%{_datadir}/%{name}/samples
install -d %{buildroot}%{_datadir}/%{name}/cheats
install -d %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/cfg
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/comments
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/diff
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/ini
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/inp
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/memcard
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/nvram
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/snap
install -d %{buildroot}%{_sysconfdir}/skel/.%{name}/sta

# install binaries and config files
install -pm 644 %{name}.ini %{buildroot}%{_sysconfdir}/%{name}
install -pm 644 src/osd/sdl/keymaps/* %{buildroot}%{_datadir}/%{name}/keymaps
#install -pm 644 ui.bdf %{SOURCE2} %{buildroot}%{_datadir}/%{name}/fonts
%if %{with debug}
install -pm 755 %{name}d %{buildroot}%{_bindir}
%else
install -pm 755 %{name} %{buildroot}%{_bindir}
%endif
install -pm 755 chdman jedutil ldresample ldverify \
    romcmp testkeys unidasm %{buildroot}%{_bindir}
#for tool in regrep runtest split src2html srcclean
for tool in regrep split src2html srcclean
do
install -pm 755 $tool %{buildroot}%{_bindir}/%{name}-$tool
done
pushd src/osd/sdl/man
install -pm 644 chdman.1 jedutil.1 ldverify.1 mame.1 romcmp.1 \
    testkeys.1 %{buildroot}%{_mandir}/man1
popd


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc docs/* whatsnew*.txt
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.ini
%dir %{_sysconfdir}/%{name}
%if %{with debug}
%{_bindir}/%{name}d
%else
%{_bindir}/%{name}
%endif
%{_datadir}/%{name}
%{_mandir}/man1/mame.1*
%{_sysconfdir}/skel/.%{name}

%files tools
%defattr(-,root,root,-)
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

#%files ldplayer
#%defattr(-,root,root,-)
#%{_bindir}/ldplayer
#%{_mandir}/man1/ldplayer.1*


%changelog
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
