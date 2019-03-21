import os
import logging
from unittest.mock import MagicMock, patch, mock_open

from django.test import TestCase
from django.conf import settings

import cra_helper
from cra_helper import asset_manifest

# Quiet down logging
logging.disable(logging.CRITICAL)

server_url = 'http://foo.bar'


class TestGenerateManifest(TestCase):
    def test_returns_dict(self):
        self.assertIsInstance(asset_manifest.generate_manifest(True, '', ''), dict)

    def test_returns_bundle_url_if_cra_is_running(self):
        self.assertEqual(asset_manifest.generate_manifest(True, server_url, ''), {
            'bundle_js': server_url
        })

    def test_returns_main_paths_if_cra_is_not_running(self):
        open_mock = mock_open(
            read_data='''{
                "main.js": "static/js/main.1234.js",
                "main.css": "static/css/main.1234.css"
            }'''
        )
        with patch('builtins.open', open_mock):
            self.assertEqual(asset_manifest.generate_manifest(False, server_url, '.'), {
                'main_js': 'js/main.1234.js',
                'main_css': 'css/main.1234.css',
            })

    def test_checks_static_root_when_manifest_missing_from_cra_build_dir(self):
        # Pretend this folder is STATIC_ROOT to emulate falling back and accessing the
        # collected asset-manifest.json
        _here_path = os.path.dirname(os.path.realpath(__file__))
        setattr(settings, 'STATIC_ROOT', _here_path)
        self.assertEqual(asset_manifest.generate_manifest(False, server_url, 'not_a_real_dir'), {
            'main_js': 'js/main.1234.js',
            'main_css': 'css/main.1234.css',
        })

    def test_returns_empty_dict_if_file_not_found(self):
        open_mock = MagicMock(side_effect=Exception)
        with patch('builtins.open', open_mock):
            self.assertEqual(asset_manifest.generate_manifest(False, server_url, '.'), {})
