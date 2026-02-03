#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import os
import sys

from flask import url_for
from pymisp import MISPObject

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
from lib.objects.abstract_daterange_object import AbstractDaterangeObject, AbstractDaterangeObjects

config_loader = ConfigLoader()
r_objects = config_loader.get_db_conn("Kvrocks_Objects")
baseurl = config_loader.get_config_str("Notifications", "ail_domain")
config_loader = None


class Phash(AbstractDaterangeObject):
    """
    AIL Perceptual Hash Object.
    """

    def __init__(self, phash_id):
        super(Phash, self).__init__('phash', phash_id)

    def delete(self):
        # TODO: Implement deletion
        pass

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&id={self.id}'
        return url

    def get_svg_icon(self):
        return {'style': 'fas', 'icon': '\uf302', 'color': '#4287f5', 'radius': 5}

    def get_misp_object(self):
        obj_attrs = []
        obj = MISPObject('phash')
        first_seen = self.get_first_seen()
        last_seen = self.get_last_seen()
        if first_seen:
            obj.first_seen = first_seen
        if last_seen:
            obj.last_seen = last_seen
        if not first_seen or not last_seen:
            self.logger.warning(
                f'Export error, None seen {self.type}:{self.subtype}:{self.id}, first={first_seen}, last={last_seen}')

        obj_attrs.append(obj.add_attribute('phash', value=self.get_id()))
        for obj_attr in obj_attrs:
            for tag in self.get_tags():
                obj_attr.add_tag(tag)
        return obj

    def get_nb_seen(self):
        return self.get_nb_correlation('image')

    def get_meta(self, options=set()):
        meta = self._get_meta(options=options)
        meta['id'] = self.id
        meta['tags'] = self.get_tags(r_list=True)
        return meta

    def create(self, _first_seen=None, _last_seen=None):
        self._create()


def hamming_distance(phash1, phash2):
    """
    Calculate Hamming distance between two phash values.
    
    Args:
        phash1: First phash value (hex string)
        phash2: Second phash value (hex string)
    
    Returns:
        int: Hamming distance (0-64 for 16-character hex phash)
    """
    if not phash1 or not phash2:
        return None
    if len(phash1) != len(phash2):
        return None
    
    # Convert hex strings to integers and XOR them
    try:
        xor_result = int(phash1, 16) ^ int(phash2, 16)
        # Count the number of 1 bits
        distance = bin(xor_result).count('1')
        return distance
    except (ValueError, TypeError):
        return None


def calculate_phash(image_content):
    """
    Calculate perceptual hash for image content.
    
    Args:
        image_content: Image content as bytes or PIL Image
    
    Returns:
        str: Phash value as hex string, or None if calculation fails
    """
    try:
        import imagehash
        from PIL import Image
        from io import BytesIO
        
        # Handle bytes input
        if isinstance(image_content, bytes):
            image_content = Image.open(BytesIO(image_content))
        
        # Calculate phash
        phash_value = str(imagehash.phash(image_content))
        return phash_value
    except ImportError:
        return None
    except Exception:
        return None


def add_to_bktree_index(phash_value):
    """
    Add a phash value to the BK-tree index.
    
    The BK-tree is stored in KVRocks using:
    - phash:bktree:root - stores the root node phash
    - phash:bktree:{phash}:children - hash map storing distance -> child_phash
    
    Args:
        phash_value: Phash value to add to the index
    """
    if not phash_value:
        return
    
    # Check if root exists
    root = r_objects.get('phash:bktree:root')
    
    if not root:
        # First phash becomes the root
        r_objects.set('phash:bktree:root', phash_value)
        return
    
    # Traverse tree to find insertion point
    current = root
    while True:
        # Calculate distance from current node to new phash
        distance = hamming_distance(current, phash_value)
        
        if distance is None:
            return
        
        if distance == 0:
            # Duplicate phash, no need to add
            return
        
        # Check if child exists at this distance
        child_key = f'phash:bktree:{current}:children'
        child = r_objects.hget(child_key, str(distance))
        
        if not child:
            # No child at this distance, insert here
            r_objects.hset(child_key, str(distance), phash_value)
            return
        else:
            # Continue traversing
            current = child


def search_bktree_index(query_phash, max_distance):
    """
    Search the BK-tree index for similar phash values.
    
    Uses triangle inequality to prune branches:
    If |d(node, query) - d(node, child)| > max_distance, skip that subtree
    
    Args:
        query_phash: Phash value to search for
        max_distance: Maximum Hamming distance for matches
    
    Returns:
        list: List of (phash_value, distance) tuples for all matches
    """
    if not query_phash:
        return []
    
    root = r_objects.get('phash:bktree:root')
    if not root:
        # Empty tree
        return []
    
    results = []
    candidates = [root]
    
    while candidates:
        current = candidates.pop()
        
        # Calculate distance from current node to query
        distance = hamming_distance(current, query_phash)
        
        if distance is None:
            continue
        
        # If within threshold, add to results
        if distance <= max_distance:
            results.append((current, distance))
        
        # Get children of current node
        child_key = f'phash:bktree:{current}:children'
        children = r_objects.hgetall(child_key)
        
        if children:
            # Check each child
            for child_distance_str, child_phash in children.items():
                child_distance = int(child_distance_str)
                
                # Triangle inequality: only explore if it could contain matches
                # |d(node, query) - d(node, child)| <= d(query, child)
                # So if |d(node, query) - d(node, child)| > max_distance, skip
                if abs(distance - child_distance) <= max_distance:
                    candidates.append(child_phash)
    
    return results


def rebuild_bktree_index():
    """
    Rebuild the BK-tree index from all existing phash objects.
    
    This should be called:
    - After importing old data
    - After index corruption
    - During migration
    
    Returns:
        int: Number of phashes indexed
    """
    # Clear existing index
    root = r_objects.get('phash:bktree:root')
    if root:
        r_objects.delete('phash:bktree:root')
        # Clear all children keys - we'll need to iterate through all phashes
    
    # Get all phash objects
    phashs = Phashs()
    count = 0
    
    for phash_id in phashs.get_ids_iterator():
        add_to_bktree_index(phash_id)
        count += 1
    
    return count


def create(phash_value):
    """
    Create a Phash object and add it to the BK-tree index.
    
    Args:
        phash_value: Phash value (hex string)
    
    Returns:
        Phash: Phash object
    """
    obj = Phash(phash_value)
    if not obj.exists():
        obj.create()
        add_to_bktree_index(phash_value)
    return obj


class Phashs(AbstractDaterangeObjects):
    """
    Phashs Objects Collection
    """
    def __init__(self):
        super().__init__('phash', Phash)

    def get_name(self):
        return 'Phashs'

    def get_icon(self):
        return {'fas': 'fas', 'icon': 'fingerprint'}

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('objects_phash.objects_phashs')
        else:
            url = f'{baseurl}/objects/phashes'
        return url

    def sanitize_id_to_search(self, name_to_search):
        return name_to_search
