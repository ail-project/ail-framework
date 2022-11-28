#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import os
import sys

from flask import url_for
from hashlib import sha256

from pymisp import MISPObject, MISPAttribute

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
from lib.objects.abstract_subtype_object import AbstractSubtypeObject, get_all_id

config_loader = ConfigLoader()

config_loader = None

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


# http://rosettacode.org/wiki/Bitcoin/address_validation#Python
def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')


# http://rosettacode.org/wiki/Bitcoin/address_validation#Python
def check_base58_address(bc):
    try:
        bcbytes = decode_base58(bc, 25)
        return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
    except Exception:
        return False


class CryptoCurrency(AbstractSubtypeObject):
    """
    AIL CryptoCurrency Object. (strings)
    """

    def __init__(self, id, subtype):
        super(CryptoCurrency, self).__init__('cryptocurrency', id, subtype=subtype)

    # def get_ail_2_ail_payload(self):
    #     payload = {'raw': self.get_gzip_content(b64=True),
    #                 'compress': 'gzip'}
    #     return payload

    # # WARNING: UNCLEAN DELETE /!\ TEST ONLY /!\
    def delete(self):
        # # TODO:
        pass

    def is_valid_address(self):
        if self.type == 'bitcoin' or self.type == 'dash' or self.type == 'litecoin':
            return check_base58_address(self.id)
        else:
            return True

    def get_currency_symbol(self):
        if self.subtype == 'bitcoin':
            return 'BTC'
        elif self.subtype == 'ethereum':
            return 'ETH'
        elif self.subtype == 'bitcoin-cash':
            return 'BCH'
        elif self.subtype == 'litecoin':
            return 'LTC'
        elif self.subtype == 'monero':
            return 'XMR'
        elif self.subtype == 'zcash':
            return 'ZEC'
        elif self.subtype == 'dash':
            return 'DASH'
        return None

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, subtype=self.subtype, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&subtype={self.subtype}&id={self.id}'
        return url

    def get_svg_icon(self):
        if self.subtype == 'bitcoin':
            style = 'fab'
            icon = '\uf15a'
        elif self.subtype == 'monero':
            style = 'fab'
            icon = '\uf3d0'
        elif self.subtype == 'ethereum':
            style = 'fab'
            icon = '\uf42e'
        else:
            style = 'fas'
            icon = '\uf51e'
        return {'style': style, 'icon': icon, 'color': '#DDCC77', 'radius': 5}

    def get_misp_object(self):
        obj_attrs = []
        obj = MISPObject('coin-address')
        obj.first_seen = self.get_first_seen()
        obj.last_seen = self.get_last_seen()

        obj_attrs.append(obj.add_attribute('address', value=self.id))
        crypto_symbol = self.get_currency_symbol()
        if crypto_symbol:
            obj_attrs.append(obj.add_attribute('symbol', value=crypto_symbol))

        for obj_attr in obj_attrs:
            for tag in self.get_tags():
                obj_attr.add_tag(tag)
        return obj

    def get_meta(self, options=set()):
        meta = self._get_meta()
        meta['id'] = self.id
        meta['subtype'] = self.subtype
        meta['tags'] = self.get_tags(r_list=True)
        return meta

    ############################################################################
    ############################################################################


def get_all_subtypes():
    # return ail_core.get_object_all_subtypes(self.type)
    return ['bitcoin', 'bitcoin-cash', 'dash', 'ethereum', 'litecoin', 'monero', 'zcash']


# def build_crypto_regex(subtype, search_id):
#     pass
#
# def search_by_name(subtype, search_id): ##################################################
#
#     # # TODO: BUILD regex
#     obj = CryptoCurrency(subtype, search_id)
#     if obj.exists():
#         return search_id
#     else:
#         regex = build_crypto_regex(subtype, search_id)
#         return abstract_object.search_subtype_obj_by_id('cryptocurrency', subtype, regex)


def get_subtype_by_symbol(symbol):
    if symbol == 'BTC':
        return 'bitcoin'
    elif symbol == 'ETH':
        return 'ethereum'
    elif symbol == 'BCH':
        return 'bitcoin-cash'
    elif symbol == 'LTC':
        return 'litecoin'
    elif symbol == 'XMR':
        return 'monero'
    elif symbol == 'ZEC':
        return 'zcash'
    elif symbol == 'DASH':
        return 'dash'
    return None


# by days -> need first/last entry USEFUL FOR DATA RETENTION UI

def get_all_cryptocurrencies():
    cryptos = {}
    for subtype in get_all_subtypes():
        cryptos[subtype] = get_all_cryptocurrencies_by_subtype(subtype)
    return cryptos


def get_all_cryptocurrencies_by_subtype(subtype):
    return get_all_id('cryptocurrency', subtype)


# TODO save object
def import_misp_object(misp_obj):
    """
    :type misp_obj: MISPObject
    """
    obj_id = None
    obj_subtype = None
    for attribute in misp_obj.attributes:
        if attribute.object_relation == 'address':  # TODO: handle xmr address field
            obj_id = attribute.value
        elif attribute.object_relation == 'symbol':
            obj_subtype = get_subtype_by_symbol(attribute.value)
    if obj_id and obj_subtype:
        obj = CryptoCurrency(obj_id, obj_subtype)
        first_seen, last_seen = obj.get_misp_object_first_last_seen(misp_obj)
        tags = obj.get_misp_object_tags(misp_obj)
        # for tag in tags:
        #     obj.add_tag()


if __name__ == '__main__':
    res = get_all_cryptocurrencies()
    print(res)
