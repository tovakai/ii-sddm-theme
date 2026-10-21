"""Unit tests for ii-sddm-theme's least-privilege synchronization logic."""
import importlib.machinery
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "secure-sync/ii-sddm-theme-sync"
module = types.ModuleType("ii_sddm_sync")
importlib.machinery.SourceFileLoader("ii_sddm_sync", str(MODULE_PATH)).exec_module(module)


class SyncTests(unittest.TestCase):
    def test_config_background_paths_stay_inside_theme(self):
        conf = '[General]\nBackground="Backgrounds/old.png"\nBackgroundPlaceholder=""\n'
        result = module.replace_background(conf, "background.jpg", False)
        self.assertIn('Background="Backgrounds/background.jpg"', result)
        self.assertIn('BackgroundPlaceholder=""', result)
        result = module.replace_background(conf, "background.mp4", True)
        self.assertIn('BackgroundPlaceholder="Backgrounds/placeholder.png"', result)

    def test_rejects_missing_config_keys(self):
        with self.assertRaises(RuntimeError):
            module.replace_background("[General]\n", "background.png", False)

    def test_wallpaper_selection_prefers_ii_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            folder = home / ".config/ii-sddm-theme"
            folder.mkdir(parents=True)
            settings = 'QtObject {\n property string background_wallpaperPath: "' + str(home / "wall paper.png") + '"\n}'
            colors = "// nothing\n" * 5
            self.assertEqual(module.wallpaper_from_sources(home, folder, settings, colors), home / "wall paper.png")

    def test_wallpaper_selection_supports_matugen_header(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            folder = home / ".config/ii-sddm-theme"
            folder.mkdir(parents=True)
            colors = 'import QtQuick\npragma Singleton\n\n// matugen\n// ~/Pictures/bg.png\nQtObject {}\n'
            self.assertEqual(module.wallpaper_from_sources(home, folder, "", colors), home / "Pictures/bg.png")

    def test_refuses_other_users_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "source.qml"
            path.write_text("dummy")
            self.assertEqual(module.read_owned(path, os.getuid(), 200), b"dummy")
            with self.assertRaises(RuntimeError):
                module.read_owned(path, os.getuid() + 1, 200)
            link = root / "link.qml"
            link.symlink_to(path)
            with self.assertRaises(OSError):
                module.read_owned(link, os.getuid(), 200)

    def test_atomic_write_does_not_follow_destination_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            victim = root / "victim"
            victim.write_bytes(b"leave-me-alone")
            target = root / "target"
            target.symlink_to(victim)
            with mock.patch.object(module, "checked_directory", lambda _: None):
                module.atomic_write(target, b"new-theme")
            self.assertEqual(victim.read_bytes(), b"leave-me-alone")
            self.assertFalse(target.is_symlink())
            self.assertEqual(target.read_bytes(), b"new-theme")

    def test_full_image_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            src = home / ".config/ii-sddm-theme"
            src.mkdir(parents=True)
            theme = Path(directory) / "theme"
            for name in ["Components", "Backgrounds", "Themes"]:
                (theme / name).mkdir(parents=True)
            wall = home / "cool wallpaper.jpg"
            wall.write_bytes(b"test-image")
            (src / "Colors.qml").write_text("import QtQuick\n")
            (src / "Settings.qml").write_text('property string background_wallpaperPath: "' + str(wall) + '"\n')
            (src / "ii-sddm.conf").write_text('[General]\nBackgroundPlaceholder=""\nBackground="Backgrounds/background.png"\n')
            with mock.patch.object(module, "caller", return_value=(os.getuid(), home)), \
                 mock.patch.object(module, "DEST", theme), \
                 mock.patch.object(module, "checked_directory", lambda _: None), \
                 mock.patch.object(module.sys, "argv", ["ii-sddm-theme-sync"]):
                module.main()
            self.assertEqual((theme / "Backgrounds/background.jpg").read_bytes(), b"test-image")
            self.assertIn('Background="Backgrounds/background.jpg"',
                          (theme / "Themes/ii-sddm.conf").read_text())


if __name__ == "__main__":
    unittest.main()
