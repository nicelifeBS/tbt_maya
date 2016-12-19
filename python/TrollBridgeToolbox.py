import pymel.core as pm
from maya import OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import logging
logger = logging.getLogger('TrollBridgeToolbox')

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)

res_final = (2048.0, 858.0)

SETTINGS = {
              'final': {'res': res_final,
                        'aa_samples': 10
                        },
              'draft': {'res': [res_final[0]/2, res_final[1]/2],
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
        self.btn_camera_setup = QPushButton('Set Camera')
        self.btn_camera_setup.clicked.connect(self.set_aspect_ratio)
        self.main_layout.addWidget(self.btn_camera_setup)

        # Render settings
        self.__setup_render_settings()

    def __setup_render_settings(self):
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

    def setup_project(self):

        # Set project fps
        pm.currentUnit(time='pal')

        # load arnold plugin
        pm.loadPlugin('mtoa.bundle')

        # Set render resolution
        pm.SCENE.defaultResolution.aspectLock.set(0)
        self.set_render_settings('final')
        pm.SCENE.defaultResolution.aspectLock.set(1)

        # set gamma to 1.0
        pm.SCENE.defaultArnoldRenderOptions.display_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.light_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.shader_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.texture_gamma.set(1.0)

        # set image folder structure
        pm.SCENE.defaultRenderGlobals.imageFilePrefix.set('<Scene>/<RenderLayer>_<RenderPass>')
        # activate animation and set file name to filename.#.exr
        pm.SCENE.defaultRenderGlobals.animation.set(True)
        pm.SCENE.defaultRenderGlobals.periodInExt.set(1)

        # Shutter open on start frame
        pm.SCENE.defaultArnoldRenderOptions.range_type.set(0)
        # Enable motion blur
        pm.SCENE.defaultArnoldRenderOptions.motion_blur_enable.set(1)
        # Display driver settings
        pm.SCENE.defaultArnoldDriver.outputMode.set(2)
        pm.SCENE.defaultArnoldDriver.mergeAOVs.set(1)
        pm.SCENE.defaultArnoldDriver.prefix.set("<Scene>/<RenderLayer>")

        # Set yeti plugin premel
        pm.SCENE.defaultRenderGlobals.preMel.set("pgYetiPreRender")

        # Todo: set start end frame range

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
                new_width = width * (res_final[1] / res_final[0])
                # set the width
                shape.verticalFilmAperture.set(new_width)
                print 'Changed height of film gate to '.format(new_width)
            return

    def preview_setup(self):
        """
        Set render settings to draft settings
        and disable motion blur
        """
        self.set_render_settings('draft')
        pm.SCENE.defaultArnoldRenderOptions.motion_blur_enable.set(0)

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
        self.set_render_settings('final')
        # enable motion blur
        pm.SCENE.defaultArnoldRenderOptions.motion_blur_enable.set(1)
        pm.SCENE.defaultArnoldRenderOptions.range_type.set(0)
        pm.SCENE.defaultArnoldRenderOptions.outputOverscan.set('10%')
        pm.SCENE.defaultArnoldDriver.mergeAOVs.set(1)

    def set_render_settings(self, preset, pixel_ar=1.0):
        if preset in SETTINGS.keys():
            settings = SETTINGS[preset]
        else:
            return

        width, height = settings['res']

        pm.SCENE.defaultResolution.width.set(width)
        pm.SCENE.defaultResolution.height.set(height)
        pm.SCENE.defaultArnoldRenderOptions.AASamples.set(settings['aa_samples'])
        pm.SCENE.defaultResolution.pixelAspect.set(pixel_ar)
        pm.SCENE.defaultArnoldRenderOptions.GIDiffuseDepth.set(3)
        pm.SCENE.defaultArnoldRenderOptions.GIGlossyDepth.set(3)

def open():
    dialog = MainWindow(parent=mayaMainWindow)
    dialog.show()