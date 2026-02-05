#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import gzip
from base64 import b64encode
from distutils.dir_util import copy_tree

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
# Modules Classes
from modules.ApiKey import ApiKey
from modules.Categ import Categ
from modules.CreditCards import CreditCards
from modules.DomClassifier import DomClassifier
from modules.Global import Global
from modules.ImagePhash import Phash as ImagePhash
from modules.Keys import Keys
from modules.Onion import Onion
from modules.PhashCorrelation import PhashCorrelation
from modules.Telegram import Telegram

# project packages
import lib.objects.Items as Items

#### COPY SAMPLES ####
config_loader = ConfigLoader()
ITEMS_FOLDER = Items.ITEMS_FOLDER
TESTS_ITEMS_FOLDER = os.path.join(ITEMS_FOLDER, 'tests')
sample_dir = os.path.join(os.environ['AIL_HOME'], 'samples')
copy_tree(sample_dir, TESTS_ITEMS_FOLDER)


#### ---- ####

class TestModuleApiKey(unittest.TestCase):

    def setUp(self):
        self.module = ApiKey()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/api_keys.gz'
        self.module.obj = Items.Item(item_id)
        google_api_key = 'AIza00000000000000000000000_example-KEY'
        aws_access_key = 'AKIAIOSFODNN7EXAMPLE'
        aws_secret_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

        matches = self.module.compute('3', r_result=True)
        self.assertCountEqual(matches[0], {google_api_key})
        self.assertCountEqual(matches[1], {aws_access_key})
        self.assertCountEqual(matches[2], {aws_secret_key})


class TestModuleCateg(unittest.TestCase):

    def setUp(self):
        self.module = Categ()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/categ.gz'
        self.module.obj = Items.Item(item_id)
        test_categ = ['CreditCards', 'Mail', 'Onion', 'Urls', 'Credential', 'Cve']

        result = self.module.compute(None, r_result=True)
        self.assertCountEqual(result, test_categ)


class TestModuleCreditCards(unittest.TestCase):

    def setUp(self):
        self.module = CreditCards()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/credit_cards.gz'
        self.module.obj = Items.Item(item_id)
        test_cards = ['341039324930797',   # American Express
                      '6011613905509166',  # Discover Card
                      '3547151714018657',  # Japan Credit Bureau (JCB)
                      '5492981206527330',  # 16 digits MasterCard
                      '4024007132849695',  # '4532525919781' # 16-digit VISA, with separators
                      ]

        result = self.module.compute('7', r_result=True)
        self.assertCountEqual(result, test_cards)


class TestModuleDomClassifier(unittest.TestCase):

    def setUp(self):
        self.module = DomClassifier()
        self.module.debug = True

    def test_module(self):
        test_host = 'foo.be'
        item_id = 'tests/2021/01/01/domain_classifier.gz'
        self.module.obj = Items.Item(item_id)
        result = self.module.compute(f'{test_host}', r_result=True)
        self.assertTrue(len(result))


class TestModuleGlobal(unittest.TestCase):

    def setUp(self):
        self.module = Global()
        self.module.debug = True

    def test_module(self):
        # # TODO: delete item
        item_id = 'tests/2021/01/01/global.gz'
        item = Items.Item(item_id)
        item.delete()

        item_content = b'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
        item_content_1 = b64encode(gzip.compress(item_content)).decode()
        item_content_2 = b64encode(gzip.compress(item_content + b' more text ...')).decode()

        self.module.obj = Items.Item(item_id)
        # Test new item
        result = self.module.compute(item_content_1, r_result=True)
        self.assertEqual(result, item_id)

        # Test duplicate
        result = self.module.compute(item_content_1, r_result=True)
        self.assertIsNone(result)

        # Test same id with != content
        item = Items.Item('tests/2021/01/01/global_831875da824fc86ab5cc0e835755b520.gz')
        item.delete()
        result = self.module.compute(item_content_2, r_result=True)
        self.assertIn(item_id[:-3], result)
        self.assertNotEqual(result, item_id)

        # cleanup
        # item = Items.Item(result)
        # item.delete()
        # # TODO: remove from queue


class TestModuleKeys(unittest.TestCase):

    def setUp(self):
        self.module = Keys()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/keys.gz'
        self.module.obj = Items.Item(item_id)
        # # TODO: check results
        self.module.compute(None)


class TestModuleOnion(unittest.TestCase):

    def setUp(self):
        self.module = Onion()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/onion.gz'
        self.module.obj = Items.Item(item_id)
        # domain_1 = 'eswpccgr5xyovsahffkehgleqthrasfpfdblwbs4lstd345dwq5qumqd.onion'
        # domain_2 = 'www.facebookcorewwwi.onion'

        self.module.compute(f'3')


class TestModuleTelegram(unittest.TestCase):

    def setUp(self):
        self.module = Telegram()
        self.module.debug = True

    def test_module(self):
        item_id = 'tests/2021/01/01/keys.gz'
        self.module.obj = Items.Item(item_id)
        # # TODO: check results
        self.module.compute(None)


if __name__ == '__main__':
    unittest.main()

class TestModulePhashCorrelation(unittest.TestCase):
    """Test PhashCorrelation module initialization."""

    @patch('lib.ConfigLoader.ConfigLoader')
    def test_init_loads_config_max_hamming_distance(self, mock_config_loader_class):
        """__init__ should load max_hamming_distance from config."""
        mock_config_loader = MagicMock()
        mock_config_loader_class.return_value = mock_config_loader
        mock_config_loader.get_config_int.return_value = 10
        
        module = PhashCorrelation()
        
        self.assertEqual(module.max_hamming_distance, 10)
        self.assertEqual(module.pending_seconds, 1)
        mock_config_loader.get_config_int.assert_called_once_with("Images", "phash_max_hamming_distance")
    
    @patch('lib.ConfigLoader.ConfigLoader')
    def test_init_defaults_to_8_when_config_missing(self, mock_config_loader_class):
        """__init__ should default to 8 when config is missing or invalid."""
        mock_config_loader = MagicMock()
        mock_config_loader_class.return_value = mock_config_loader
        mock_config_loader.get_config_int.side_effect = Exception("Config not found")
        
        module = PhashCorrelation()
        
        self.assertEqual(module.max_hamming_distance, 8)  # Default value
        self.assertEqual(module.pending_seconds, 1)
    
    @patch('lib.ConfigLoader.ConfigLoader')
    def test_init_sets_pending_seconds(self, mock_config_loader_class):
        """__init__ should set pending_seconds to 1."""
        mock_config_loader = MagicMock()
        mock_config_loader_class.return_value = mock_config_loader
        mock_config_loader.get_config_int.return_value = 5
        
        module = PhashCorrelation()
        
        self.assertEqual(module.pending_seconds, 1)
    
    @patch('lib.ConfigLoader.ConfigLoader')
    @patch('modules.abstract_module.AILQueue')
    @patch('logging.getLogger')
    def test_init_logs_module_initialization(self, mock_get_logger, mock_ail_queue, mock_config_loader_class):
        """__init__ should log module initialization."""
        mock_config_loader = MagicMock()
        mock_config_loader_class.return_value = mock_config_loader
        mock_config_loader.get_config_int.return_value = 8
        
        # Mock AILQueue to avoid queue setup issues
        mock_queue_instance = MagicMock()
        mock_ail_queue.return_value = mock_queue_instance
        
        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Create module and verify logger.info was called
        module = PhashCorrelation()
        # Verify logger.info was called during initialization
        mock_logger.info.assert_called_once()
        # Verify it contains module name
        call_args = mock_logger.info.call_args[0][0]
        self.assertIn('Module', call_args)
        self.assertIn('initialized', call_args)


class TestModulePhashCorrelationFindSimilar(unittest.TestCase):
    """Test PhashCorrelation.find_similar_phashes() method."""

    def setUp(self):
        """Set up test module with mocked config."""
        with patch('lib.ConfigLoader.ConfigLoader') as mock_config_loader_class:
            mock_config_loader = MagicMock()
            mock_config_loader_class.return_value = mock_config_loader
            mock_config_loader.get_config_int.return_value = 8
            self.module = PhashCorrelation()

    @patch('modules.PhashCorrelation.Phashs.compare_phash')
    @patch('modules.PhashCorrelation.Phashs')
    def test_find_similar_phashes_skips_self(self, mock_phashes_module, mock_compare_phash):
        """find_similar_phashes() should skip comparing phash to itself."""
        # Create mock phash objects
        mock_phash_self = MagicMock()
        mock_phash_self.id = 'abc123'
        mock_phash_self.exists.return_value = True
        
        mock_phash_other = MagicMock()
        mock_phash_other.id = 'def456'
        mock_phash_other.exists.return_value = True
        
        # Mock Phashs.Phashs() to return instance with get_iterator()
        mock_phashes_class = MagicMock()
        mock_phashes_instance = MagicMock()
        mock_phashes_class.return_value = mock_phashes_instance
        mock_phashes_instance.get_iterator.return_value = [mock_phash_self, mock_phash_other]
        mock_phashes_module.Phashs = mock_phashes_class
        
        # Mock compare_phash to return distance
        mock_compare_phash.return_value = 5
        
        result = self.module.find_similar_phashes('abc123', max_hamming_distance=10)
        
        # Should only compare with 'def456', not 'abc123' (self)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'def456')
        # Should not have called compare_phash with self
        mock_compare_phash.assert_called_once_with('abc123', 'def456')

    @patch('modules.PhashCorrelation.Phashs.compare_phash')
    @patch('modules.PhashCorrelation.Phashs')
    def test_find_similar_phashes_skips_nonexistent(self, mock_phashes_module, mock_compare_phash):
        """find_similar_phashes() should skip phash objects that don't exist."""
        # Create mock phash objects
        mock_phash_existing = MagicMock()
        mock_phash_existing.id = 'abc123'
        mock_phash_existing.exists.return_value = True
        
        mock_phash_nonexistent = MagicMock()
        mock_phash_nonexistent.id = 'def456'
        mock_phash_nonexistent.exists.return_value = False  # Doesn't exist
        
        # Mock Phashs.Phashs() to return instance with get_iterator()
        mock_phashes_class = MagicMock()
        mock_phashes_instance = MagicMock()
        mock_phashes_class.return_value = mock_phashes_instance
        mock_phashes_instance.get_iterator.return_value = [mock_phash_existing, mock_phash_nonexistent]
        mock_phashes_module.Phashs = mock_phashes_class
        
        mock_compare_phash.return_value = 5
        
        result = self.module.find_similar_phashes('xyz789', max_hamming_distance=10)
        
        # Should only process existing phash, not nonexistent one
        mock_compare_phash.assert_called_once_with('xyz789', 'abc123')
        # nonexistent phash should not be compared
        self.assertNotIn('def456', [r[0] for r in result])

    @patch('modules.PhashCorrelation.Phashs.compare_phash')
    @patch('modules.PhashCorrelation.Phashs')
    def test_find_similar_phashes_filters_by_distance(self, mock_phashes_module, mock_compare_phash):
        """find_similar_phashes() should only return phashes within max_hamming_distance."""
        # Create mock phash objects with different distances
        mock_phash_close = MagicMock()
        mock_phash_close.id = 'close123'
        mock_phash_close.exists.return_value = True
        
        mock_phash_far = MagicMock()
        mock_phash_far.id = 'far456'
        mock_phash_far.exists.return_value = True
        
        # Mock Phashs.Phashs() to return instance with get_iterator()
        mock_phashes_class = MagicMock()
        mock_phashes_instance = MagicMock()
        mock_phashes_class.return_value = mock_phashes_instance
        mock_phashes_instance.get_iterator.return_value = [mock_phash_close, mock_phash_far]
        mock_phashes_module.Phashs = mock_phashes_class
        
        # Mock compare_phash to return different distances
        def compare_side_effect(phash1, phash2):
            if phash2 == 'close123':
                return 5  # Within distance (max=10)
            elif phash2 == 'far456':
                return 15  # Too far (max=10)
            return None
        
        mock_compare_phash.side_effect = compare_side_effect
        
        result = self.module.find_similar_phashes('test789', max_hamming_distance=10)
        
        # Should only include 'close123' (distance 5), not 'far456' (distance 15)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'close123')
        self.assertEqual(result[0][1], 5)

    @patch('modules.PhashCorrelation.Phashs.compare_phash')
    @patch('modules.PhashCorrelation.Phashs')
    def test_find_similar_phashes_handles_none_distance(self, mock_phashes_module, mock_compare_phash):
        """find_similar_phashes() should skip phashes when compare_phash returns None."""
        mock_phash = MagicMock()
        mock_phash.id = 'test123'
        mock_phash.exists.return_value = True
        
        # Mock Phashs.Phashs() to return instance with get_iterator()
        mock_phashes_class = MagicMock()
        mock_phashes_instance = MagicMock()
        mock_phashes_class.return_value = mock_phashes_instance
        mock_phashes_instance.get_iterator.return_value = [mock_phash]
        mock_phashes_module.Phashs = mock_phashes_class
        
        # Mock compare_phash to return None (invalid phash)
        mock_compare_phash.return_value = None
        
        result = self.module.find_similar_phashes('abc456', max_hamming_distance=10)
        
        # Should return empty list when distance is None
        self.assertEqual(result, [])

    def test_find_similar_phashes_returns_empty_for_empty_phash_value(self):
        """find_similar_phashes() should return [] for empty phash_value."""
        result = self.module.find_similar_phashes('', max_hamming_distance=10)
        self.assertEqual(result, [])
        
        result = self.module.find_similar_phashes(None, max_hamming_distance=10)
        self.assertEqual(result, [])

    @patch('modules.PhashCorrelation.Phashs.compare_phash')
    @patch('modules.PhashCorrelation.Phashs')
    def test_find_similar_phashes_uses_module_default_distance(self, mock_phashes_module, mock_compare_phash):
        """find_similar_phashes() should use module's max_hamming_distance when not provided."""
        mock_phash = MagicMock()
        mock_phash.id = 'test123'
        mock_phash.exists.return_value = True
        
        # Mock Phashs.Phashs() to return instance with get_iterator()
        mock_phashes_class = MagicMock()
        mock_phashes_instance = MagicMock()
        mock_phashes_class.return_value = mock_phashes_instance
        mock_phashes_instance.get_iterator.return_value = [mock_phash]
        mock_phashes_module.Phashs = mock_phashes_class
        
        mock_compare_phash.return_value = 5
        
        # Call without max_hamming_distance parameter
        result = self.module.find_similar_phashes('abc456')
        
        # Should use module's default (8) from setUp
        mock_compare_phash.assert_called_once_with('abc456', 'test123')
        self.assertEqual(len(result), 1)  # Distance 5 <= 8, so included


class TestModulePhashCorrelationCompute(unittest.TestCase):
    """Test PhashCorrelation.compute() method."""
    
    # Real phash values are 16-character hex strings from imagehash
    # Example: 'c6073f39b0949d4b' or '8000000000000000'
    PHASH_1 = 'c6073f39b0949d4b'  # Current phash
    PHASH_2 = 'def4567890abcdef0'  # Similar phash 1
    PHASH_3 = '1234567890abcdef'   # Similar phash 2
    PHASH_4 = 'fedcba0987654321'   # Non-existent phash

    def setUp(self):
        """Set up test module with mocked config."""
        with patch('lib.ConfigLoader.ConfigLoader') as mock_config_loader_class:
            mock_config_loader = MagicMock()
            mock_config_loader_class.return_value = mock_config_loader
            mock_config_loader.get_config_int.return_value = 8
            self.module = PhashCorrelation()

    def test_compute_returns_none_if_not_phash_object(self):
        """compute() should return None if object type is not 'phash'.
        
        Note: The 'message' parameter is the date (e.g., '20240101') but is not
        used in compute() - it's just stored in the 'date' variable.
        """
        # Mock a non-phash object
        mock_obj = MagicMock()
        mock_obj.type = 'image'  # Not 'phash'
        self.module.obj = mock_obj
        
        result = self.module.compute('20240101')  # Date message (not used in compute)
        
        self.assertIsNone(result)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_calls_find_similar_phashes_with_correct_value(self, mock_phashes_module):
        """compute() should call find_similar_phashes() with the phash object's id."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        mock_phash_obj.is_correlated.return_value = False
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to return empty list
        self.module.find_similar_phashes = MagicMock(return_value=[])
        
        self.module.compute('20240101')
        
        # Should call find_similar_phashes with the phash id
        self.module.find_similar_phashes.assert_called_once_with(self.PHASH_1)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_creates_correlations_for_similar_phashes(self, mock_phashes_module):
        """compute() should create correlations for similar phashes."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        mock_phash_obj.is_correlated.return_value = False
        self.module.obj = mock_phash_obj
        
        # Mock logger so we can assert on debug calls
        self.module.logger = MagicMock()
        
        # Mock find_similar_phashes to return similar phashes (with realistic hex values)
        self.module.find_similar_phashes = MagicMock(return_value=[
            (self.PHASH_2, 5),  # Similar phash 1, distance 5
            (self.PHASH_3, 3)   # Similar phash 2, distance 3
        ])
        
        # Mock Phash objects for similar phashes
        mock_similar_phash1 = MagicMock()
        mock_similar_phash1.exists.return_value = True
        
        mock_similar_phash2 = MagicMock()
        mock_similar_phash2.exists.return_value = True
        
        mock_phashes_class = MagicMock()
        mock_phashes_module.Phash = mock_phashes_class
        mock_phashes_class.side_effect = [mock_similar_phash1, mock_similar_phash2]
        
        self.module.compute('20240101')
        
        # Should create correlations for both similar phashes
        self.assertEqual(mock_phash_obj.add_correlation.call_count, 2)
        mock_phash_obj.add_correlation.assert_any_call('phash', '', self.PHASH_2)
        mock_phash_obj.add_correlation.assert_any_call('phash', '', self.PHASH_3)
        # Verify debug logging was called for each correlation
        self.assertEqual(self.module.logger.debug.call_count, 2)
        # Verify debug messages contain phash values
        debug_calls = [call[0][0] for call in self.module.logger.debug.call_args_list]
        self.assertTrue(any(self.PHASH_1 in msg and self.PHASH_2 in msg for msg in debug_calls))
        self.assertTrue(any(self.PHASH_1 in msg and self.PHASH_3 in msg for msg in debug_calls))

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_skips_self_correlation(self, mock_phashes_module):
        """compute() should skip creating correlation with itself."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        mock_phash_obj.is_correlated.return_value = False
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to return self (shouldn't happen, but test the check)
        self.module.find_similar_phashes = MagicMock(return_value=[
            (self.PHASH_1, 0),  # Self - should be skipped
            (self.PHASH_2, 5)   # Other - should be processed
        ])
        
        # Mock Phash object for similar phash
        mock_similar_phash = MagicMock()
        mock_similar_phash.exists.return_value = True
        
        mock_phashes_class = MagicMock()
        mock_phashes_module.Phash = mock_phashes_class
        mock_phashes_class.return_value = mock_similar_phash
        
        self.module.compute('20240101')
        
        # Should only create correlation for PHASH_2, not PHASH_1 (self)
        mock_phash_obj.add_correlation.assert_called_once_with('phash', '', self.PHASH_2)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_skips_nonexistent_similar_phash_objects(self, mock_phashes_module):
        """compute() should skip similar phash objects that don't exist."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        mock_phash_obj.is_correlated.return_value = False
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to return similar phashes
        self.module.find_similar_phashes = MagicMock(return_value=[
            (self.PHASH_2, 5),  # Exists
            (self.PHASH_4, 3)   # Doesn't exist
        ])
        
        # Mock Phash objects - first exists, second doesn't
        mock_existing_phash = MagicMock()
        mock_existing_phash.exists.return_value = True
        
        mock_nonexistent_phash = MagicMock()
        mock_nonexistent_phash.exists.return_value = False
        
        mock_phashes_class = MagicMock()
        mock_phashes_module.Phash = mock_phashes_class
        mock_phashes_class.side_effect = [mock_existing_phash, mock_nonexistent_phash]
        
        self.module.compute('20240101')
        
        # Should only create correlation for existing phash
        mock_phash_obj.add_correlation.assert_called_once_with('phash', '', self.PHASH_2)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_skips_if_correlation_already_exists(self, mock_phashes_module):
        """compute() should skip creating correlation if it already exists."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to return similar phashes
        self.module.find_similar_phashes = MagicMock(return_value=[
            (self.PHASH_2, 5),
            (self.PHASH_3, 3)
        ])
        
        # Mock is_correlated - first doesn't exist, second already exists
        def is_correlated_side_effect(type2, subtype2, id2):
            if id2 == self.PHASH_2:
                return False  # Doesn't exist yet
            elif id2 == self.PHASH_3:
                return True   # Already exists
            return False
        mock_phash_obj.is_correlated.side_effect = is_correlated_side_effect
        
        # Mock Phash objects
        mock_similar_phash1 = MagicMock()
        mock_similar_phash1.exists.return_value = True
        
        mock_similar_phash2 = MagicMock()
        mock_similar_phash2.exists.return_value = True
        
        mock_phashes_class = MagicMock()
        mock_phashes_module.Phash = mock_phashes_class
        mock_phashes_class.side_effect = [mock_similar_phash1, mock_similar_phash2]
        # add date as logs usually need one
        self.module.compute('20240101')
        
        # Should only create correlation for PHASH_2 (not PHASH_3 which already exists)
        mock_phash_obj.add_correlation.assert_called_once_with('phash', '', self.PHASH_2)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_handles_exceptions_gracefully(self, mock_phashes_module):
        """compute() should handle exceptions gracefully without crashing."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to raise an exception
        self.module.find_similar_phashes = MagicMock(side_effect=Exception("Database connection error"))
        
        # Should not raise exception, should log warning instead
        result = self.module.compute('20240101')
        
        # Should return None (or not raise)
        self.assertIsNone(result)
        # Exception should be caught and logged (we can't easily test logging, but we can test it doesn't crash)

    @patch('modules.PhashCorrelation.Phashs')
    def test_compute_handles_exception_in_add_correlation(self, mock_phashes_module):
        """compute() should handle exceptions during add_correlation gracefully."""
        # Mock phash object with realistic phash value
        mock_phash_obj = MagicMock()
        mock_phash_obj.type = 'phash'
        mock_phash_obj.id = self.PHASH_1
        mock_phash_obj.is_correlated.return_value = False
        # Make add_correlation raise an exception
        mock_phash_obj.add_correlation.side_effect = Exception("Database write error")
        self.module.obj = mock_phash_obj
        
        # Mock find_similar_phashes to return similar phashes
        self.module.find_similar_phashes = MagicMock(return_value=[
            (self.PHASH_2, 5)
        ])
        
        # Mock Phash object
        mock_similar_phash = MagicMock()
        mock_similar_phash.exists.return_value = True
        
        mock_phashes_class = MagicMock()
        mock_phashes_module.Phash = mock_phashes_class
        mock_phashes_class.return_value = mock_similar_phash
        
        # Should not raise exception, should catch and log
        result = self.module.compute('20240101')
        
        # Should not crash
        self.assertIsNone(result)


class TestModuleImagePhash(unittest.TestCase):
    """Test ImagePhash module initialization."""

    @patch('modules.abstract_module.AILQueue')
    def test_init_sets_pending_seconds(self, mock_ail_queue):
        """__init__ should set pending_seconds to 1."""
        # Mock AILQueue to avoid config requirements
        mock_queue_instance = MagicMock()
        mock_ail_queue.return_value = mock_queue_instance
        
        module = ImagePhash()
        self.assertEqual(module.pending_seconds, 1)


class TestModuleImagePhashCompute(unittest.TestCase):
    """Test ImagePhash.compute() method."""
    
    # Real phash values are 16-character hex strings from imagehash
    PHASH_VALUE = 'c6073f39b0949d4b'  # Example phash value

    def setUp(self):
        """Set up test module."""
        with patch('modules.abstract_module.AILQueue') as mock_ail_queue:
            # Mock AILQueue to avoid config requirements
            mock_queue_instance = MagicMock()
            mock_ail_queue.return_value = mock_queue_instance
            self.module = ImagePhash()

    @patch('modules.ImagePhash.Phashs.calculate_phash_from_filepath')
    def test_compute_returns_none_if_phash_calculation_fails(self, mock_calc_phash):
        """compute() should return None if phash calculation fails."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_calc_phash.return_value = None
        self.module.obj = mock_image

        result = self.module.compute('20240101')

        self.assertIsNone(result)
        mock_calc_phash.assert_called_once_with('/path/to/image')

    @patch('modules.ImagePhash.Phashs')
    def test_compute_does_not_store_phash_on_image_metadata(self, mock_phashes_module):
        """compute() uses correlation only; does not store phash on image metadata."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_phashes_module.calculate_phash_from_filepath.return_value = self.PHASH_VALUE
        mock_phash_obj = MagicMock()
        mock_phashes_module.create.return_value = mock_phash_obj
        self.module.obj = mock_image
        self.module.add_message_to_queue = MagicMock()

        self.module.compute('20240101')

        # Phash is not stored on image; retrieval is via get_correlation('phash').get('phash')
        self.assertFalse(mock_image.set_phash.called)

    @patch('modules.ImagePhash.Phashs')
    def test_compute_creates_phash_object(self, mock_phashes_module):
        """compute() should create Phash object using Phashs.create()."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_phashes_module.calculate_phash_from_filepath.return_value = self.PHASH_VALUE
        mock_phash_obj = MagicMock()
        mock_phashes_module.create.return_value = mock_phash_obj
        self.module.obj = mock_image
        self.module.add_message_to_queue = MagicMock()

        self.module.compute('20240101')

        mock_phashes_module.calculate_phash_from_filepath.assert_called_once_with('/path/to/image')
        mock_phashes_module.create.assert_called_once_with(self.PHASH_VALUE)

    @patch('modules.ImagePhash.Phashs')
    def test_compute_creates_phash_image_correlation(self, mock_phashes_module):
        """compute() should create Phash ↔ Image correlation using add()."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_phashes_module.calculate_phash_from_filepath.return_value = self.PHASH_VALUE
        mock_phash_obj = MagicMock()
        mock_phashes_module.create.return_value = mock_phash_obj
        self.module.obj = mock_image
        self.module.add_message_to_queue = MagicMock()

        date = '20240101'
        self.module.compute(date)

        mock_phash_obj.add.assert_called_once_with(date, mock_image)

    @patch('modules.ImagePhash.Phashs')
    def test_compute_queues_phash_to_correlation_queue(self, mock_phashes_module):
        """compute() should queue Phash object to PhashCorrelation queue."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_phashes_module.calculate_phash_from_filepath.return_value = self.PHASH_VALUE
        mock_phash_obj = MagicMock()
        mock_phashes_module.create.return_value = mock_phash_obj
        self.module.obj = mock_image
        self.module.add_message_to_queue = MagicMock()

        date = '20240101'
        self.module.compute(date)

        self.module.add_message_to_queue.assert_called_once_with(
            obj=mock_phash_obj,
            queue='PhashCorrelation',
            message=date
        )

    @patch('modules.ImagePhash.Phashs.calculate_phash_from_filepath')
    def test_compute_propagates_exceptions_from_calculate_phash(self, mock_calc_phash):
        """compute() should propagate exceptions from phash calculation."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_calc_phash.side_effect = Exception("Database error")
        self.module.obj = mock_image

        with self.assertRaises(Exception) as context:
            self.module.compute('20240101')

        self.assertIn("Database error", str(context.exception))

    @patch('modules.ImagePhash.Phashs')
    def test_compute_complete_workflow(self, mock_phashes_module):
        """compute() should complete: calculate from filepath, create Phash, correlate, queue."""
        mock_image = MagicMock()
        mock_image.id = 'test_image_123'
        mock_image.get_filepath.return_value = '/path/to/image'
        mock_phashes_module.calculate_phash_from_filepath.return_value = self.PHASH_VALUE
        mock_phash_obj = MagicMock()
        mock_phashes_module.create.return_value = mock_phash_obj
        self.module.obj = mock_image
        self.module.add_message_to_queue = MagicMock()

        date = '20240101'
        self.module.compute(date)

        mock_phashes_module.calculate_phash_from_filepath.assert_called_once_with('/path/to/image')
        mock_phashes_module.create.assert_called_once_with(self.PHASH_VALUE)
        mock_phash_obj.add.assert_called_once_with(date, mock_image)
        self.module.add_message_to_queue.assert_called_once_with(
            obj=mock_phash_obj,
            queue='PhashCorrelation',
            message=date
        )


if __name__ == '__main__':
    unittest.main()
