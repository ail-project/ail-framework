#!/usr/bin/env python3
# -*-coding:UTF-8 -*

"""
ImagePhash Module
===================

Process images from the Image queue and:
1. Calculate perceptual hash (phash)
2. Store phash in Image metadata
3. Create Phash objects
4. Create Phash ↔ Image correlations

"""

import os
import sys

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from modules.abstract_module import AbstractModule
from lib.objects import Images
from lib.objects import Phashs


class ImagePhash(AbstractModule):
    """
    ImagePhash module: Calculate and store perceptual hashes for images
    """

    def __init__(self):
        super(ImagePhash, self).__init__()
        
        # Send to PhashCorrelation queue
        self.obj = None

    def compute(self, message, r_result=False):
        """
        Process an image and calculate its phash.
        
        Args:
            message: Image ID
            r_result: Return result for testing
        """
        image_id = message
        
        # Get image object
        image = Images.Image(image_id)
        
        if not image.exists():
            return None
        
        # Get image content
        image_content = image.get_content(r_type='bytes')
        
        if not image_content:
            return None
        
        # Calculate phash
        phash_value = Phashs.calculate_phash(image_content)
        
        if not phash_value:
            # imagehash library not available or calculation failed
            return None
        
        # Create Phash object
        phash_obj = Phashs.create(phash_value)
        
        # Add correlation: Phash ↔ Image
        phash_obj.add_correlation('image', '', image_id)
        
        # Send to PhashCorrelation queue for similarity detection
        self.send_message_to_queue(phash_value, 'PhashCorrelation')
        
        if r_result:
            return phash_value
        
        return None


if __name__ == '__main__':
    module = ImagePhash()
    module.run()
