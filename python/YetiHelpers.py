import os
import logging
from datetime import datetime

import pymel.core as pm

logger = logging.getLogger('YetiToolbox')

def change_location(location):

    sel = pm.ls(selection=True)
    for s in sel:
        shape = s.getShape()
        if shape.type() == 'pgYetiMaya':
            cache = shape.cacheFileName.get()
            rel = cache.split('/')[-2:]
            cache_new = os.path.join(location, '/'.join(rel))

            image = shape.imageSearchPath.get()
            rel = image.split('/')[-1:]
            image_new = os.path.join(location, '/'.join(rel))

            # check if path is valid
            if os.path.exists(cache_new):
                shape.cacheFileName.set(cache_new)
                logger.info('Changed {} -> {}'.format(cache, cache_new))
            else:
                logger.error('Error: path {} does not exist'.format(cache_new))

            if os.path.exists(image_new):
                shape.imageSearchPath.set(image_new)
                logger.info('Changed {} -> {}'.format(cache, image_new))
            else:
                logger.error('Error: path {} does not exist'.format(image_new))

def get_project_dir(_type=None):
    """
    Returns the project directory or a file rule path defined as type

    :param _type: fileRule type
    :type _type: str
    :return:
    """
    ws = pm.workspace
    if _type:
        return os.path.join(ws.getPath(), ws.fileRules[_type])
    else:
        return ws.getPath()

def get_time_range():
    start = pm.playbackOptions(ast=True, query=True)
    end = pm.playbackOptions(aet=True, query=True)

    return start, end

def get_selection():
    return pm.selected()

def get_yeti_nodes(selection=False):
    """
    Return list of yeti nodes in the scene or selection
    :param selection:
    :return:
    """
    data = []
    if isinstance(selection, list):
        selected = selection
    elif isinstance(selection, bool):
        selected = pm.selected()
    else:
        data = pm.ls(type='pgYetiMaya')

    if not data:
        for s in selected:
            if s.type() == 'pgYetiMaya':
                data.append(s)
                continue
            try:
                shape = s.getShape()
            except AttributeError:
                continue
            if shape.type() == 'pgYetiMaya':
                data.append(shape)

    return data

def set_image_path(path, selection=False):
    """
    Set image path of yeti nodes in scene or selection
    :param path:
    :param selection:
    :return:
    """
    nodes = get_yeti_nodes(selection=selection)
    for n in nodes:
        n.imageSearchPath.set(str(path))

def get_input_cache(node):
    return node.cacheFileName.get()

def create_cache(node, _range=(1, 3), samples=3, cache_dir=None):
    """
    create cache for yeti node
    :param node:
    :return:
    """
    # select the node
    pm.select(node)
    # create output file name
    file_name = node.getParent().name().replace(':', '_')
    file_name += '.%04d.fur'
    # Set the output directory if not defined
    # and create it if needed
    if not cache_dir:
        cache_dir = get_project_dir(_type='fileCache')
    else:
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
    file_name = os.path.join(cache_dir, file_name)
    logger.info('time range: {_range}, samples: {samples}'.format(_range=_range, samples=samples))

    # Check if we are either loaded a groom file or not using a loaded cache
    groom_file = node.cacheFileName.get()
    if groom_file:
        if groom_file.endswith('.grm'):
            try:
                node.YetiGroomFile.set(str(groom_file))
            except AttributeError:
                node.addAttr("YetiGroomFile", dt="string")
                node.YetiGroomFile.set(str(groom_file))
    elif node.fileMode.get() != 0:
        logger.info('You are already using a cache')
        return

    # Create cache
    logger.info('Writing cache: {}'.format(file_name))
    cmd = 'pgYetiCommand -writeCache "{file_path}" -range {start} {stop} -samples {samples}'
    pm.mel.eval(cmd.format(file_path=file_name, start=int(_range[0]), stop=int(_range[1]), samples=3))
    print 'cmd: ', cmd.format(file_path=file_name, start=int(_range[0]), stop=int(_range[1]), samples=3)
    # Add notes and original groom file to a custom attribute
    if groom_file:
        try:
            notes = node.notes.get()
        except AttributeError:
            node.addAttr('notes', dt="string")
            notes = '\n\n'
        notes += 'Original Yeti Cache from {time}:\n' \
                 '{cache_path}'.format(time=str(datetime.now()), cache_path=groom_file)
        node.notes.set(notes)
        logger.info('Added original groom file path to YetiGroomFile attribute')

    # Set file cache on node and change to Cache mode
    node.cacheFileName.set(file_name)
    node.fileMode.set(1)