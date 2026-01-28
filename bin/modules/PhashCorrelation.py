#!/usr/bin/env python3
# -*-coding:UTF-8 -*
"""
The PhashCorrelation Module
======================

Finds similar images by phash and creates correlations.
Processes images after phash has been calculated.
"""

##################################
# Import External packages
##################################
import os
import sys

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from modules.abstract_module import AbstractModule
from lib.objects import Phashs
from lib.objects import Images


class PhashCorrelation(AbstractModule):
    """
    PhashCorrelation module for AIL framework
    Finds similar Phash objects and creates Phash ↔ Phash correlations
    """

    def __init__(self):
        super(PhashCorrelation, self).__init__()

        # Waiting time in seconds between to message processed
        self.pending_seconds = 1

        # Send module state to logs
        self.logger.info(f'Module {self.module_name} initialized')
        
        # Load config for max hamming distance
        from lib.ConfigLoader import ConfigLoader
        config_loader = ConfigLoader()
        try:
            self.max_hamming_distance = config_loader.get_config_int("Images", "phash_max_hamming_distance")
        except:
            self.max_hamming_distance = 8  # Default value

    def find_similar_phashes(self, phash_value, max_hamming_distance=None):
        """
        Find all phash values similar to the given phash within hamming distance threshold.
        Queries all Phash objects from database and compares phash values.
        
        Args:
            phash_value: The phash string value to find similarities for
            max_hamming_distance: Maximum hamming distance (default: from module config, or 8)
        
        Returns:
            List of tuples: [(phash_value, hamming_distance), ...]
        """
        if max_hamming_distance is None:
            max_hamming_distance = self.max_hamming_distance
        
        if not phash_value:
            return []
        
        similar_phashes = []
        # Get all Phash objects
        for phash_obj in Phashs.Phashs().get_iterator():
            if phash_obj.id == phash_value:  # Skip self
                continue
            if not phash_obj.exists():
                continue
            
            other_phash_value = phash_obj.id
            # Use compare_phash utility function from Images module
            distance = Images.compare_phash(phash_value, other_phash_value)
            if distance is not None and distance <= max_hamming_distance:
                similar_phashes.append((other_phash_value, distance))
        
        return similar_phashes

    def compute(self, message):
        phash_obj = self.get_obj()
        date = message

        if phash_obj.type != 'phash':
            # Not a phash object, skip
            return None

        current_phash_value = phash_obj.id

        # Find similar phashes using hamming distance
        try:
            similar_phashes = self.find_similar_phashes(current_phash_value)
            
            # Create correlations for similar phashes
            for similar_phash_value, distance in similar_phashes:
                if similar_phash_value == current_phash_value:
                    continue  # Skip self
                
                similar_phash_obj = Phashs.Phash(similar_phash_value)
                if not similar_phash_obj.exists():
                    continue
                
                # Check if correlation already exists
                if not phash_obj.is_correlated('phash', '', similar_phash_value):
                    # Create bidirectional correlation
                    phash_obj.add_correlation('phash', '', similar_phash_value)
                    self.logger.debug(f'Created phash correlation: {current_phash_value} <-> {similar_phash_value} (distance: {distance})')
        
        except Exception as e:
            self.logger.warning(f'Error finding similar phashes for {current_phash_value}: {e}')


if __name__ == '__main__':

    module = PhashCorrelation()
    module.run()

