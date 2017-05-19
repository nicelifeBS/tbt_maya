import pymel.core as pm

import logging

RES_FINAL = (2048.0, 858.0)


SETTINGS = {
              'final': {'res': RES_FINAL,
                        'aa_samples': 10
                        },
              'draft': {'res': [RES_FINAL[0]/2, RES_FINAL[1]/2],
                        'aa_samples': 3},
              'final_oar': {'res': (4480, 1920),
                            'aa_samples': 10},
              }

# Rig types: currently two
head = 'head'
body = 'body'

# projectSetup
# setCamera
# renderPasses
# frameRange
# startFrame
# endFrame
# renderSettings

logger = logging.getLogger('tbt_settings')

def set_status(attr, value):
    pm.setAttr('tbt_settings.' + attr, value)


def get_status(node_name):
    """Get the status of settings in the scene from tbt_settings node"""
    try:
        attrs = pm.PyNode(node_name).listAttr(ud=True)
    except pm.MayaNodeError:
        create_node(node_name)
        return

    status = {}
    for i in attrs:
        status[str(i)] = i.get()

    return status


def create_node(node_name):
    """Node for our render settings to store data on attributes

    Args:
        node_name (str): node name
    """

    # if there is already a node in the scene by query all user defined attrs

    try:
        attrs = pm.PyNode(node_name).listAttr(ud=True)
    except pm.MayaNodeError:
        node = pm.createNode('', n=node_name)
    else:
        # update older nodes
        node = pm.PyNode(node_name)
        pm.lockNode(node, lock=False)
        attr_names = [x.name() for x in attrs]
        if 'tbt_settings.sceneName' not in attr_names:
            node.addAttr('sceneName', dt='string')
            logger.info('Added new attribute: sceneName')
        # pm.lockNode(node, lock=True)

        return

    node.addAttr('projectSetup', attributeType='bool')
    node.addAttr('setCamera', attributeType='bool')
    node.addAttr('renderPasses', attributeType='bool')
    node.addAttr('frameRange', attributeType='bool')
    node.addAttr('startFrame', attributeType='float')
    node.addAttr('endFrame', attributeType='float')
    node.addAttr('renderSettings', dt='string')
    node.addAttr('sceneName', dt='string')

    pm.lockNode(node, lock=True)


def setup_project(name=''):
    """projectSetup"""

    # get the scene instance
    scene = pm.Scene()

    # Set project fps
    pm.currentUnit(time='pal')

    # load arnold plugin
    pm.loadPlugin('mtoa.bundle')

    # Set render resolution
    scene.defaultResolution.aspectLock.set(0)
    set_render_settings('final')

    # set gamma to 1.0
    scene.defaultArnoldRenderOptions.display_gamma.set(1.0)
    scene.defaultArnoldRenderOptions.light_gamma.set(1.0)
    scene.defaultArnoldRenderOptions.shader_gamma.set(1.0)
    scene.defaultArnoldRenderOptions.texture_gamma.set(1.0)

    # set image folder structure
    scene.defaultRenderGlobals.imageFilePrefix.set('<Scene>/<RenderLayer>_<RenderPass>')
    # activate animation and set file name to filename.#.exr
    scene.defaultRenderGlobals.animation.set(True)
    scene.defaultRenderGlobals.putFrameBeforeExt.set(True)
    scene.defaultRenderGlobals.periodInExt.set(1)

    # Shutter open on start frame
    scene.defaultArnoldRenderOptions.range_type.set(0)
    # Enable motion blur
    scene.defaultArnoldRenderOptions.motion_blur_enable.set(1)
    # Display driver settings
    scene.defaultArnoldDriver.outputMode.set(2)
    scene.defaultArnoldDriver.mergeAOVs.set(1)
    if name: name = name + '_'
    scene.defaultArnoldDriver.prefix.set('<Scene>/{}<RenderLayer>'.format(name))
    # half precision exrs to save diskspace
    scene.defaultArnoldDriver.halfPrecision.set(1)

    # Set yeti plugin premel
    scene.defaultRenderGlobals.preMel.set('pgYetiPreRender')
    set_status('projectSetup', 1)


def setup_render_layer():
    """renderPasses"""

    # select head yeti and lightsetup
    select_ = [
        '*:Yeti_grp',
        '*:HorseHead',
        # '__lightsetup*', todo: need solution if group is not present
    ]

    pm.select(select_)
    try:
        pm.nodetypes.RenderLayer.findLayerByName('head')
    except:
        head_rl = pm.createRenderLayer(name='head', empty=False)

    try:
        pm.nodetypes.RenderLayer.findLayerByName('bridle')
    except:
        bridle_rl = pm.createRenderLayer(name='bridle', empty=False)

    # set overrides for head pass
    head_rl.setCurrent()
    pm.editRenderLayerAdjustment('*:Yeti_grp.visibility', 'head')
    pm.PyNode('*:Yeti_grp').visibility.set(1)
    pm.editRenderLayerAdjustment('*:layer_bridle.primaryVisibility', 'head')
    pm.PyNode('*:layer_bridle').primaryVisibility.set(0)
    pm.editRenderLayerAdjustment('*:layer_rein.primaryVisibility', 'head')
    pm.PyNode('*:layer_rein').primaryVisibility.set(0)

    # set override for bridle pass
    bridle_rl.setCurrent()
    pm.editRenderLayerAdjustment('*:layer_head.aiMatte', 'bridle')
    pm.PyNode('*:layer_head').aiMatte.set(1)
    pm.editRenderLayerAdjustment('*:Yeti_grp.visibility', 'bridle')
    pm.PyNode('*:Yeti_grp').visibility.set(0)

    # set the default layer active again
    default_rl = pm.nodetypes.RenderLayer.defaultRenderLayer()
    default_rl.setCurrent()
    # make the default render layer not renderable
    default_rl.renderable.set(0)
    set_status('renderPasses', 1)


def get_frame_range():
    """Get the start and end frame of the rendering

    Returns:
        tuple(float, float): Start and end frame of frame range
    """
    start = pm.SCENE.defaultRenderGlobals.startFrame.get()
    end = pm.SCENE.defaultRenderGlobals.endFrame.get()

    return start, end


def set_frame_range(start_frame, end_frame):
    """Set the frame range in the maya scene and the render globals"""

    # set timeline
    pm.animation.playbackOptions(ast=start_frame, aet=end_frame, min=start_frame, max=end_frame)
    # set the render globals
    pm.SCENE.defaultRenderGlobals.startFrame.set(start_frame)
    pm.SCENE.defaultRenderGlobals.endFrame.set(end_frame)
    set_status('startFrame', start_frame)
    set_status('endFrame', end_frame)
    set_status('frameRange', 1)


def set_aspect_ratio():
    """
    Set the film gate height of a selected camera based on our render
    resolution to meet the correct aspect ratio
    """
    sel = pm.ls(selection=True)
    if not sel:
        print 'Please select a camera'
        raise TypeError

    for shape in sel:
        try:
            shape = shape.getShape()
        except:
            continue
        if shape.type() == 'camera':
            # get the width of the film back
            width = shape.horizontalFilmAperture.get()
            # calculate the new width with our final render resolution
            new_width = width * (RES_FINAL[1] / RES_FINAL[0])
            # set the width
            shape.verticalFilmAperture.set(new_width)
            print 'Changed height of film gate to '.format(new_width)
            set_status('setCamera', 1)
            return


def preview_setup():
    """
    Set render settings to draft settings
    and disable motion blur
    """
    # get the scene instance
    scene = pm.Scene()

    set_render_settings('draft')
    scene.defaultArnoldRenderOptions.motion_blur_enable.set(0)
    set_status('renderSettings', 'draft')


def final_setup():
    """
    Set resolution and aa samples to final render resolution if settings were
    changed
    :return:
    """
    set_render_settings('final')
    set_status('renderSettings', 'final')


def final_oar_setup():
    set_render_settings('final_oar')
    set_status('renderSettings', 'final_oar')


def final_render_animation():
    # get the scene instance
    scene = pm.Scene()

    set_render_settings('final')
    # enable motion blur
    scene.defaultArnoldRenderOptions.motion_blur_enable.set(1)
    scene.defaultArnoldRenderOptions.range_type.set(0)
    scene.defaultArnoldRenderOptions.outputOverscan.set('10%')
    scene.defaultArnoldDriver.mergeAOVs.set(1)
    set_status('renderSettings', 'final_anim')


def set_render_settings(preset, pixel_ar=1.0):
    """Set render settings to preset value

    Args:
        preset (str):
        pixel_ar (float):
    """

    if preset in SETTINGS.keys():
        settings = SETTINGS[preset]
    else:
        return

    width, height = settings['res']

    # get the scene instance
    scene = pm.Scene()

    scene.defaultResolution.width.set(width)
    scene.defaultResolution.height.set(height)
    scene.defaultResolution.deviceAspectRatio.set(width / height)
    # samples
    scene.defaultArnoldRenderOptions.AASamples.set(settings['aa_samples'])
    scene.defaultArnoldRenderOptions.GIDiffuseSamples.set(4)
    # ray depth
    scene.defaultArnoldRenderOptions.GIDiffuseDepth.set(3)
    scene.defaultArnoldRenderOptions.GIGlossyDepth.set(3)
    scene.defaultArnoldRenderOptions.autoTransparencyDepth.set(4)
    scene.defaultArnoldRenderOptions.use_existing_tiled_textures.set(1)
    scene.defaultArnoldRenderOptions.textureAutomip.set(0)
    scene.defaultArnoldRenderOptions.log_verbosity.set(1)
    scene.defaultArnoldFilter.width.set(2.2)


def render_current_frame():
    start_f = pm.SCENE.defaultRenderGlobals.startFrame.get()
    end_f = pm.SCENE.defaultRenderGlobals.endFrame.get()
    current_frame = pm.currentTime()

    pm.SCENE.defaultRenderGlobals.startFrame.set(current_frame)
    pm.SCENE.defaultRenderGlobals.endFrame.set(current_frame)
    pm.mel.eval('mayaBatchRender();')
    # reset frame settings
    pm.SCENE.defaultRenderGlobals.startFrame.set(start_f)
    pm.SCENE.defaultRenderGlobals.endFrame.set(end_f)


def get_filename():
    """Return the scene name and scene extension"""
    scene_name = pm.sceneName()
    name, ext = scene_name.basename().splitext()
    return name, ext


def set_file_name(name):
    set_status('sceneName', name)
    pm.SCENE.defaultArnoldDriver.prefix.set('<Scene>/{}_<RenderLayer>'.format(name))


def get_frame_range():
    """Return the current used frame range in scene

    Returns:
        tuple (float, float): Frame range tuple
    """
    start = pm.playbackOptions(ast=True, query=True)
    end = pm.playbackOptions(aet=True, query=True)
    return start, end


def export_alembic_bake(start, stop, node, suffix=''):
    path = pm.workspace.getPath().joinpath(pm.workspace.fileRules['alembicCache'])
    path = path.joinpath(pm.sceneName().basename().splitext()[0] + suffix + '.abc')
    print 'export to: ', path
    print 'start frame: ', start
    print 'end frame: ', stop
    opt = '-frameRange {start} {stop} -noNormals -dataFormat ogawa -root |{node} -file \"{path}\"'
    pm.AbcExport(j=opt.format(
        start=start, stop=stop, node=node, path=path))


def write_alembic(path, proj_dir, rig_type=head):
    """Load maya scene update the horse rig to the latest version found in Horse_rig
    directory and then export an alembic cache.

    Args:
        path (str): File path of maya file
        proj_dir (str): Project directory
    """

    import glob
    import os
    import pymel.core as pm

    print 'Loading abc plugin'
    pm.loadPlugin('AbcExport.bundle')

    print 'Setting project to: ', proj_dir
    pm.workspace.open(proj_dir)
    # open the file
    pm.openFile(path, open=True, force=True)

    # get the reference
    rig_path = None
    if rig_type == head:
        refs = pm.ls('*horseHeadRig*', type='reference')
        rig_path = pm.workspace.path.joinpath('scenes/Horse_rig')
    if rig_type == body:
        # todo: check and change file path
        refs = pm.ls('*HorseBodyRig*', type='reference')
        rig_path = pm.workspace.path.joinpath('scenes/HorseBody_rig')
    if not rig_path or not os.path.exists(rig_path):
        raise IOError('Horse_rig directory not found: {}'.format(rig_path))

    # get the most recent rig in our folder
    files = glob.glob(rig_path + '/*')
    new_path = max(files, key=os.path.getctime)
    # change reference path
    for ref in refs:
        ref.referenceFile().replaceWith(new_path)
        print 'reference file: ', ref.referenceFile()

    end = pm.playbackOptions(aet=True, query=True)
    if rig_type == body:
        node = pm.ls('*:Grp_Mesh')[0]
    else:
        node = pm.ls('*:render_GEO_GRP')[0]
    if node:
        export_alembic_bake(0, end, node.longName())
    else:
        raise IOError('Node not found *:render_GEO_GRP')