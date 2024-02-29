#!/usr/bin/env python3
# -*-coding:UTF-8 -*
import os
import sys

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.exceptions import AILObjectUnknown



from lib.ConfigLoader import ConfigLoader
from lib.ail_core import get_all_objects, get_object_all_subtypes, get_objects_with_subtypes
from lib import correlations_engine
from lib import relationships_engine
from lib import btc_ail
from lib import Tag

from lib.objects import Chats
from lib.objects import ChatSubChannels
from lib.objects import ChatThreads
from lib.objects import CryptoCurrencies
from lib.objects import CookiesNames
from lib.objects.Cves import Cve
from lib.objects.Decodeds import Decoded, get_all_decodeds_objects, get_nb_decodeds_objects
from lib.objects.Domains import Domain
from lib.objects import Etags
from lib.objects import Favicons
from lib.objects import FilesNames
from lib.objects import HHHashs
from lib.objects.Items import Item, get_all_items_objects, get_nb_items_objects
from lib.objects import Images
from lib.objects.Messages import Message
from lib.objects import Pgps
from lib.objects.Screenshots import Screenshot
from lib.objects import Titles
from lib.objects.UsersAccount import UserAccount
from lib.objects import Usernames

config_loader = ConfigLoader()

config_loader = None


def is_valid_object_type(obj_type):
    return obj_type in get_all_objects()

def is_object_subtype(obj_type):
    return obj_type in get_objects_with_subtypes()

def is_valid_object_subtype(obj_type, subtype):
    return subtype in get_object_all_subtypes(obj_type)

def sanitize_objs_types(objs):
    l_types = []
    for obj in objs:
        if is_valid_object_type(obj):
            l_types.append(obj)
    if not l_types:
        l_types = get_all_objects()
    return l_types

#### OBJECT ####

def get_object(obj_type, subtype, obj_id):
    if not subtype:
        if obj_type == 'item':
            return Item(obj_id)
        elif obj_type == 'domain':
            return Domain(obj_id)
        elif obj_type == 'decoded':
            return Decoded(obj_id)
        elif obj_type == 'cookie-name':
            return CookiesNames.CookieName(obj_id)
        elif obj_type == 'cve':
            return Cve(obj_id)
        elif obj_type == 'etag':
            return Etags.Etag(obj_id)
        elif obj_type == 'favicon':
            return Favicons.Favicon(obj_id)
        elif obj_type == 'file-name':
            return FilesNames.FileName(obj_id)
        elif obj_type == 'hhhash':
            return HHHashs.HHHash(obj_id)
        elif obj_type == 'image':
            return Images.Image(obj_id)
        elif obj_type == 'message':
            return Message(obj_id)
        elif obj_type == 'screenshot':
            return Screenshot(obj_id)
        elif obj_type == 'title':
            return Titles.Title(obj_id)
        else:
            raise AILObjectUnknown(f'Unknown AIL object: {obj_type} {subtype} {obj_id}')
    # SUBTYPES
    else:
        if obj_type == 'chat':
            return Chats.Chat(obj_id, subtype)
        elif obj_type == 'chat-subchannel':
            return ChatSubChannels.ChatSubChannel(obj_id, subtype)
        elif obj_type == 'chat-thread':
            return ChatThreads.ChatThread(obj_id, subtype)
        elif obj_type == 'cryptocurrency':
            return CryptoCurrencies.CryptoCurrency(obj_id, subtype)
        elif obj_type == 'pgp':
            return Pgps.Pgp(obj_id, subtype)
        elif obj_type == 'user-account':
            return UserAccount(obj_id, subtype)
        elif obj_type == 'username':
            return Usernames.Username(obj_id, subtype)
        else:
            raise AILObjectUnknown(f'Unknown AIL object: {obj_type} {subtype} {obj_id}')

def exists_obj(obj_type, subtype, obj_id):
    obj = get_object(obj_type, subtype, obj_id)
    if obj:
        return obj.exists()
    else:
        return False

#### API ####

def api_get_object(obj_type, obj_subtype, obj_id):
    if not obj_id:
        return {'status': 'error', 'reason': 'Invalid object id'}, 400
    if not is_valid_object_type(obj_type):
        return {'status': 'error', 'reason': 'Invalid object type'}, 400
    if obj_subtype:
        if not is_valid_object_subtype(obj_type, obj_subtype):
            return {'status': 'error', 'reason': 'Invalid object subtype'}, 400
    obj = get_object(obj_type, obj_subtype, obj_id)
    if not obj.exists():
        return {'status': 'error', 'reason': 'Object Not Found'}, 404
    options = {'chat', 'content', 'created_at', 'files-names', 'icon', 'images', 'info', 'nb_participants', 'parent', 'parent_meta', 'reactions', 'thread', 'user-account', 'username', 'subchannels', 'threads'}
    return obj.get_meta(options=options), 200


def api_get_object_type_id(obj_type, obj_id):
    if not is_valid_object_type(obj_type):
        return {'status': 'error', 'reason': 'Invalid object type'}, 400
    if is_object_subtype(obj_type):
        subtype, obj_id = obj_type.split('/', 1)
    else:
        subtype = None
    return api_get_object(obj_type, subtype, obj_id)


def api_get_object_global_id(global_id):
    obj_type, subtype, obj_id = global_id.split(':', 2)
    return api_get_object(obj_type, subtype, obj_id)

#### --API-- ####

#########################################################################################
#########################################################################################
#########################################################################################


def get_objects(objects): # TODO RENAME ME
    objs = set()
    for obj in objects:
        if isinstance(obj, dict):
            obj_type = obj['type']
            obj_subtype = obj['subtype']
            obj_id = obj['id']
            if 'lvl' in obj:
                correl_objs = get_obj_correlations_objs(obj_type, obj_subtype, obj_id, lvl=int(obj['lvl']))
                objs = objs.union(correl_objs)
        else:
            obj_type, obj_subtype, obj_id = obj
        objs.add((obj_type, obj_subtype, obj_id))
    ail_objects = []
    for obj in objs:
        ail_objects.append(get_object(obj[0], obj[1], obj[2]))
    return ail_objects


def get_obj_global_id(obj_type, subtype, obj_id):
    obj = get_object(obj_type, subtype, obj_id)
    return obj.get_global_id()

def get_obj_type_subtype_id_from_global_id(global_id):
    obj_type, subtype, obj_id = global_id.split(':', 2)
    return obj_type, subtype, obj_id

def get_obj_from_global_id(global_id):
    obj = get_obj_type_subtype_id_from_global_id(global_id)
    return get_object(obj[0], obj[1], obj[2])


def get_object_link(obj_type, subtype, id, flask_context=False):
    obj = get_object(obj_type, subtype, id)
    return obj.get_link(flask_context=flask_context)


def get_object_svg(obj_type, subtype, id):
    obj = get_object(obj_type, subtype, id)
    return obj.get_svg_icon()


## TAGS ##
def get_obj_tags(obj_type, subtype, id):
    obj = get_object(obj_type, subtype, id)
    return obj.get_tags()

def is_obj_tags_safe(obj_type, subtype, id):
    obj = get_object(obj_type, subtype, id)
    return obj.is_tags_safe()

def add_obj_tag(obj_type, subtype, id, tag):
    obj = get_object(obj_type, subtype, id)
    obj.add_tag(tag)


def add_obj_tags(obj_type, subtype, id, tags):
    obj = get_object(obj_type, subtype, id)
    for tag in tags:
        obj.add_tag(tag)


# -TAGS- #

def get_object_meta(obj_type, subtype, id, options=set(), flask_context=False):
    obj = get_object(obj_type, subtype, id)
    meta = obj.get_meta(options=options)
    meta['icon'] = obj.get_svg_icon()
    meta['link'] = obj.get_link(flask_context=flask_context)
    return meta


def get_objects_meta(objs, options=set(), flask_context=False):
    metas = []
    for obj in objs:
        if isinstance(obj, dict):
            obj_type = obj['type']
            subtype = obj['subtype']
            obj_id = obj['id']
        elif isinstance(obj, tuple):
            obj_type = obj[0]
            subtype = obj[1]
            obj_id = obj[2]
        else:
            obj_type, subtype, obj_id = get_obj_type_subtype_id_from_global_id(obj)
        metas.append(get_object_meta(obj_type, subtype, obj_id, options=options, flask_context=flask_context))
    return metas


def get_object_card_meta(obj_type, subtype, id, related_btc=False):
    obj = get_object(obj_type, subtype, id)
    meta = obj.get_meta()
    meta['icon'] = obj.get_svg_icon()
    if subtype or obj_type == 'cookie-name' or obj_type == 'cve' or obj_type == 'etag' or obj_type == 'title' or obj_type == 'favicon' or obj_type == 'hhhash':
        meta['sparkline'] = obj.get_sparkline()
        if obj_type == 'cve':
            meta['cve_search'] = obj.get_cve_search()
        # if obj_type == 'title':
        #     meta['cve_search'] = obj.get_cve_search()
    if subtype == 'bitcoin' and related_btc:
        meta["related_btc"] = btc_ail.get_bitcoin_info(obj.id)
    if obj.get_type() == 'decoded':
        meta['mimetype'] = obj.get_mimetype()
        meta['size'] = obj.get_size()
        meta["vt"] = obj.get_meta_vt()
        meta["vt"]["status"] = obj.is_vt_enabled()
    # TAGS MODAL
    meta["add_tags_modal"] = Tag.get_modal_add_tags(obj.id, obj.get_type(), obj.get_subtype(r_str=True))
    return meta


#### OBJ FILTERS ####

def is_filtered(obj, filters):
    if 'mimetypes' in filters:
        mimetype = obj.get_mimetype()
        if mimetype not in filters['mimetypes']:
            return True
    if 'sources' in filters:
        obj_source = obj.get_source()
        if obj_source not in filters['sources']:
            return True
    if 'subtypes' in filters:
        subtype = obj.get_subtype(r_str=True)
        if subtype not in filters['subtypes']:
            return True
    return False

def obj_iterator(obj_type, filters):
    if obj_type == 'decoded':
        return get_all_decodeds_objects(filters=filters)
    elif obj_type == 'item':
        return get_all_items_objects(filters=filters)
    elif obj_type == 'pgp':
        return Pgps.get_all_pgps_objects(filters=filters)

def card_objs_iterators(filters):
    nb = 0
    for obj_type in filters:
        nb += int(card_obj_iterator(obj_type, filters.get(obj_type, {})))
    return nb

def card_obj_iterator(obj_type, filters):
    if obj_type == 'decoded':
        return get_nb_decodeds_objects(filters=filters)
    elif obj_type == 'item':
        return get_nb_items_objects(filters=filters)
    elif obj_type == 'pgp':
        return Pgps.nb_all_pgps_objects(filters=filters)

def get_ui_obj_tag_table_keys(obj_type): # TODO REMOVE ME
    """
    Warning: use only in flask (dynamic templates)
    """
    if obj_type == "domain":
        return ['id', 'first_seen', 'last_check', 'status']  # # TODO: add root screenshot



# # # # MISP OBJECTS # # # #

# # TODO: CHECK IF object already have an UUID
def get_misp_object(obj_type, subtype, id):
    obj = get_object(obj_type, subtype, id)
    return obj.get_misp_object()


def get_misp_objects(objs):
    misp_objects = {}
    for obj in objs:
        misp_objects[obj] = obj.get_misp_object()
    for relation in get_objects_relationships(objs):
        obj_src = misp_objects[relation['src']]
        obj_dest = misp_objects[relation['dest']]
        # print(relation['src'].get_id(), relation['dest'].get_id())
        obj_src.add_reference(obj_dest.uuid, relation['relationship'], 'ail correlation')
    return misp_objects.values()

# get misp relationship
def get_objects_relationships(objs):
    relation = []
    if len(objs) == 2:
        if objs[0].are_correlated(objs[1]):
            relationship = get_objects_relationship(objs[0], objs[1])
            if relationship:
                relation.append(relationship)
    else:
        iterator = objs.copy()  # [obj1, obj2, obj3, obj4]
        for obj in objs[:-1]:  # [obj1, obj2, obj3]
            iterator.pop(0)  # [obj2, obj3, obj4] obj1 correlation already checked
            for obj2 in iterator:
                # CHECK CORRELATION obj - > obj2
                if obj.are_correlated(obj2):
                    relationship = get_objects_relationship(obj, obj2)
                    if relationship:
                        relation.append(relationship)
    return relation

def get_relationship_src_dest(src_type, obj1, obj2):
    if obj1.get_type() == src_type:
        src = obj1
        dest = obj2
    else:
        src = obj2
        dest = obj1
    return src, dest

# get misp relationship
def get_objects_relationship(obj1, obj2):
    obj_types = (obj1.get_type(), obj2.get_type())

    ##############################################################
    # if ['cryptocurrency', 'pgp', 'username', 'decoded', 'screenshot']:
    #     {'relation': '', 'src':, 'dest':}
    #     relationship[relation] =
    ##############################################################
    if 'cryptocurrency' in obj_types:
        relationship = 'extracted-from'
        src, dest = get_relationship_src_dest('cryptocurrency', obj1, obj2)
    elif 'cve' in obj_types:
        relationship = 'extracted-from'
        src, dest = get_relationship_src_dest('cve', obj1, obj2)
    elif 'pgp' in obj_types:
        relationship = 'extracted-from'
        src, dest = get_relationship_src_dest('pgp', obj1, obj2)
    elif 'username' in obj_types:
        relationship = 'extracted-from'
        src, dest = get_relationship_src_dest('username', obj1, obj2)
    elif 'decoded' in obj_types:
        relationship = 'included-in'
        src, dest = get_relationship_src_dest('decoded', obj1, obj2)
    elif 'screenshot' in obj_types:
        relationship = 'screenshot-of'
        src, dest = get_relationship_src_dest('screenshot', obj1, obj2)
    elif 'domain' in obj_types:
        relationship = 'extracted-from'
        src, dest = get_relationship_src_dest('domain', obj1, obj2)
    # default
    else:
        relationship = None
        src = None
        dest = None
    if not relationship:
        return {}
    else:
        return {'src': src, 'dest': dest, 'relationship': relationship}

# - - - MISP OBJECTS - - - #


def api_sanitize_object_type(obj_type):
    if not is_valid_object_type(obj_type):
        return {'status': 'error', 'reason': 'Incorrect object type'}, 400

#### CORRELATION ####

def get_obj_correlations(obj_type, subtype, obj_id):
    obj = get_object(obj_type, subtype, obj_id)
    return obj.get_correlations()

def _get_obj_correlations_objs(objs, obj_type, subtype, obj_id, filter_types, lvl, nb_max, objs_hidden):
    if len(objs) < nb_max or nb_max == 0:
        if lvl == 0:
            objs.add((obj_type, subtype, obj_id))

        elif lvl > 0 and (obj_type, subtype, obj_id) not in objs:  # Avoid looking for the same correlation
            objs.add((obj_type, subtype, obj_id))
            obj = get_object(obj_type, subtype, obj_id)
            correlations = obj.get_correlations(filter_types=filter_types)
            lvl = lvl - 1
            for obj2_type in correlations:
                for str_obj in correlations[obj2_type]:
                    obj2_subtype, obj2_id = str_obj.split(':', 1)
                    if get_obj_global_id(obj2_type, obj2_subtype, obj2_id) in objs_hidden:
                        continue  # filter object to hide
                    _get_obj_correlations_objs(objs, obj2_type, obj2_subtype, obj2_id, filter_types, lvl, nb_max, objs_hidden)

def get_obj_correlations_objs(obj_type, subtype, obj_id, filter_types=[], lvl=0, nb_max=300, objs_hidden=set()):
    objs = set()
    _get_obj_correlations_objs(objs, obj_type, subtype, obj_id, filter_types, int(lvl), nb_max, objs_hidden)
    return objs

def obj_correlations_objs_add_tags(obj_type, subtype, obj_id, tags, filter_types=[], lvl=0, nb_max=300, objs_hidden=set()):
    objs = get_obj_correlations_objs(obj_type, subtype, obj_id, filter_types=filter_types, lvl=lvl, nb_max=nb_max, objs_hidden=objs_hidden)
    # print(objs)
    for obj_tuple in objs:
        obj1_type, subtype1, id1 = obj_tuple
        add_obj_tags(obj1_type, subtype1, id1, tags)
    return objs

def get_obj_nb_correlations(obj_type, subtype, obj_id, filter_types=[]):
    obj = get_object(obj_type, subtype, obj_id)
    return obj.get_nb_correlations(filter_types=filter_types)

################################################################################
################################################################################ TODO
################################################################################

def delete_obj_correlations(obj_type, subtype, obj_id):
    obj = get_object(obj_type, subtype, obj_id)
    if obj.exists():
        return correlations_engine.delete_obj_correlations(obj_type, subtype, obj_id)

def delete_obj(obj_type, subtype, obj_id):
    obj = get_object(obj_type, subtype, obj_id)
    return obj.delete()


################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

def create_correlation_graph_links(links_set):
    links = []
    for link in links_set:
        links.append({"source": link[0], "target": link[1]})
    return links


def create_correlation_graph_nodes(nodes_set, obj_str_id, flask_context=True):
    graph_nodes_list = []
    for node_id in nodes_set:
        obj_type, subtype, obj_id = get_obj_type_subtype_id_from_global_id(node_id)
        dict_node = {'id': node_id}
        dict_node['style'] = get_object_svg(obj_type, subtype, obj_id)

        # # TODO: # FIXME: in UI
        dict_node['style']['icon_class'] = dict_node['style']['style']
        dict_node['style']['icon_text'] = dict_node['style']['icon']
        dict_node['style']['node_color'] = dict_node['style']['color']
        dict_node['style']['node_radius'] = dict_node['style']['radius']
        # # TODO: # FIXME: in UI

        dict_node['text'] = obj_id
        if node_id == obj_str_id:
            dict_node["style"]["node_color"] = 'orange'
            dict_node["style"]["node_radius"] = 7
        dict_node['url'] = get_object_link(obj_type, subtype, obj_id, flask_context=flask_context)
        graph_nodes_list.append(dict_node)
    return graph_nodes_list


def get_correlations_graph_node(obj_type, subtype, obj_id, filter_types=[], max_nodes=300, level=1,
                                objs_hidden=set(),
                                flask_context=False):
    obj_str_id, nodes, links, meta = correlations_engine.get_correlations_graph_nodes_links(obj_type, subtype, obj_id,
                                                                                            filter_types=filter_types,
                                                                                            max_nodes=max_nodes, level=level,
                                                                                            objs_hidden=objs_hidden,
                                                                                            flask_context=flask_context)
    # print(meta)
    meta['objs'] = list(meta['objs'])
    return {"nodes": create_correlation_graph_nodes(nodes, obj_str_id, flask_context=flask_context),
            "links": create_correlation_graph_links(links),
            "meta": meta}


# --- CORRELATION --- #

def get_obj_nb_relationships(obj_type, subtype, obj_id, filter_types=[]):
    obj = get_object(obj_type, subtype, obj_id)
    return obj.get_nb_relationships(filter=filter_types)

def get_relationships_graph_node(obj_type, subtype, obj_id, filter_types=[], max_nodes=300, level=1,
                                 objs_hidden=set(),
                                 flask_context=False):
    obj_global_id = get_obj_global_id(obj_type, subtype, obj_id)
    nodes, links, meta = relationships_engine.get_relationship_graph(obj_global_id,
                                                                    filter_types=filter_types,
                                                                    max_nodes=max_nodes, level=level,
                                                                    objs_hidden=objs_hidden)
    # print(meta)
    meta['objs'] = list(meta['objs'])
    return {"nodes": create_correlation_graph_nodes(nodes, obj_global_id, flask_context=flask_context),
            "links": links,
            "meta": meta}


# if __name__ == '__main__':
    # r = get_objects([{'lvl': 1, 'type': 'item', 'subtype': '', 'id': 'crawled/2020/09/14/circl.lu0f4976a4-dda4-4189-ba11-6618c4a8c951'}])
    # r = get_misp_objects([Item('crawled/2020/09/14/circl.lu0f4976a4-dda4-4189-ba11-6618c4a8c951'),
    #                       Cve('CVE-2020-16856'), Cve('CVE-2014-6585'), Cve('CVE-2015-0383'),
    #                       Cve('CVE-2015-0410')])
    # print()
    # print(r)

    # res = get_obj_correlations_objs('username', 'telegram', 'corona', lvl=100)
    # print(res)