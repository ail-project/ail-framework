#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Image and Screenshot objects.

Note: pHash logic (calculate_phash, get_phash, set_phash) lives in lib.objects.Phashs
and is retrieved via get_correlation('phash').get('phash'). Tests for phash
behavior are in test_objects_phashes.py and test_modules.py (ImagePhash, PhashCorrelation).
"""

import base64
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.environ['AIL_BIN'])

from lib.objects import Images
from lib.objects import Screenshots


class TestImages(unittest.TestCase):

    @patch('lib.objects.Images.Image')
    def test_create_enforces_size_limit(self, mock_image_class):
        """create() should refuse content that exceeds size_limit."""
        oversized = b'a' * 10
        result = Images.create(oversized, size_limit=5, b64=False, force=False)
        self.assertIsNone(result)
        mock_image_class.assert_not_called()

    @patch('lib.objects.Images.Image')
    def test_create_decodes_base64_before_size_check(self, mock_image_class):
        """create() must decode base64 payloads before hashing/storing."""
        raw_content = b'hello-world'
        b64_content = base64.standard_b64encode(raw_content).decode()
        # size_limit must allow decoded size: create() uses (len(content)*3)/4 for b64
        decoded_size = (len(b64_content) * 3) // 4
        size_limit = max(len(raw_content), decoded_size)

        mock_image = MagicMock()
        mock_image.exists.return_value = False
        mock_image_class.return_value = mock_image

        result = Images.create(b64_content, size_limit=size_limit, b64=True)

        self.assertIsNotNone(result)
        mock_image.create.assert_called_once_with(raw_content)

    @patch('lib.objects.abstract_object.r_object')
    def test_get_description_models_returns_models(self, mock_r_object):
        """get_description_models() should return all desc:* fields."""
        mock_r_object.hkeys.return_value = [b'desc:modelA', b'other', 'desc:modelB']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertEqual(sorted(models), ['modelA', 'modelB'])

    @patch('lib.objects.abstract_object.r_object')
    def test_get_description_models_handles_bytes_and_strings(self, mock_r_object):
        """get_description_models() should handle keys as bytes or strings."""
        mock_r_object.hkeys.return_value = [b'desc:modelA', 'desc:modelB']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertEqual(sorted(models), ['modelA', 'modelB'])


class TestScreenshots(unittest.TestCase):

    @patch('lib.objects.Screenshots.Screenshot.__init__', return_value=None)
    @patch('lib.objects.Screenshots.Screenshot.exists')
    def test_create_screenshot_uses_binary_size(self, mock_exists, mock_init):
        mock_exists.return_value = False
        raw_content = b'abc'
        result = Screenshots.create_screenshot(raw_content, size_limit=2, b64=False)
        self.assertIsNone(result)
        mock_init.assert_not_called()

    @patch('lib.objects.Screenshots.sha256')
    @patch('lib.objects.Screenshots.Screenshot')
    def test_create_screenshot_decodes_base64(self, mock_screenshot_class, mock_sha256):
        raw_content = b'test-bytes'
        b64_content = base64.standard_b64encode(raw_content).decode()
        # size_limit must allow decoded size: create_screenshot() uses (len(content)*3)/4 for b64
        decoded_size = (len(b64_content) * 3) // 4
        size_limit = max(len(raw_content), decoded_size)

        mock_hash = MagicMock()
        mock_hash.hexdigest.return_value = 'cafebabe'
        mock_sha256.return_value = mock_hash
        mock_screenshot = MagicMock()
        mock_screenshot.exists.return_value = True
        mock_screenshot_class.return_value = mock_screenshot

        result = Screenshots.create_screenshot(b64_content, size_limit=size_limit, b64=True)

        self.assertIsNotNone(result)
        mock_sha256.assert_called_once_with(raw_content)

    @patch('lib.objects.abstract_object.r_object')
    def test_screenshot_get_description_models(self, mock_r_object):
        mock_r_object.hkeys.return_value = ['desc:ollama', b'desc:phi3']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertEqual(sorted(models), ['ollama', 'phi3'])

    @patch('lib.objects.abstract_object.r_object')
    def test_screenshot_get_description_models_handles_bytes_and_strings(self, mock_r_object):
        """get_description_models() should handle keys as bytes or strings."""
        mock_r_object.hkeys.return_value = [b'desc:ollama', 'desc:phi3']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertEqual(sorted(models), ['ollama', 'phi3'])


if __name__ == '__main__':
    unittest.main()
