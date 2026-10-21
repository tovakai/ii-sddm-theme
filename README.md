# ii-sddm-theme

https://github.com/user-attachments/assets/a03e1628-3438-4390-bb62-96e18308a8e0

## Overview

[ii-sddm-theme](https://github.com/tovakai/ii-sddm-theme) is a custom theme for the [SDDM](https://github.com/sddm/sddm/) display manager that tries to replicate the lockscreen aesthetic and settings of [illogical impulse](https://github.com/end-4/dots-hyprland). It can be used with ii dotfiles, with [Matugen](https://github.com/InioX/matugen) only, or as a standalone theme.

I only have a basic understanding of Qt QML, so this project is a learning experience and mostly about piecing together code from various sources while figuring things out along the way. I also get a ton of help from ai models.

**Currently supports:** Arch Linux + Hyprland, to be extended

---

## Acknowledgements

This theme wouldn't exist without these projects:

- **[illogical impulse](https://github.com/end-4/dots-hyprland)** – All the widgets code, the design and the creativeness comes from [end-4](https://github.com/end-4) repo
- **[win11-sddm-theme](https://github.com/syrupderg/win11-sddm-theme)** – An amazing win 11 sddm theme, which i used for the waffle implementation
- **[sddm-astronaut-theme](https://github.com/Keyitdev/sddm-astronaut-theme)** – The starting point for this theme
- **[SilentSDDM](https://github.com/uiriansan/SilentSDDM)** – Custom virtual keyboard implementation and various improvements
- **[matugen](https://github.com/InioX/matugen)** - Material You color palette generator
- **[qt/qtvirtualkeyboard](https://github.com/qt/qtvirtualkeyboard)** – Default virtual keyboard style template

---

## Features

Depending on your setup, you can choose from one to three different installation modes:

### ii + Matugen Integration
Settings, wallpaper, and colors automatically synced from ii configuration

<p align="left">
  <img src="https://github.com/3d3f/ii-sddm-theme/raw/main/Previews/iiMatugen-preview.png" width="50%" alt="ii + Matugen" />
</p>

### Matugen Integration Only
Wallpaper and colors generated via Matugen, with manual settings configuration

<p align="left">
  <img src="https://github.com/3d3f/ii-sddm-theme/raw/main/Previews/Matugen-preview.png" width="50%" alt="Matugen Only" />
</p>

### No Matugen Integration
Manually configure your background, colors, and settings

<p align="left">
  <img src="https://github.com/3d3f/ii-sddm-theme/raw/main/Previews/noMatugen-preview.png" width="50%" alt="Manual Configuration" />
</p>

---

## Installation

### Install from this fork

Read the script before running it. Run it as your regular user, **not** with `sudo bash`:

```bash
git clone https://github.com/tovakai/ii-sddm-theme.git
cd ii-sddm-theme
bash ./setup.sh
```

The installer uses the **current local checkout**, including any checked-out fix branch. When run without a local checkout, it clones this fork rather than the upstream repository.

The installer installs SDDM and its dependencies on Arch, but **does not silently change your display manager**. If another manager is active, you must type `SWITCH` to replace it. The installer prints how to restore the previous manager. Before rebooting, preview the greeter:

```bash
sddm-greeter-qt6 --test-mode --theme /usr/share/sddm/themes/ii-sddm-theme
```

### Automatic synchronization and security

For `ii + Matugen` and `Matugen-only` modes, the Matugen post-hook runs the settings generator (when applicable) and a normal-user wrapper at:

```bash
~/.config/ii-sddm-theme/sddm-theme-apply.sh
```

You can run the wrapper manually after editing the SDDM settings or changing a wallpaper. Do **not** run it with sudo.

The original upstream installer allowed passwordless root execution of that user-writable script. This fork removes that rule. Instead:

- A small Python synchronization helper is installed as **root-owned** `/usr/local/libexec/ii-sddm-theme-sync`.
- Sudoers permits that **exact program, with no arguments**, for the installing user. The wrapper uses `sudo -n` so background hooks never hang on a password prompt.
- The helper does not run shell commands or user-provided scripts. It copies only caller-owned regular files into fixed locations inside the root-owned SDDM theme. It checks source size/ownership and destination directory permissions, and uses atomic replacements.
- Video wallpaper thumbnails are produced by FFmpeg **as your regular user**, not root.
- The installer reports sync errors instead of claiming success and overwrites the legacy unsafe sudoers rule during upgrades.

**Security boundary:** SDDM loads the generated QML in its greeter. Anyone who can modify those assets may affect the login UI, even without root access. This integration is intended for a trusted single-user desktop; don't allow untrusted users to write the synchronized QML. The wallpaper file must be owned by the installing user (copy system-owned wallpapers into your home directory first). The helper currently caps wallpapers at 512 MiB.

### Post-installation

Consult `~/.config/ii-sddm-theme/GUIDE.TXT` for the selected mode. Run `bash ./check.sh` to check the installation.

### Uninstallation

From a local checkout, as your regular user:

```bash
bash ./uninstall.sh
```

This removes the theme, configuration, fonts, Matugen integration, sudoers rule, and fixed helper. It does **not** automatically switch your display manager back; consult the rollback command printed during setup. A reboot may be necessary.

---

## Cursor theme
This example is made with [Bibata Modern Classic](https://github.com/ful1e5/Bibata_Cursor), but you can use any cursor theme.
This workaround worked for me but may not work for everybody.

### Install the cursor theme package (if you use ii you have it already)
```bash
yay -S bibata-cursor-theme-bin
```

### Workaround 
Backup and then edit `/usr/share/icons/default/index.theme`:
```bash
sudo nano /usr/share/icons/default/index.theme
```
Change or add these lines:
```ini
[Icon Theme]
Inherits=Bibata-Modern-Classic
```

---

## Issues & Questions

For issues with this fork, please [open an issue](https://github.com/tovakai/ii-sddm-theme/issues).