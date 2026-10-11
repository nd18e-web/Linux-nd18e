#!/bin/bash
# ND18E Linux - czysty, lekki system: pulpit LXQt (pasek + menu Start z ikona "N"), intro "N" przy starcie,
# Konfiguracja sprzetu (GTX 1050 Ti + i5-7400), Menedzer zadan, Sklep z aplikacjami (Flathub), dzwieki i animacje.
# Nic wiecej nie jest zainstalowane - aplikacje instalujesz sam ze Sklepu.
# Wymagania: Debian 12/Ubuntu 22.04+ (np. VirtualBox: 8 GB RAM, 40 GB dysku, internet).
# Obok skryptu musza lezec: nd18e-taskmgr.py, nd18e-store.py, nd18e-setup.py
# Uzycie: chmod +x build_nd18e_linux.sh && ./build_nd18e_linux.sh   -> ND18E_Linux.iso
set -e
for f in nd18e-taskmgr.py nd18e-store.py nd18e-setup.py; do
  [ -f "$f" ] || { echo "Brak pliku $f obok skryptu"; exit 1; }
done
sudo apt-get update
sudo apt-get install -y live-build sox wget debootstrap

rm -rf nd18e_build && mkdir nd18e_build && cd nd18e_build

lb config --distribution bookworm --architectures amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --apt-recommends false \
  --debian-installer none --binary-images iso-hybrid \
  --iso-application "ND18E Linux" --iso-volume ND18E --memtest none \
  --bootappend-live "boot=live components quiet splash locales=pl_PL.UTF-8 keyboard-layouts=pl timezone=Europe/Warsaw"

C=config/includes.chroot
mkdir -p config/package-lists config/hooks/normal $C/etc/skel/Desktop $C/etc/skel/.config/lxqt \
  $C/etc/skel/.config/pcmanfm-qt/lxqt $C/etc/xdg/autostart $C/usr/share/sounds/nd18e \
  $C/usr/share/plymouth/themes/nd18e $C/usr/local/bin $C/usr/share/applications $C/usr/share/icons/nd18e

# ---------- Pakiety: tylko podstawa systemu ----------
cat > config/package-lists/nd18e.list.chroot <<'EOF'
lxqt-core lxqt-config lxqt-policykit lxqt-themes lightdm lightdm-gtk-greeter openbox picom
pcmanfm-qt qterminal featherpad
network-manager network-manager-gnome pipewire-audio pipewire-pulse wireplumber pulseaudio-utils pavucontrol-qt
python3 python3-tk python3-psutil pciutils usbutils
flatpak xdg-desktop-portal-gtk
mesa-vulkan-drivers libgl1-mesa-dri vulkan-tools linux-headers-amd64 dkms
firmware-linux firmware-misc-nonfree firmware-realtek firmware-iwlwifi
fonts-noto fonts-dejavu imagemagick plymouth plymouth-themes calamares calamares-settings-debian sudo
EOF

# ---------- Programy ND18E ----------
for a in taskmgr store setup; do cp ../nd18e-$a.py $C/usr/local/bin/nd18e-$a; chmod +x $C/usr/local/bin/nd18e-$a; done
mk() { # nazwa, polecenie, ikona
  cat > $C/usr/share/applications/$1.desktop <<EOF
[Desktop Entry]
Type=Application
Name=$2
Exec=$3
Icon=$4
Categories=System;
EOF
  cp $C/usr/share/applications/$1.desktop $C/etc/skel/Desktop/
}
mk nd18e-taskmgr "Menedzer zadan" nd18e-taskmgr utilities-system-monitor
mk nd18e-store "Sklep z aplikacjami" nd18e-store system-software-install
mk nd18e-setup "Konfiguracja systemu" nd18e-setup preferences-system
cat > $C/etc/xdg/autostart/nd18e-setup.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E Konfiguracja (pierwsze uruchomienie)
Exec=nd18e-setup --first-run
NoDisplay=true
EOF

# ---------- Ikona "N" (menu Start) ----------
cat > $C/usr/share/icons/nd18e/n.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect x="2" y="2" width="60" height="60" rx="14" fill="#0a0506" stroke="#e11d2e" stroke-width="3"/>
<path d="M19 47 V17 L45 47 V17" fill="none" stroke="#e11d2e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF

# ---------- Dzwieki ----------
S=$C/usr/share/sounds/nd18e
sox -n -r 44100 -c 2 /tmp/n1.wav synth 0.35 sine 392 fade h 0.02 0.35 0.25 vol 0.5
sox -n -r 44100 -c 2 /tmp/n2.wav synth 0.35 sine 494 fade h 0.02 0.35 0.25 vol 0.5
sox -n -r 44100 -c 2 /tmp/n3.wav synth 1.2 sine 587 sine 784 fade h 0.02 1.2 1.0 vol 0.45
sox /tmp/n1.wav /tmp/n2.wav /tmp/n3.wav $S/startup.wav reverb
sox -n -r 44100 -c 2 $S/done.wav synth 0.12 sine 880 : synth 0.25 sine 1175 fade h 0.01 0.25 0.2 vol 0.5 2>/dev/null || \
  sox -n -r 44100 -c 2 $S/done.wav synth 0.3 sine 1000 fade h 0.01 0.3 0.25 vol 0.5
cat > $C/etc/xdg/autostart/nd18e-sound.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E startup sound
Exec=paplay /usr/share/sounds/nd18e/startup.wav
NoDisplay=true
EOF

# ---------- Intro przy starcie: czerwone "N" (Plymouth) ----------
P=$C/usr/share/plymouth/themes/nd18e
cat > $P/nd18e.plymouth <<'EOF'
[Plymouth Theme]
Name=ND18E
Description=ND18E Linux
ModuleName=script
[script]
ImageDir=/usr/share/plymouth/themes/nd18e
ScriptFile=/usr/share/plymouth/themes/nd18e/nd18e.script
EOF
cat > $P/nd18e.script <<'EOF'
Window.SetBackgroundTopColor(0.03, 0.01, 0.02);
Window.SetBackgroundBottomColor(0.22, 0.02, 0.05);
n = Image.Text("N", 0.90, 0.10, 0.16, 1, "Sans Bold 150");
g = Image.Text("N", 0.90, 0.10, 0.16, 0.35, "Sans Bold 190");
sn = Sprite(n);
sg = Sprite(g);
cx = Window.GetWidth() / 2;
cy = Window.GetHeight() / 2;
sn.SetX(cx - n.GetWidth() / 2);
sn.SetY(cy - n.GetHeight() / 2);
sg.SetX(cx - g.GetWidth() / 2);
sg.SetY(cy - g.GetHeight() / 2);
t = 0;
fun refresh() {
  t++;
  a = 0.5 + 0.5 * Math.Sin(t / 14);
  sg.SetOpacity(0.2 + 0.5 * a);
  sn.SetOpacity(0.75 + 0.25 * a);
}
Plymouth.SetRefreshFunction(refresh);
EOF

# ---------- Wyglad i animacje: ciemny motyw, panel z ikona N, kompozytor (cienie, zanikanie okien) ----------
cat > $C/etc/skel/.config/lxqt/lxqt.conf <<'EOF'
[General]
theme=dark
EOF
cat > $C/etc/skel/.config/lxqt/panel.conf <<'EOF'
[General]
__userfile__=true
[panel1]
alignment=-1
desktop=0
iconSize=26
panelSize=44
position=Bottom
plugins=mainmenu, showdesktop, taskbar, tray, worldclock
[mainmenu]
alignment=Left
type=mainmenu
ownIcon=true
icon=/usr/share/icons/nd18e/n.svg
[showdesktop]
alignment=Left
type=showdesktop
[taskbar]
alignment=Left
type=taskbar
[tray]
alignment=Right
type=tray
[worldclock]
alignment=Right
type=worldclock
EOF
cat > $C/etc/skel/.config/pcmanfm-qt/lxqt/settings.conf <<'EOF'
[Desktop]
Wallpaper=/usr/share/backgrounds/nd18e.png
WallpaperMode=stretch
EOF
cat > $C/etc/xdg/picom.conf <<'EOF'
backend = "glx";
vsync = true;
shadow = true;
shadow-radius = 16;
shadow-opacity = 0.55;
shadow-offset-x = -12;
shadow-offset-y = -10;
fading = true;
fade-in-step = 0.06;
fade-out-step = 0.07;
EOF
cat > $C/etc/xdg/autostart/nd18e-picom.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E compositor
Exec=picom
NoDisplay=true
EOF
cat > $C/etc/skel/Desktop/install.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Zainstaluj ND18E Linux
Exec=sudo calamares
Icon=system-software-install
EOF
chmod +x $C/etc/skel/Desktop/*.desktop

# ---------- Hook: sterowniki (GTX 1050 Ti, i5-7400), Flathub, odchudzanie ----------
cat > config/hooks/normal/0100-nd18e.hook.chroot <<'EOF'
#!/bin/bash
mkdir -p /usr/share/backgrounds
convert -size 1920x1080 gradient:'#0a0506-#5a0a14' -gravity center -font DejaVu-Sans-Bold \
  -pointsize 420 -fill '#e11d2e44' -annotate 0 'N' /usr/share/backgrounds/nd18e.png || true
plymouth-set-default-theme nd18e || true
sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME="ND18E Linux"/;s/^NAME=.*/NAME="ND18E Linux"/' /etc/os-release
# Sterownik NVIDIA (seria Pascal, GTX 1050 Ti) i mikrokod Intela (i5-7400)
apt-get install -y nvidia-driver intel-microcode || true
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true
# Mniej procesow w tle
for s in ModemManager bluetooth avahi-daemon cups cups-browsed ssh cron anacron rsyslog e2scrub_all.timer fstrim.timer apt-daily.timer apt-daily-upgrade.timer man-db.timer; do
  systemctl disable "$s" 2>/dev/null || true; systemctl mask "$s" 2>/dev/null || true
done
update-initramfs -u || true
EOF
chmod +x config/hooks/normal/0100-nd18e.hook.chroot

sudo lb build
cp live-image-amd64.hybrid.iso ../ND18E_Linux.iso
echo "Gotowe: ND18E_Linux.iso"
