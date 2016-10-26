import maya.cmds as mc

import json
import os
import logging
import itertools

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_edits():
    """
    Get reference edits from a selection. Returns a dict with full attr name and values
    :return:
    """

    sel = mc.ls(selection=True)
    data = {}
    for i in sel:
        print i
        edits = mc.referenceQuery('{}'.format(i), editAttrs=True)
        for e in edits:
            attr_name = '{shape}.{attr}'.format(shape=i, attr=e)
            try:
                value = mc.getAttr(attr_name)
                attr_type = mc.getAttr(attr_name, type=True)
            # except if attr is message
            except RuntimeError:
                pass
            # except if attr is nodeInfo
            except ValueError:
                pass
            else:
                data[attr_name] = {'value': value, 'type': attr_type}
    return data

def export(tmp_dir='/tmp/tbt_maya'):

    # create a temp folder for our files
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    scene_path = mc.file(query=True, sceneName=True)
    if scene_path:
        _file_name = os.path.basename(scene_path)
    else:
        _file_name = 'export'

    _file = os.path.join(tmp_dir, '{}_edits.json'.format(_file_name))
    with open(_file, 'w') as f:
        json.dump(get_edits(), f)
        logger.info('Wrote file: %s' % _file)

def apply_edits(file_path, namespace_override=None):
    """
    Apply edits to a scene
    :param edits: edits dict
    :return:
    """

    namespaces = mc.namespaceInfo(listOnlyNamespaces=True)
    errors = []
    success = []
    invalid_types = ['float']

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            logger.info('Loaded: %s' % file_path)

        for k, v in data.iteritems():

            value = v['value']
            vtype = v['type']

            if isinstance(value, list):
                if isinstance(value[0], list):
                    value = list(itertools.chain.from_iterable(value))
            if isinstance(vtype, list):
                vsize = len(vtype)
                vtype = None
            else:
                vsize = None

            name_string = k.split(':')
            if len(name_string) < 2:
                namespace = None
            else:
                namespace = name_string[0]

            if namespace_override:
                # create new namespace with override
                if namespace:
                    k = namespace_override + ':' + name_string[1:]
                else:
                    k = namespace_override + ':' + k

                # set the new namespace
                namespace = namespace_override

            #logger.info('Using following namespace: {}'.format(namespace))
            try:
                print k, value, vtype
                if vsize:
                    mc.setAttr(k, *value, size=vsize)
                elif vtype:
                    if isinstance(value, list):
                        mc.setAttr(k, *value, type=vtype)
                    else:
                        if vtype in invalid_types:
                            mc.setAttr(k, value)
                        else:
                            mc.setAttr(k, value, type=vtype)
            except RuntimeError as e:
                print '#### ', e
                errors.append(e)
            else:
                success.append(k)
    else:
        logger.error('File path does not exist: %s' % file_path)