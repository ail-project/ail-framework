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
    AIL Phash Object.
    Represents a perceptual hash value for images.
    """

    def __init__(self, id):
        super(Phash, self).__init__('phash', id)

    def delete(self):
        # TODO: Implement delete functionality
        pass

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&id={self.id}'
        return url

    def get_svg_icon(self):
        # Icon for correlation graph visualization (like DomHash and HHHash)
        return {'style': 'fas', 'icon': '\uf1c0', 'color': '#E1F5DF', 'radius': 5}

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
        # Note: DomHash doesn't include tool attribute, HHHash does. Phash follows DomHash pattern.
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


def create(phash_value, obj_id=None):
    """
    Create or get Phash object.
    
    Args:
        phash_value: The phash string value
        obj_id: Optional phash ID (if None, uses phash_value as ID)
    
    Returns:
        Phash object
    """
    if obj_id is None:
        obj_id = phash_value
    obj = Phash(obj_id)
    if not obj.exists():
        obj.create()
    return obj


class Phashs(AbstractDaterangeObjects):
    """
    Phash Objects
    """
    def __init__(self):
        super().__init__('phash', Phash)

    def get_name(self):
        return 'Phashs'

    def get_icon(self):
        return {'fa': 'fa-solid', 'icon': 'image'}

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('objects_phash.objects_phashes')
        else:
            url = f'{baseurl}/objects/phashes'
        return url

    def sanitize_id_to_search(self, name_to_search):
        return name_to_search

