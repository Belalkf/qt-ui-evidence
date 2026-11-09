import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from qt_ui_evidence.cli import main
from qt_ui_evidence.install import RESOURCE_FILES, install_skill


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def test_self_contained_install_and_existing_install_preserved(self):
        destination = self.folder / 'project/.agents/skills/qt-ui-evidence'
        self.assertEqual(install_skill(destination), destination)
        for name in RESOURCE_FILES:
            self.assertTrue((destination/name).is_file(), name)
        original = (destination/'SKILL.md').read_bytes()
        (destination/'local-note').write_text('keep')
        with self.assertRaises(FileExistsError):
            install_skill(destination)
        self.assertEqual((destination/'SKILL.md').read_bytes(), original)
        self.assertEqual((destination/'local-note').read_text(), 'keep')
        self.assertFalse(list(destination.parent.glob('.qt-ui-evidence-*')))

    def test_existing_file_or_symlink_preserved(self):
        existing = self.folder/'existing'
        existing.write_text('preserve')
        link = self.folder/'link'
        try:
            link.symlink_to(existing)
        except OSError:
            link = None  # Windows may prohibit creating links in this environment.
        for target in (existing, link):
            if target is None:
                continue
            with self.assertRaises(FileExistsError):
                install_skill(target)
        self.assertEqual(existing.read_text(), 'preserve')
        if link is not None:
            self.assertTrue(link.is_symlink())

    def test_resource_failure_leaves_destination_uncreated(self):
        destination = self.folder/'skill'
        with patch('qt_ui_evidence.install.resources.files', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):
                install_skill(destination)
        self.assertFalse(destination.exists())

    def test_explicit_project_install_cli(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['install-skill', '--project', str(self.folder)]), 0)
        self.assertTrue((self.folder/'.agents/skills/qt-ui-evidence/SKILL.md').exists())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['install-skill', '--project', str(self.folder)]), 2)

    def test_published_readme_links_work_outside_the_repository(self):
        import re
        from importlib.metadata import metadata
        info = metadata('qt-ui-evidence')
        description = info.get('Description') or info.get_payload()
        self.assertTrue(description)
        links = re.findall(r'\]\(([^)]+)\)', description)
        self.assertTrue(links)
        for link in links:
            self.assertTrue(link.startswith(('https://', '#')), link)
