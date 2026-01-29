#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
from lib.objects import Phashs

# Get test config
config_loader = ConfigLoader()
r_objects = config_loader.get_db_conn("Kvrocks_Objects")


class TestPhashObject(unittest.TestCase):
    """Test Phash object functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_phash = "a1b2c3d4e5f67890"
        self.phash_obj = Phashs.Phash(self.test_phash)
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up test phash object
        if self.phash_obj.exists():
            r_objects.delete(f'meta:phash:{self.test_phash}')
        
        # Clean up BK-tree index
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            # Clean up all children keys for test phashes
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)

    def test_phash_creation(self):
        """Test creating a Phash object"""
        self.assertFalse(self.phash_obj.exists())
        
        self.phash_obj.create()
        self.assertTrue(self.phash_obj.exists())
        
    def test_phash_get_id(self):
        """Test getting Phash ID"""
        self.assertEqual(self.phash_obj.get_id(), self.test_phash)
        
    def test_phash_get_type(self):
        """Test getting Phash type"""
        self.assertEqual(self.phash_obj.get_type(), 'phash')
        
    def test_phash_get_link(self):
        """Test getting Phash link"""
        link = self.phash_obj.get_link()
        self.assertIn('phash', link)
        self.assertIn(self.test_phash, link)
        
    def test_phash_get_meta(self):
        """Test getting Phash metadata"""
        self.phash_obj.create()
        meta = self.phash_obj.get_meta()
        
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta['id'], self.test_phash)
        self.assertIn('tags', meta)


class TestHammingDistance(unittest.TestCase):
    """Test Hamming distance calculation"""

    def test_hamming_distance_identical(self):
        """Test Hamming distance for identical phashes"""
        phash1 = "a1b2c3d4e5f67890"
        phash2 = "a1b2c3d4e5f67890"
        distance = Phashs.hamming_distance(phash1, phash2)
        self.assertEqual(distance, 0)
        
    def test_hamming_distance_different(self):
        """Test Hamming distance for different phashes"""
        phash1 = "0000000000000000"
        phash2 = "ffffffffffffffff"
        distance = Phashs.hamming_distance(phash1, phash2)
        self.assertEqual(distance, 64)  # All 64 bits different
        
    def test_hamming_distance_one_bit(self):
        """Test Hamming distance with one bit different"""
        phash1 = "0000000000000000"
        phash2 = "0000000000000001"
        distance = Phashs.hamming_distance(phash1, phash2)
        self.assertEqual(distance, 1)
        
    def test_hamming_distance_none_input(self):
        """Test Hamming distance with None input"""
        distance = Phashs.hamming_distance(None, "a1b2c3d4e5f67890")
        self.assertIsNone(distance)
        
        distance = Phashs.hamming_distance("a1b2c3d4e5f67890", None)
        self.assertIsNone(distance)
        
    def test_hamming_distance_different_lengths(self):
        """Test Hamming distance with different length inputs"""
        phash1 = "a1b2c3d4"
        phash2 = "a1b2c3d4e5f67890"
        distance = Phashs.hamming_distance(phash1, phash2)
        self.assertIsNone(distance)
        
    def test_hamming_distance_invalid_hex(self):
        """Test Hamming distance with invalid hex strings"""
        phash1 = "invalid_hex"
        phash2 = "a1b2c3d4e5f67890"
        distance = Phashs.hamming_distance(phash1, phash2)
        self.assertIsNone(distance)


class TestBKTreeIndexing(unittest.TestCase):
    """Test BK-tree indexing functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
                
    def tearDown(self):
        """Clean up after tests"""
        # Clean up BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
        
        # Clean up test phash objects
        for i in range(10):
            phash_id = f"000000000000000{i:x}"
            r_objects.delete(f'meta:phash:{phash_id}')

    def test_bktree_add_root(self):
        """Test adding root to BK-tree"""
        phash = "a1b2c3d4e5f67890"
        
        Phashs.add_to_bktree_index(phash)
        
        root = r_objects.get('phash:bktree:root')
        self.assertEqual(root, phash)
        
    def test_bktree_add_multiple(self):
        """Test adding multiple phashes to BK-tree"""
        phashes = [
            "0000000000000000",
            "0000000000000001",
            "0000000000000003",
            "00000000000000ff"
        ]
        
        for phash in phashes:
            Phashs.add_to_bktree_index(phash)
        
        root = r_objects.get('phash:bktree:root')
        self.assertEqual(root, phashes[0])
        
        # Check that children are added
        children_key = f'phash:bktree:{phashes[0]}:children'
        children = r_objects.hgetall(children_key)
        self.assertGreater(len(children), 0)
        
    def test_bktree_add_duplicate(self):
        """Test adding duplicate phash to BK-tree"""
        phash = "a1b2c3d4e5f67890"
        
        Phashs.add_to_bktree_index(phash)
        Phashs.add_to_bktree_index(phash)  # Add again
        
        root = r_objects.get('phash:bktree:root')
        self.assertEqual(root, phash)
        
        # Should not create children for duplicate
        children_key = f'phash:bktree:{phash}:children'
        children = r_objects.hgetall(children_key)
        self.assertEqual(len(children), 0)
        
    def test_bktree_add_none(self):
        """Test adding None to BK-tree"""
        Phashs.add_to_bktree_index(None)
        
        root = r_objects.get('phash:bktree:root')
        self.assertIsNone(root)


class TestBKTreeSearch(unittest.TestCase):
    """Test BK-tree search functionality"""

    def setUp(self):
        """Set up test fixtures with populated BK-tree"""
        # Clean up any existing BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
        
        # Build test tree with known phashes
        self.test_phashes = [
            "0000000000000000",  # Distance 0 from query
            "0000000000000001",  # Distance 1 from query
            "0000000000000003",  # Distance 2 from query
            "0000000000000007",  # Distance 3 from query
            "000000000000000f",  # Distance 4 from query
            "00000000000000ff",  # Distance 8 from query
            "0000000000000fff",  # Distance 12 from query
        ]
        
        for phash in self.test_phashes:
            Phashs.add_to_bktree_index(phash)
            
    def tearDown(self):
        """Clean up after tests"""
        # Clean up BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
        
        # Clean up test phash objects
        for phash in self.test_phashes:
            r_objects.delete(f'meta:phash:{phash}')

    def test_bktree_search_exact_match(self):
        """Test searching for exact match"""
        query = "0000000000000000"
        results = Phashs.search_bktree_index(query, max_distance=0)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], query)
        self.assertEqual(results[0][1], 0)
        
    def test_bktree_search_threshold_1(self):
        """Test searching with threshold 1"""
        query = "0000000000000000"
        results = Phashs.search_bktree_index(query, max_distance=1)
        
        # Should find phashes with distance 0 and 1
        distances = [r[1] for r in results]
        self.assertIn(0, distances)
        self.assertIn(1, distances)
        self.assertTrue(all(d <= 1 for d in distances))
        
    def test_bktree_search_threshold_8(self):
        """Test searching with default threshold 8"""
        query = "0000000000000000"
        results = Phashs.search_bktree_index(query, max_distance=8)
        
        # Should find multiple phashes
        self.assertGreater(len(results), 0)
        distances = [r[1] for r in results]
        self.assertTrue(all(d <= 8 for d in distances))
        
    def test_bktree_search_empty_tree(self):
        """Test searching in empty tree"""
        # Clean up tree
        r_objects.delete('phash:bktree:root')
        
        query = "0000000000000000"
        results = Phashs.search_bktree_index(query, max_distance=8)
        
        self.assertEqual(len(results), 0)
        
    def test_bktree_search_none_query(self):
        """Test searching with None query"""
        results = Phashs.search_bktree_index(None, max_distance=8)
        self.assertEqual(len(results), 0)
        
    def test_bktree_search_large_threshold(self):
        """Test searching with large threshold"""
        query = "0000000000000000"
        results = Phashs.search_bktree_index(query, max_distance=64)
        
        # Should find all phashes in tree
        self.assertGreater(len(results), 0)


class TestRebuildBKTreeIndex(unittest.TestCase):
    """Test BK-tree index rebuilding"""

    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
                
        # Create some test phash objects without adding to tree
        self.test_phashes = [
            "1111111111111111",
            "2222222222222222",
            "3333333333333333"
        ]
        
        for phash in self.test_phashes:
            obj = Phashs.Phash(phash)
            obj.create()
            
    def tearDown(self):
        """Clean up after tests"""
        # Clean up BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)
        
        # Clean up test phash objects
        for phash in self.test_phashes:
            r_objects.delete(f'meta:phash:{phash}')

    def test_rebuild_bktree_index(self):
        """Test rebuilding BK-tree index"""
        # Rebuild index
        count = Phashs.rebuild_bktree_index()
        
        # Should have indexed all test phashes
        self.assertGreaterEqual(count, len(self.test_phashes))
        
        # Root should be set
        root = r_objects.get('phash:bktree:root')
        self.assertIsNotNone(root)


class TestCalculatePhash(unittest.TestCase):
    """Test perceptual hash calculation"""

    def test_calculate_phash_none_input(self):
        """Test phash calculation with None input"""
        result = Phashs.calculate_phash(None)
        # Should return None if calculation fails
        self.assertIsNone(result)
        
    def test_calculate_phash_invalid_input(self):
        """Test phash calculation with invalid input"""
        result = Phashs.calculate_phash(b"invalid image data")
        # Should return None if calculation fails
        self.assertIsNone(result)


class TestCreatePhash(unittest.TestCase):
    """Test Phash object creation with index"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_phash = "9999999999999999"
        
    def tearDown(self):
        """Clean up after tests"""
        # Clean up test phash object
        r_objects.delete(f'meta:phash:{self.test_phash}')
        
        # Clean up BK-tree
        root = r_objects.get('phash:bktree:root')
        if root:
            r_objects.delete('phash:bktree:root')
            for key in r_objects.keys('phash:bktree:*:children'):
                r_objects.delete(key)

    def test_create_phash(self):
        """Test creating phash with automatic indexing"""
        obj = Phashs.create(self.test_phash)
        
        self.assertIsNotNone(obj)
        self.assertTrue(obj.exists())
        
        # Check that it was added to BK-tree
        root = r_objects.get('phash:bktree:root')
        self.assertIsNotNone(root)
        
    def test_create_phash_duplicate(self):
        """Test creating duplicate phash"""
        obj1 = Phashs.create(self.test_phash)
        obj2 = Phashs.create(self.test_phash)
        
        # Both should return same object
        self.assertEqual(obj1.get_id(), obj2.get_id())


class TestPhashs(unittest.TestCase):
    """Test Phashs collection class"""

    def test_phashs_get_name(self):
        """Test getting Phashs collection name"""
        phashs = Phashs.Phashs()
        self.assertEqual(phashs.get_name(), 'Phashs')
        
    def test_phashs_get_icon(self):
        """Test getting Phashs icon"""
        phashs = Phashs.Phashs()
        icon = phashs.get_icon()
        self.assertIsInstance(icon, dict)
        self.assertIn('icon', icon)
        
    def test_phashs_get_link(self):
        """Test getting Phashs link"""
        phashs = Phashs.Phashs()
        link = phashs.get_link()
        self.assertIn('phash', link)


if __name__ == '__main__':
    unittest.main()
