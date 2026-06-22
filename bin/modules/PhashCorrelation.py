#!/usr/bin/env python3
# -*-coding:UTF-8 -*

"""
PhashCorrelation Module
========================

Find similar phash values using BK-tree indexing and create correlations.

Features:
- Efficient similarity search using BK-tree (O(log n) vs O(n))
- Configurable Hamming distance threshold
- Graceful fallback to linear search if BK-tree fails
- Creates Phash ↔ Phash correlations

"""

import os
import sys

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from modules.abstract_module import AbstractModule
from lib.objects import Phashs
from lib.ConfigLoader import ConfigLoader


class PhashCorrelation(AbstractModule):
    """
    PhashCorrelation module: Find similar phashes using BK-tree indexing
    """

    def __init__(self):
        super(PhashCorrelation, self).__init__()
        
        # Load configuration
        config_loader = ConfigLoader()
        self.max_distance = config_loader.get_config_int('Images', 'phash_max_hamming_distance')
        if self.max_distance is None:
            self.max_distance = 8  # Default threshold
        config_loader = None
        
        self.obj = None

    def compute(self, message, r_result=False):
        """
        Find similar phashes using BK-tree search.
        
        Args:
            message: Phash value to search for
            r_result: Return result for testing
        """
        phash_value = message
        
        # Get Phash object
        phash_obj = Phashs.Phash(phash_value)
        
        if not phash_obj.exists():
            return None
        
        # Search for similar phashes using BK-tree
        similar_phashes = self._find_similar_phashes(phash_value)
        
        # Create correlations
        for similar_phash, distance in similar_phashes:
            # Don't correlate with self
            if similar_phash != phash_value:
                # Add bidirectional correlation: Phash ↔ Phash
                phash_obj.add_correlation('phash', '', similar_phash)
        
        if r_result:
            return similar_phashes
        
        return None
    
    def _find_similar_phashes(self, query_phash):
        """
        Find similar phashes using BK-tree index.
        
        Falls back to linear search if BK-tree search fails.
        
        Args:
            query_phash: Phash value to search for
        
        Returns:
            list: List of (phash_value, distance) tuples
        """
        try:
            # Try BK-tree search first (efficient)
            results = Phashs.search_bktree_index(query_phash, self.max_distance)
            
            if results:
                return results
            
            # If no results but tree might not be built yet, fall back
            return self._linear_search_fallback(query_phash)
            
        except Exception as e:
            # If BK-tree search fails, fall back to linear search
            self.logger.warning(f'BK-tree search failed, using linear fallback: {e}')
            return self._linear_search_fallback(query_phash)
    
    def _linear_search_fallback(self, query_phash):
        """
        Linear search fallback for when BK-tree is not available.
        
        This is much slower (O(n)) but ensures functionality.
        
        Args:
            query_phash: Phash value to search for
        
        Returns:
            list: List of (phash_value, distance) tuples
        """
        results = []
        
        # Iterate through all phashes
        phashs = Phashs.Phashs()
        for phash_id in phashs.get_ids_iterator():
            distance = Phashs.hamming_distance(query_phash, phash_id)
            
            if distance is not None and distance <= self.max_distance:
                results.append((phash_id, distance))
        
        return results


if __name__ == '__main__':
    module = PhashCorrelation()
    module.run()
