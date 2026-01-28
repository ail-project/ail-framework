#!/usr/bin/env python3
# -*-coding:UTF-8 -*
"""
The ImagePhash Module
======================

Calculates perceptual hash (phash) for images when they are imported.
Creates Phash objects and correlates them with Images.
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
from lib.objects import Images
from lib.objects import Phashs


class Phash(AbstractModule):
    """
    Phash module for AIL framework
    Calculates perceptual hash for images and creates Phash objects
    """

    def __init__(self):
        super(Phash, self).__init__()

        # Waiting time in seconds between to message processed
        self.pending_seconds = 1

        # Send module state to logs
        self.logger.info(f'Module {self.module_name} initialized')

    def compute(self, message):
        image = self.get_obj()
        date = message

        # Calculate phash
        phash_value = image.calculate_phash()
        if not phash_value:
            self.logger.warning(f'Failed to calculate phash for image {image.id}')
            return None

        # Store phash in image metadata (for backward compatibility and quick access)
        image.set_phash(phash_value)
        
        # Create or get Phash object
        phash_obj = Phashs.create(phash_value)
        
        # Correlate Phash ↔ Image (using add() which automatically creates correlation)
        phash_obj.add(date, image)
        
        self.logger.debug(f'Created Phash object {phash_value} for image {image.id}')
        
        # Queue Phash object for correlation processing
        self.add_message_to_queue(obj=phash_obj, queue='PhashCorrelation', message=date)


if __name__ == '__main__':

    module = Phash()
    module.run()

