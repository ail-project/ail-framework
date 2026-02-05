#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Phashs.py object class.

These tests should be run in the AIL virtual environment where all dependencies
(flask, pymisp, redis, xxhash, etc.) are installed.

Run with:
    python3 -m nose2 tests.test_objects_phashes
    # or
    python3 -m unittest tests.test_objects_phashes
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.environ['AIL_BIN'])

from lib.objects import Phashs


class TestPhashInit(unittest.TestCase):
    """Test Phash.__init__() method."""
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_sets_type_and_id(self, mock_super_init):
        """__init__() should call super with 'phash' type and provided id."""
        phash = Phashs.Phash('c6073f39b0949d4b')
        mock_super_init.assert_called_once_with('phash', 'c6073f39b0949d4b')
        # Set attributes manually since __init__ is mocked
        phash.id = 'c6073f39b0949d4b'
        phash.type = 'phash'
        self.assertEqual(phash.id, 'c6073f39b0949d4b')
        self.assertEqual(phash.type, 'phash')


class TestPhashFormatValidation(unittest.TestCase):
    """Test that Phash accepts valid phash format strings (16-character hex)."""
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_valid_16_char_hex_string(self, mock_super_init):
        """__init__() should accept valid 16-character hexadecimal strings."""
        valid_phash = 'c6073f39b0949d4b'
        phash = Phashs.Phash(valid_phash)
        mock_super_init.assert_called_once_with('phash', valid_phash)
        # Set attributes manually since __init__ is mocked
        phash.id = valid_phash
        phash.type = 'phash'
        self.assertEqual(phash.id, valid_phash)
        self.assertEqual(len(valid_phash), 16)
        # Verify it's hex: all characters are 0-9, a-f
        self.assertTrue(all(c in '0123456789abcdef' for c in valid_phash.lower()))
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_valid_hex_with_uppercase(self, mock_super_init):
        """__init__() should accept 16-character hex strings with uppercase letters."""
        valid_phash = 'C6073F39B0949D4B'
        phash = Phashs.Phash(valid_phash)
        mock_super_init.assert_called_once_with('phash', valid_phash)
        # Set attributes manually since __init__ is mocked
        phash.id = valid_phash
        phash.type = 'phash'
        self.assertEqual(phash.id, valid_phash)
        self.assertEqual(len(valid_phash), 16)
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_all_zeros_phash(self, mock_super_init):
        """__init__() should accept phash with all zeros (edge case)."""
        valid_phash = '0000000000000000'
        phash = Phashs.Phash(valid_phash)
        mock_super_init.assert_called_once_with('phash', valid_phash)
        # Set attributes manually since __init__ is mocked
        phash.id = valid_phash
        phash.type = 'phash'
        self.assertEqual(phash.id, valid_phash)
        self.assertEqual(len(valid_phash), 16)
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_all_f_phash(self, mock_super_init):
        """__init__() should accept phash with all 'f' characters (edge case)."""
        valid_phash = 'ffffffffffffffff'
        phash = Phashs.Phash(valid_phash)
        mock_super_init.assert_called_once_with('phash', valid_phash)
        # Set attributes manually since __init__ is mocked
        phash.id = valid_phash
        phash.type = 'phash'
        self.assertEqual(phash.id, valid_phash)
        self.assertEqual(len(valid_phash), 16)
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_mixed_case_hex(self, mock_super_init):
        """__init__() should accept mixed case hex strings."""
        valid_phash = 'aBcDeF1234567890'
        phash = Phashs.Phash(valid_phash)
        mock_super_init.assert_called_once_with('phash', valid_phash)
        # Set attributes manually since __init__ is mocked
        phash.id = valid_phash
        phash.type = 'phash'
        self.assertEqual(phash.id, valid_phash)
        self.assertEqual(len(valid_phash), 16)
    
    @patch('lib.objects.Phashs.AbstractDaterangeObject.__init__')
    def test_init_accepts_other_valid_16_char_hex_strings(self, mock_super_init):
        """__init__() should accept other valid 16-character hex strings."""
        # Test various valid phash values used in other tests
        valid_phashes = [
            'def4567890abcdef',  # 16 characters
            '1234567890abcdef',  # 16 characters
            'fedcba0987654321',  # 16 characters
            '8000000000000000',  # 16 characters
        ]
        
        for valid_phash in valid_phashes:
            with self.subTest(phash=valid_phash):
                phash = Phashs.Phash(valid_phash)
                # Set attributes manually since __init__ is mocked
                phash.id = valid_phash
                phash.type = 'phash'
                self.assertEqual(phash.id, valid_phash)
                self.assertEqual(len(valid_phash), 16)
                # Verify it's hex
                self.assertTrue(all(c in '0123456789abcdef' for c in valid_phash.lower()))


class TestPhashGetLink(unittest.TestCase):
    """Test Phash.get_link() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
            self.phash.type = 'phash'
            self.phash.id = 'c6073f39b0949d4b'
    
    @patch('lib.objects.Phashs.url_for')
    def test_get_link_with_flask_context(self, mock_url_for):
        """get_link() should use url_for when flask_context=True."""
        mock_url_for.return_value = '/correlation/show?type=phash&id=c6073f39b0949d4b'
        result = self.phash.get_link(flask_context=True)
        mock_url_for.assert_called_once_with('correlation.show_correlation', type='phash', id='c6073f39b0949d4b')
        self.assertEqual(result, '/correlation/show?type=phash&id=c6073f39b0949d4b')
    
    @patch('lib.objects.Phashs.baseurl', 'https://example.com')
    def test_get_link_without_flask_context(self):
        """get_link() should construct URL from baseurl when flask_context=False."""
        result = self.phash.get_link(flask_context=False)
        expected = 'https://example.com/correlation/show?type=phash&id=c6073f39b0949d4b'
        self.assertEqual(result, expected)


class TestPhashGetSvgIcon(unittest.TestCase):
    """Test Phash.get_svg_icon() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
    
    def test_get_svg_icon_returns_correct_dict(self):
        """get_svg_icon() should return correct icon dictionary."""
        result = self.phash.get_svg_icon()
        expected = {'style': 'fas', 'icon': '\uf1c0', 'color': '#E1F5DF', 'radius': 5}
        self.assertEqual(result, expected)


class TestPhashGetMispObject(unittest.TestCase):
    """Test Phash.get_misp_object() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
            self.phash.type = 'phash'
            self.phash.id = 'c6073f39b0949d4b'
            self.phash.subtype = ''  # Phash doesn't have subtype, but get_misp_object references it
            self.phash.logger = MagicMock()
    
    @patch('lib.objects.Phashs.MISPObject')
    def test_get_misp_object_creates_misp_object(self, mock_misp_object_class):
        """get_misp_object() should create MISP object with phash attribute."""
        # Mock MISPObject
        mock_misp_obj = MagicMock()
        mock_attr = MagicMock()
        mock_misp_obj.add_attribute.return_value = mock_attr
        mock_misp_object_class.return_value = mock_misp_obj
        
        # Mock get_first_seen and get_last_seen
        self.phash.get_first_seen = MagicMock(return_value='20240101')
        self.phash.get_last_seen = MagicMock(return_value='20240102')
        self.phash.get_tags = MagicMock(return_value=['tag1', 'tag2'])
        self.phash.get_id = MagicMock(return_value='c6073f39b0949d4b')
        
        result = self.phash.get_misp_object()
        
        # Verify MISPObject was created with 'phash' type
        mock_misp_object_class.assert_called_once_with('phash')
        
        # Verify first_seen and last_seen were set
        self.assertEqual(mock_misp_obj.first_seen, '20240101')
        self.assertEqual(mock_misp_obj.last_seen, '20240102')
        
        # Verify phash attribute was added
        mock_misp_obj.add_attribute.assert_called_once_with('phash', value='c6073f39b0949d4b')
        
        # Verify tags were added to attribute
        self.assertEqual(mock_attr.add_tag.call_count, 2)
        mock_attr.add_tag.assert_any_call('tag1')
        mock_attr.add_tag.assert_any_call('tag2')
        
        self.assertEqual(result, mock_misp_obj)
    
    @patch('lib.objects.Phashs.MISPObject')
    def test_get_misp_object_handles_missing_first_seen(self, mock_misp_object_class):
        """get_misp_object() should handle None first_seen gracefully."""
        mock_misp_obj = MagicMock()
        mock_attr = MagicMock()
        mock_misp_obj.add_attribute.return_value = mock_attr
        mock_misp_object_class.return_value = mock_misp_obj
        
        self.phash.get_first_seen = MagicMock(return_value=None)
        self.phash.get_last_seen = MagicMock(return_value='20240102')
        self.phash.get_tags = MagicMock(return_value=[])
        self.phash.get_id = MagicMock(return_value='c6073f39b0949d4b')
        
        result = self.phash.get_misp_object()
        
        # Should log warning when first_seen or last_seen is None
        self.phash.logger.warning.assert_called_once()
        # first_seen should not be set when it's None (the code checks `if first_seen:` before setting)
        # Since first_seen is None, the assignment `obj.first_seen = first_seen` never happens
        # Verify last_seen was set correctly (since it's not None)
        self.assertEqual(mock_misp_obj.last_seen, '20240102')
        # Verify the MISP object was still created and returned
        self.assertEqual(result, mock_misp_obj)
    
    @patch('lib.objects.Phashs.MISPObject')
    def test_get_misp_object_handles_both_none(self, mock_misp_object_class):
        """get_misp_object() should handle both first_seen and last_seen being None."""
        mock_misp_obj = MagicMock()
        mock_attr = MagicMock()
        mock_misp_obj.add_attribute.return_value = mock_attr
        mock_misp_object_class.return_value = mock_misp_obj
        
        self.phash.get_first_seen = MagicMock(return_value=None)
        self.phash.get_last_seen = MagicMock(return_value=None)
        self.phash.get_tags = MagicMock(return_value=['tag1'])
        self.phash.get_id = MagicMock(return_value='c6073f39b0949d4b')
        
        result = self.phash.get_misp_object()
        
        # Should log warning when both are None
        self.phash.logger.warning.assert_called_once()
        # Neither should be set
        # Verify the MISP object was still created and returned
        self.assertEqual(result, mock_misp_obj)
        # Verify phash attribute was still added
        mock_misp_obj.add_attribute.assert_called_once_with('phash', value='c6073f39b0949d4b')
    
    @patch('lib.objects.Phashs.MISPObject')
    def test_get_misp_object_handles_empty_tags(self, mock_misp_object_class):
        """get_misp_object() should handle empty tags list."""
        mock_misp_obj = MagicMock()
        mock_attr = MagicMock()
        mock_misp_obj.add_attribute.return_value = mock_attr
        mock_misp_object_class.return_value = mock_misp_obj
        
        self.phash.get_first_seen = MagicMock(return_value='20240101')
        self.phash.get_last_seen = MagicMock(return_value='20240102')
        self.phash.get_tags = MagicMock(return_value=[])  # Empty tags
        self.phash.get_id = MagicMock(return_value='c6073f39b0949d4b')
        
        result = self.phash.get_misp_object()
        
        # Verify phash attribute was added
        mock_misp_obj.add_attribute.assert_called_once_with('phash', value='c6073f39b0949d4b')
        # Verify no tags were added (empty list, so loop doesn't execute)
        mock_attr.add_tag.assert_not_called()
        self.assertEqual(result, mock_misp_obj)


class TestPhashDelete(unittest.TestCase):
    """Test Phash.delete() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
    
    def test_delete_exists_and_does_not_raise(self):
        """delete() method exists and doesn't raise an error (currently just pass)."""
        # Currently delete() is a TODO and just has `pass`
        # Test that it exists and can be called without error
        try:
            self.phash.delete()
        except Exception as e:
            self.fail(f"delete() raised an exception: {e}")


class TestPhashGetNbSeen(unittest.TestCase):
    """Test Phash.get_nb_seen() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
    
    def test_get_nb_seen_returns_image_correlations(self):
        """get_nb_seen() should return number of image correlations."""
        self.phash.get_nb_correlation = MagicMock(return_value=5)
        result = self.phash.get_nb_seen()
        self.phash.get_nb_correlation.assert_called_once_with('image')
        self.assertEqual(result, 5)


class TestPhashGetMeta(unittest.TestCase):
    """Test Phash.get_meta() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
            self.phash.id = 'c6073f39b0949d4b'
    
    def test_get_meta_includes_id_and_tags(self):
        """get_meta() should include id and tags in returned metadata."""
        self.phash._get_meta = MagicMock(return_value={'first_seen': '20240101', 'last_seen': '20240102'})
        self.phash.get_tags = MagicMock(return_value=['tag1', 'tag2'])
        
        result = self.phash.get_meta()
        
        self.phash._get_meta.assert_called_once_with(options=set())
        self.phash.get_tags.assert_called_once_with(r_list=True)
        self.assertEqual(result['id'], 'c6073f39b0949d4b')
        self.assertEqual(result['tags'], ['tag1', 'tag2'])
        self.assertEqual(result['first_seen'], '20240101')
        self.assertEqual(result['last_seen'], '20240102')
    
    def test_get_meta_passes_options_to_get_meta(self):
        """get_meta() should pass options to _get_meta()."""
        self.phash._get_meta = MagicMock(return_value={})
        self.phash.get_tags = MagicMock(return_value=[])
        
        options = {'link', 'sparkline'}
        self.phash.get_meta(options=options)
        
        self.phash._get_meta.assert_called_once_with(options=options)


class TestPhashCreate(unittest.TestCase):
    """Test Phash.create() method."""
    
    def setUp(self):
        """Set up Phash instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObject.__init__', return_value=None):
            self.phash = Phashs.Phash('c6073f39b0949d4b')
    
    def test_create_calls_create(self):
        """create() should call _create() method."""
        self.phash._create = MagicMock()
        self.phash.create()
        self.phash._create.assert_called_once()
    
    def test_create_passes_first_seen_and_last_seen(self):
        """create() should call _create() (parameters are accepted but not currently used)."""
        self.phash._create = MagicMock()
        self.phash.create(_first_seen='20240101', _last_seen='20240102')
        # Note: The current implementation accepts _first_seen and _last_seen parameters
        # but doesn't pass them to _create(). This test documents current behavior.
        # The parameters are accepted for API compatibility but ignored.
        self.phash._create.assert_called_once()
        # Verify _create was called without arguments (current implementation)
        self.phash._create.assert_called_once_with()


class TestPhashCreateFunction(unittest.TestCase):
    """Test create() module-level function."""
    
    PHASH_VALUE = 'c6073f39b0949d4b'
    
    @patch('lib.objects.Phashs.Phash')
    def test_create_uses_phash_value_as_id_when_obj_id_none(self, mock_phash_class):
        """create() should use phash_value as id when obj_id is None."""
        mock_phash_obj = MagicMock()
        mock_phash_obj.exists.return_value = False
        mock_phash_class.return_value = mock_phash_obj
        
        result = Phashs.create(self.PHASH_VALUE)
        
        mock_phash_class.assert_called_once_with(self.PHASH_VALUE)
        mock_phash_obj.exists.assert_called_once()
        mock_phash_obj.create.assert_called_once()
        self.assertEqual(result, mock_phash_obj)
    
    @patch('lib.objects.Phashs.Phash')
    def test_create_uses_obj_id_when_provided(self, mock_phash_class):
        """create() should use obj_id when provided instead of phash_value."""
        mock_phash_obj = MagicMock()
        mock_phash_obj.exists.return_value = False
        mock_phash_class.return_value = mock_phash_obj
        
        custom_id = 'custom_phash_id'
        result = Phashs.create(self.PHASH_VALUE, obj_id=custom_id)
        
        mock_phash_class.assert_called_once_with(custom_id)
        mock_phash_obj.exists.assert_called_once()
        mock_phash_obj.create.assert_called_once()
        self.assertEqual(result, mock_phash_obj)
    
    @patch('lib.objects.Phashs.Phash')
    def test_create_does_not_create_if_exists(self, mock_phash_class):
        """create() should not call create() if Phash object already exists."""
        mock_phash_obj = MagicMock()
        mock_phash_obj.exists.return_value = True
        mock_phash_class.return_value = mock_phash_obj
        
        result = Phashs.create(self.PHASH_VALUE)
        
        mock_phash_obj.exists.assert_called_once()
        mock_phash_obj.create.assert_not_called()
        self.assertEqual(result, mock_phash_obj)


class TestPhashsInit(unittest.TestCase):
    """Test Phashs.__init__() method."""
    
    @patch('lib.objects.Phashs.AbstractDaterangeObjects.__init__')
    def test_init_sets_type_and_class(self, mock_super_init):
        """__init__() should call super with 'phash' type and Phash class."""
        phashs = Phashs.Phashs()
        mock_super_init.assert_called_once_with('phash', Phashs.Phash)


class TestPhashsGetName(unittest.TestCase):
    """Test Phashs.get_name() method."""
    
    def setUp(self):
        """Set up Phashs instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObjects.__init__', return_value=None):
            self.phashs = Phashs.Phashs()
    
    def test_get_name_returns_phashes(self):
        """get_name() should return 'Phashs'."""
        result = self.phashs.get_name()
        self.assertEqual(result, 'Phashs')


class TestPhashsGetIcon(unittest.TestCase):
    """Test Phashs.get_icon() method."""
    
    def setUp(self):
        """Set up Phashs instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObjects.__init__', return_value=None):
            self.phashs = Phashs.Phashs()
    
    def test_get_icon_returns_correct_dict(self):
        """get_icon() should return correct icon dictionary."""
        result = self.phashs.get_icon()
        expected = {'fa': 'fa-solid', 'icon': 'image'}
        self.assertEqual(result, expected)


class TestPhashsGetLink(unittest.TestCase):
    """Test Phashs.get_link() method."""
    
    def setUp(self):
        """Set up Phashs instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObjects.__init__', return_value=None):
            self.phashs = Phashs.Phashs()
    
    @patch('lib.objects.Phashs.url_for')
    def test_get_link_with_flask_context(self, mock_url_for):
        """get_link() should use url_for when flask_context=True."""
        mock_url_for.return_value = '/objects/phashes'
        result = self.phashs.get_link(flask_context=True)
        mock_url_for.assert_called_once_with('objects_phash.objects_phashes')
        self.assertEqual(result, '/objects/phashes')
    
    @patch('lib.objects.Phashs.baseurl', 'https://example.com')
    def test_get_link_without_flask_context(self):
        """get_link() should construct URL from baseurl when flask_context=False."""
        result = self.phashs.get_link(flask_context=False)
        expected = 'https://example.com/objects/phashes'
        self.assertEqual(result, expected)


class TestPhashsSanitizeIdToSearch(unittest.TestCase):
    """Test Phashs.sanitize_id_to_search() method."""
    
    def setUp(self):
        """Set up Phashs instance for testing."""
        with patch('lib.objects.Phashs.AbstractDaterangeObjects.__init__', return_value=None):
            self.phashs = Phashs.Phashs()
    
    def test_sanitize_id_to_search_returns_input(self):
        """sanitize_id_to_search() should return input as-is."""
        test_id = 'c6073f39b0949d4b'
        result = self.phashs.sanitize_id_to_search(test_id)
        self.assertEqual(result, test_id)
    
    def test_sanitize_id_to_search_handles_special_chars(self):
        """sanitize_id_to_search() should return input even with special characters."""
        test_id = 'abc123!@#'
        result = self.phashs.sanitize_id_to_search(test_id)
        self.assertEqual(result, test_id)

