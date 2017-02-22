import pymel.core as pm
from maya import OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import logging
logger = logging.getLogger('TrollBridgeToolbox')

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)


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


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resolution = None
        self.aa_samples = None

        self.setWindowFlags(Qt.Window)
        self.setProperty("saveWindowPref", True)
        self.setMinimumWidth(300)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.__setup_widgets()

    def __setup_widgets(self):
        """Setup menu widgets and add to main layout"""

        # Default project settings button
        self.btn_project_setup = QPushButton('Set up Project')
        self.btn_project_setup.clicked.connect(self.setup_project)
        self.main_layout.addWidget(self.btn_project_setup)

        # camera height
        h_line = QFrame()
        h_line.setFrameStyle(QFrame.HLine)
        self.main_layout.addWidget(h_line)
        self.btn_camera_setup = QPushButton('Set Camera')
        self.btn_camera_setup.clicked.connect(self.set_aspect_ratio)
        self.main_layout.addWidget(self.btn_camera_setup)

        # Add frame range spin boxes
        self.__frame_range_widget()

        # Setup renderpasses
        btn_renderpasses = QPushButton('Setup Render Passes')
        btn_renderpasses.clicked.connect(self.setup_render_layer)
        self.main_layout.addWidget(btn_renderpasses)

        # Render settings
        self.__render_settings_widget()

    def __render_settings_widget(self):
        """
        Render settings buttons grouped and added to main layout
        """

        self.btn_render_prev = QPushButton('Preview Render')
        self.btn_render_prev.clicked.connect(self.preview_setup)

        self.btn_render_final = QPushButton('Final Render')
        self.btn_render_final.clicked.connect(self.final_setup)

        self.btn_render_final_oar = QPushButton('Final Render OAR')
        self.btn_render_final_oar.clicked.connect(self.final_oar_setup)

        self.btn_render_final_anim = QPushButton('Final Render Animation')
        self.btn_render_final_anim.clicked.connect(self.final_render_animation)

        layout = QVBoxLayout()
        layout.addWidget(self.btn_render_prev)
        layout.addWidget(self.btn_render_final_oar)
        layout.addWidget(self.btn_render_final)
        layout.addWidget(self.btn_render_final_anim)
        layout.addStretch(1)

        group = QGroupBox('Render Settings')
        group.setLayout(layout)

        self.main_layout.addWidget(group)

    def __frame_range_widget(self):

        self.field_start_frame = QSpinBox()
        self.field_start_frame.setValue(1)
        self.field_end_frame = QSpinBox()
        self.field_end_frame.setValue(50)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.field_start_frame)
        h_layout.addWidget(self.field_end_frame)

        btn_set_frame_range = QPushButton('Set Frame Range')
        btn_set_frame_range.clicked.connect(self.set_frame_range)

        layout = QVBoxLayout()
        layout.addLayout(h_layout)
        layout.addWidget(btn_set_frame_range)

        self.main_layout.addLayout(layout)

    def setup_project(self):

        # get the scene instance
        scene = pm.Scene()
        
        # Set project fps
        pm.currentUnit(time='pal')

        # load arnold plugin
        pm.loadPlugin('mtoa.bundle')

        # Set render resolution
        scene.defaultResolution.aspectLock.set(0)
        self.set_render_settings('final')

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
        # Todo: set start end frame range

    def setup_render_layer(self):

        # select head yeti and lightsetup
        select_ = [
            '*:Yeti_grp',
            '*:HorseHead',
            #'__lightsetup*', todo: need solution if group is not present
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

    def set_frame_range(self):
        """Set the frame range in the maya scene and the render globals"""
        start_f = int(self.field_start_frame.value())
        end_f = int(self.field_end_frame.value())

        # set timeline
        pm.animation.playbackOptions(ast=start_f, aet=end_f, min=start_f, max=end_f)
        # set the render globals
        pm.SCENE.defaultRenderGlobals.startFrame.set(start_f)
        pm.SCENE.defaultRenderGlobals.endFrame.set(end_f)

    def set_aspect_ratio(self):
        """
        Set the film gate height of a selected camera based on our render
        resolution to meet the correct aspect ratio
        """
        sel = pm.ls(selection=True)
        if not sel:
            print 'Please select a camera'
            return

        for shape in sel:
            try:
                shape = shape.getShape()
            except:
                pass
            if shape.type() == 'camera':
                # get the width of the film back
                width = shape.horizontalFilmAperture.get()
                # calculate the new width with our final render resolution
                new_width = width * (RES_FINAL[1] / RES_FINAL[0])
                # set the width
                shape.verticalFilmAperture.set(new_width)
                print 'Changed height of film gate to '.format(new_width)
            return

    def preview_setup(self):
        """
        Set render settings to draft settings
        and disable motion blur
        """
        # get the scene instance
        scene = pm.Scene()

        self.set_render_settings('draft')
        scene.defaultArnoldRenderOptions.motion_blur_enable.set(0)

    def final_setup(self):
        """
        Set resolution and aa samples to final render resolution if settings were
        changed
        :return:
        """
        self.set_render_settings('final')

    def final_oar_setup(self):
        self.set_render_settings('final_oar')

    def final_render_animation(self):
        # get the scene instance
        scene = pm.Scene()

        self.set_render_settings('final')
        # enable motion blur
        scene.defaultArnoldRenderOptions.motion_blur_enable.set(1)
        scene.defaultArnoldRenderOptions.range_type.set(0)
        scene.defaultArnoldRenderOptions.outputOverscan.set('10%')
        scene.defaultArnoldDriver.mergeAOVs.set(1)

    def set_render_settings(self, preset, pixel_ar=1.0):
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

def open():
    dialog = MainWindow(parent=mayaMainWindow)
    dialog.show()