#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

    # ========== get_description_models() Tests ==========
    
    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_returns_models(self, mock_get_keys):
        """get_description_models() should return all desc:* fields."""
        # Fix: Mock _get_fields_keys() instead of r_serv_metadata.hkeys()
        mock_get_keys.return_value = ['desc:modelA', 'other', 'desc:modelB']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertEqual(sorted(models), ['modelA', 'modelB'])

    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_empty_when_no_fields(self, mock_get_keys):
        """Should return empty list when no fields exist."""
        mock_get_keys.return_value = []
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertIsInstance(models, list)
        self.assertEqual(models, [])

    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_empty_when_no_desc_fields(self, mock_get_keys):
        """Should return empty list when no desc: fields exist."""
        mock_get_keys.return_value = ['other_field', 'another_field', 'some_key']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertIsInstance(models, list)
        self.assertEqual(models, [])

    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_multiple_models(self, mock_get_keys):
        """Should return all description models when multiple desc: fields exist."""
        mock_get_keys.return_value = ['desc:ollama', 'desc:phi3', 'desc:gpt4', 'other_field']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        self.assertEqual(sorted(models), ['gpt4', 'ollama', 'phi3'])

    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_handles_bytes_and_strings(self, mock_get_keys):
        """Should handle both bytes and string keys from database."""
        # Database may return keys as bytes or strings
        mock_get_keys.return_value = [b'desc:model1', 'desc:model2', b'other_field']
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        # After fix: code now decodes bytes, so both model1 and model2 should be returned
        self.assertEqual(sorted(models), ['model1', 'model2'])

    @patch('lib.objects.Images.Image._get_fields_keys')
    def test_get_description_models_returns_list_not_none(self, mock_get_keys):
        """Should return a list, never None (this was the bug we fixed!)."""
        mock_get_keys.return_value = []
        image = Images.Image('deadbeef')
        models = image.get_description_models()
        # Critical test: The bug was returning None instead of a list
        self.assertIsNotNone(models, "get_description_models() must not return None")
        self.assertIsInstance(models, list, "get_description_models() must return a list")


class TestScreenshots(unittest.TestCase):

    @patch('lib.objects.Screenshots.Screenshot.__init__', return_value=None)
    @patch('lib.objects.Screenshots.Screenshot.exists')
    def test_create_screenshot_uses_binary_size(self, mock_exists, mock_init):
        mock_exists.return_value = False
        raw_content = b'abc'
        result = Screenshots.create_screenshot(raw_content, size_limit=2, b64=False)
        self.assertIsNone(result)
        mock_init.assert_not_called()

    # ========== get_description_models() Tests ==========
    
    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models(self, mock_get_keys):
        """get_description_models() should return all desc:* fields."""
        # Fix: Mock _get_fields_keys() instead of r_serv_metadata.hkeys()
        mock_get_keys.return_value = ['desc:ollama', 'desc:phi3']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertEqual(sorted(models), ['ollama', 'phi3'])

    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models_empty_when_no_fields(self, mock_get_keys):
        """Should return empty list when no fields exist."""
        mock_get_keys.return_value = []
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertIsInstance(models, list)
        self.assertEqual(models, [])

    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models_empty_when_no_desc_fields(self, mock_get_keys):
        """Should return empty list when no desc: fields exist."""
        mock_get_keys.return_value = ['other_field', 'another_field']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertIsInstance(models, list)
        self.assertEqual(models, [])

    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models_multiple_models(self, mock_get_keys):
        """Should return all description models when multiple desc: fields exist."""
        mock_get_keys.return_value = ['desc:ollama', 'desc:phi3', 'desc:gpt4']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        self.assertEqual(sorted(models), ['gpt4', 'ollama', 'phi3'])

    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models_handles_bytes_and_strings(self, mock_get_keys):
        """Should handle both bytes and string keys from database."""
        mock_get_keys.return_value = [b'desc:model1', 'desc:model2']
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        # After fix: code now decodes bytes, so both model1 and model2 should be returned
        self.assertEqual(sorted(models), ['model1', 'model2'])

    @patch('lib.objects.Screenshots.Screenshot._get_fields_keys')
    def test_screenshot_get_description_models_returns_list_not_none(self, mock_get_keys):
        """Should return a list, never None (this was the bug we fixed!)."""
        mock_get_keys.return_value = []
        screenshot = Screenshots.Screenshot('cafebabe')
        models = screenshot.get_description_models()
        # Critical test: The bug was returning None instead of a list
        self.assertIsNotNone(models, "get_description_models() must not return None")
        self.assertIsInstance(models, list, "get_description_models() must return a list")


    # ========== Phash Tests ==========
    
    # What it tests: When phash is already cached in database, get_phash() should return it immediately
    # without recalculating. Uses a real test image to verify the expected phash value.
    @patch('lib.objects.Images.Image.exists')
    @patch('lib.objects.Images.Image.get_filepath')
    @patch('lib.objects.Images.Image._get_field')
    @patch('lib.objects.Images.Image._set_field')
    def test_get_phash_returns_cached_value(self, mock_set, mock_get_field, mock_filepath, mock_exists):
        """get_phash() should return cached value if available."""
        # Calculate expected phash from real test image
        try:
            import imagehash
            from PIL import Image as PILImage
            test_image_path = os.path.join(os.path.dirname(__file__), 'images', 'test_image_red.png')
            if os.path.exists(test_image_path):
                with PILImage.open(test_image_path) as img:
                    expected_phash = str(imagehash.phash(img))
            else:
                expected_phash = 'cached_phash_value'  # Fallback if image doesn't exist
        except ImportError:
            expected_phash = 'cached_phash_value'  # Fallback if imagehash not available
        
        mock_get_field.return_value = expected_phash
        image = Images.Image('test123')
        result = image.get_phash()
        self.assertEqual(result, expected_phash)
        mock_set.assert_not_called()  # Should not recalculate
    
    # What it tests: When phash is NOT cached, get_phash() should calculate it from a real image file
    # and store it in the database. Verifies the calculated phash matches expected value.
    @patch('lib.objects.Images.Image.exists')
    @patch('lib.objects.Images.Image.get_filepath')
    @patch('lib.objects.Images.Image._get_field')
    @patch('lib.objects.Images.Image._set_field')
    @patch('lib.objects.Images.IMAGEHASH_AVAILABLE', True)
    def test_get_phash_calculates_if_not_cached(self, mock_set, mock_get_field, mock_filepath, mock_exists):
        """get_phash() should calculate and cache if not stored."""
        # Use real test image
        test_image_path = os.path.join(os.path.dirname(__file__), 'images', 'test_image_red.png')
        if not os.path.exists(test_image_path):
            self.skipTest(f"Test image not found: {test_image_path}")
        
        mock_get_field.return_value = None  # No cached value
        mock_exists.return_value = True
        mock_filepath.return_value = test_image_path
        
        # Calculate expected phash
        try:
            import imagehash
            from PIL import Image as PILImage
            with PILImage.open(test_image_path) as img:
                expected_phash = str(imagehash.phash(img))
        except ImportError:
            self.skipTest("imagehash library not available")
        
        image = Images.Image('test123')
        result = image.get_phash()
        
        self.assertEqual(result, expected_phash)
        mock_set.assert_called_once_with('phash', expected_phash)
    
    # What it tests: When imagehash library is not installed, calculate_phash() should return None
    # gracefully without crashing. This ensures the system works even without optional dependencies.
    @patch('lib.objects.Images.Image.exists')
    @patch('lib.objects.Images.IMAGEHASH_AVAILABLE', False)
    def test_calculate_phash_returns_none_if_library_unavailable(self, mock_exists):
        """calculate_phash() should return None if imagehash library not available."""
        image = Images.Image('test123')
        result = image.calculate_phash()
        self.assertIsNone(result)
    
    # What it tests: When opening/reading the image file fails (corrupt file, permission error, etc.),
    # calculate_phash() should catch the exception and return None gracefully without crashing.
    @patch('lib.objects.Images.Image.exists')
    @patch('lib.objects.Images.Image.get_filepath')
    @patch('lib.objects.Images.IMAGEHASH_AVAILABLE', True)
    @patch('lib.objects.Images.PILImage')
    @patch('lib.objects.Images.imagehash')
    def test_calculate_phash_handles_exceptions(self, mock_imagehash, mock_pil, mock_filepath, mock_exists):
        """calculate_phash() should return None on exceptions."""
        mock_exists.return_value = True
        mock_filepath.return_value = '/path/to/image.png'
        mock_pil.open.side_effect = Exception("File error")
        
        image = Images.Image('test123')
        result = image.calculate_phash()
        self.assertIsNone(result)
    
    # What it tests: When metadata is requested with options={'phash'}, get_meta() should include
    # the phash value in the returned metadata dictionary.
    @patch('lib.objects.Images.Image.get_phash')
    def test_get_meta_includes_phash_when_requested(self, mock_get_phash):
        """get_meta() should include phash when 'phash' is in options."""
        mock_get_phash.return_value = 'test_phash_value'
        image = Images.Image('test123')
        
        # Mock other required methods
        with patch.object(image, '_get_meta', return_value={}):
            with patch.object(image, 'get_tags', return_value=[]):
                meta = image.get_meta(options={'phash'})
        
        self.assertIn('phash', meta)
        self.assertEqual(meta['phash'], 'test_phash_value')
        mock_get_phash.assert_called_once()
    
    # What it tests: When calculate_phash() returns None, get_phash() should return None
    # but NOT store None in the database (prevents database pollution).
    @patch('lib.objects.Images.Image.exists')
    @patch('lib.objects.Images.Image._get_field')
    @patch('lib.objects.Images.Image._set_field')
    @patch('lib.objects.Images.IMAGEHASH_AVAILABLE', False)
    def test_get_phash_does_not_store_none_when_calculation_fails(self, mock_set, mock_get_field, mock_exists):
        """get_phash() should not store None when calculation fails."""
        mock_get_field.return_value = None  # No cached value
        image = Images.Image('test123')
        result = image.get_phash()
        
        self.assertIsNone(result)
        mock_set.assert_not_called()  # Should NOT store None
    
    # What it tests: When requesting metadata with options={'all'}, phash should be included
    # even though 'phash' is not explicitly in the options set.
    @patch('lib.objects.Images.Image.get_phash')
    def test_get_meta_includes_phash_when_all_requested(self, mock_get_phash):
        """get_meta() should include phash when 'all' is in options."""
        mock_get_phash.return_value = 'test_phash_value'
        image = Images.Image('test123')
        
        with patch.object(image, '_get_meta', return_value={}):
            with patch.object(image, 'get_tags', return_value=[]):
                meta = image.get_meta(options={'all'})
        
        self.assertIn('phash', meta)
        self.assertEqual(meta['phash'], 'test_phash_value')
        mock_get_phash.assert_called_once()
    
    # What it tests: When phash is NOT requested in options, get_meta() should NOT include it
    # and should NOT call get_phash() (lazy loading - only calculate when needed).
    @patch('lib.objects.Images.Image.get_phash')
    def test_get_meta_excludes_phash_when_not_requested(self, mock_get_phash):
        """get_meta() should not include phash when not requested."""
        image = Images.Image('test123')
        
        with patch.object(image, '_get_meta', return_value={}):
            with patch.object(image, 'get_tags', return_value=[]):
                meta = image.get_meta(options={'description'})  # phash not requested
        
        self.assertNotIn('phash', meta)
        mock_get_phash.assert_not_called()  # Should NOT calculate phash


class TestScreenshotsPhash(unittest.TestCase):
    """Test phash functionality for Screenshots."""
    
    @patch('lib.objects.Screenshots.Screenshot.exists')
    @patch('lib.objects.Screenshots.Screenshot.get_filepath')
    @patch('lib.objects.Screenshots.Screenshot._get_field')
    @patch('lib.objects.Screenshots.Screenshot._set_field')
    def test_screenshot_get_phash_returns_cached_value(self, mock_set, mock_get_field, mock_filepath, mock_exists):
        """get_phash() should return cached value if available."""
        mock_get_field.return_value = 'cached_phash_value'
        screenshot = Screenshots.Screenshot('test123')
        result = screenshot.get_phash()
        self.assertEqual(result, 'cached_phash_value')
        mock_set.assert_not_called()
    
    @patch('lib.objects.Screenshots.Screenshot.get_phash')
    def test_screenshot_get_meta_includes_phash_when_requested(self, mock_get_phash):
        """get_meta() should include phash when 'phash' is in options."""
        mock_get_phash.return_value = 'test_phash_value'
        screenshot = Screenshots.Screenshot('test123')
        
        # Mock other required methods
        with patch.object(screenshot, 'get_default_meta', return_value={}):
            with patch.object(screenshot, 'get_tags', return_value=[]):
                meta = screenshot.get_meta(options={'phash'})
        
        self.assertIn('phash', meta)
        self.assertEqual(meta['phash'], 'test_phash_value')
        mock_get_phash.assert_called_once()


if __name__ == '__main__':
    unittest.main()

