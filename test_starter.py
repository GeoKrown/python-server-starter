import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import install_packages as app


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.tmp.name)
        (self.root / 'packages.json').write_text(json.dumps({'base': {'requests': 'requests'}, 'extra': {'shapely': 'shapely'}}))
        self.root_patch = patch.object(app, 'ROOT', self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.tmp.cleanup()

    def fake_create(self, path):
        python = path / ('Scripts/python.exe' if app.os.name == 'nt' else 'bin/python')
        python.parent.mkdir(parents=True)
        python.touch()

    def test_profiles(self):
        self.assertEqual(app.packages('base'), {'requests': 'requests'})
        self.assertEqual(set(app.packages('all')), {'requests', 'shapely'})

    def test_existing_unowned_environment_is_not_modified(self):
        (self.root / '.venv').mkdir()
        with patch.object(app, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'another setup'):
                app.setup()
            run.assert_not_called()

    def test_failed_install_never_writes_success_lock(self):
        with patch.object(app.venv.EnvBuilder, 'create', side_effect=self.fake_create), patch.object(app, 'run', side_effect=subprocess.CalledProcessError(1, 'pip')):
            with self.assertRaises(subprocess.CalledProcessError):
                app.setup(skip_browser=True)
        self.assertFalse(list(self.root.glob('*.lock.txt')))

    def test_repeat_reuses_lock_and_check_does_not_install(self):
        with patch.object(app.venv.EnvBuilder, 'create', side_effect=self.fake_create), patch.object(app, 'run', return_value=subprocess.CompletedProcess([], 0, stdout='requests==2.32.5\n')) as run:
            app.setup(skip_browser=True)
            self.assertEqual(len(list(self.root.glob('*.lock.txt'))), 1)
            run.reset_mock()
            app.setup(skip_browser=True)
            self.assertIn('-r', run.call_args_list[1].args[0])
            run.reset_mock()
            app.setup(skip_browser=True, check_only=True)
            self.assertFalse(any('install' in c.args[0] for c in run.call_args_list))

    def test_browser_failure_is_not_success(self):
        def fail_browser(args, capture=False):
            if 'playwright' in args:
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0, stdout='')
        with patch.object(app.venv.EnvBuilder, 'create', side_effect=self.fake_create), patch.object(app, 'run', side_effect=fail_browser):
            with self.assertRaises(subprocess.CalledProcessError):
                app.setup()
        self.assertFalse(list(self.root.glob('*.lock.txt')))

    def test_check_missing_environment_creates_nothing(self):
        with self.assertRaisesRegex(RuntimeError, 'No environment'):
            app.setup(check_only=True)
        self.assertFalse((self.root / '.venv').exists())


    def test_invalid_manifest_creates_no_environment(self):
        invalid = [[], {}, {'base': []}, {'base': {'requests': ''}},
                   {'base': {'--index-url': 'requests'}}]
        for config in invalid:
            with self.subTest(config=config):
                (self.root / 'packages.json').write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    app.setup()
                self.assertFalse((self.root / '.venv').exists())

    def test_new_manifest_package_is_installed_with_existing_lock(self):
        with patch.object(app.venv.EnvBuilder, 'create', side_effect=self.fake_create), patch.object(app, 'run', return_value=subprocess.CompletedProcess([], 0, stdout='requests==2.32.5\n')) as run:
            app.setup(skip_browser=True)
            config = json.loads((self.root / 'packages.json').read_text())
            config['base']['rich'] = 'rich'
            (self.root / 'packages.json').write_text(json.dumps(config))
            run.reset_mock()
            app.setup(skip_browser=True)
            command = run.call_args_list[1].args[0]
            self.assertIn('-r', command)
            self.assertIn('rich', command)

    def test_failed_refresh_preserves_previous_lock(self):
        with patch.object(app.venv.EnvBuilder, 'create', side_effect=self.fake_create), patch.object(app, 'run', return_value=subprocess.CompletedProcess([], 0, stdout='requests==2.32.5\n')):
            app.setup(skip_browser=True)
        lock = next(self.root.glob('*.lock.txt'))
        previous = lock.read_bytes()
        with patch.object(app, 'run', side_effect=subprocess.CalledProcessError(1, 'pip')):
            with self.assertRaises(subprocess.CalledProcessError):
                app.setup(refresh=True, skip_browser=True)
        self.assertEqual(lock.read_bytes(), previous)

    def test_atomic_write_failure_keeps_original_and_cleans_temp(self):
        path = self.root / 'snapshot.txt'
        path.write_text('original')
        with patch.object(app.os, 'replace', side_effect=OSError('write denied')):
            with self.assertRaises(OSError):
                app.atomic_text(path, 'replacement')
        self.assertEqual(path.read_text(), 'original')
        self.assertEqual(list(self.root.glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
