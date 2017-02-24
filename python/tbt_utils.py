import pymel.core as pm

RES_FINAL = (2048.0, 858.0)


SETTINGS = {
              'final': {'res': RES_FINAL,
                        'aa_samples': 10
                        },
              'draft': {'res': [RES_FINAL[0] / 2, RES_FINAL[1] / 2],
                        'aa_samples': 2},
              'final_oar': {'res': (4480, 1920),
                            'aa_samples': 10},
              }

# projectSetup
# setCamera
# renderPasses
# frameRange
# startFrame
# endFrame
# renderSettings

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
        pm.PyNode(node_name).listAttr(ud=True)
    except pm.MayaNodeError:
        node = pm.createNode('', n=node_name)
    else:
        # we exit if the node is present
        return

    node.addAttr('projectSetup', attributeType='bool')
    node.addAttr('setCamera', attributeType='bool')
    node.addAttr('renderPasses', attributeType='bool')

    node.addAttr('frameRange', attributeType='bool')
    node.addAttr('startFrame', attributeType='float')
    node.addAttr('endFrame', attributeType='float')
    node.addAttr('renderSettings', dt='string')

    pm.lockNode(node, lock=True)


def setup_project():
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
    scene.defaultArnoldDriver.prefix.set("<Scene>/<RenderLayer>")

    # Set yeti plugin premel
    scene.defaultRenderGlobals.preMel.set("pgYetiPreRender")
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
    set_status('renderPasses', 1)


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
    # scene.defaultResolution.pixelAspect.set(pixel_ar)

    scene.defaultArnoldRenderOptions.AASamples.set(settings['aa_samples'])
    scene.defaultArnoldRenderOptions.GIDiffuseDepth.set(3)
    scene.defaultArnoldRenderOptions.GIGlossyDepth.set(3)