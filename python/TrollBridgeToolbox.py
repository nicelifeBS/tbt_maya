import pymel.core as pm
from maya import OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import logging
logger = logging.getLogger('TrollBridgeToolbox')

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)

SETTINGS = {
              'final': {'res': [2048, 878],
                        'aa_samples': 8
                        },
              'draft': {'res': [1024, 439],
                        'aa_samples': 2},
              }

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resolution = None
        self.aa_samples = None

        self.setWindowFlags(Qt.Window)
        self.setProperty("saveWindowPref", True)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.__setup_widgets()

    def __setup_widgets(self):
        self.btn_project_setup = QPushButton('Set up Project')
        self.btn_project_setup.clicked.connect(self.setup_project)

        self.btn_render_prev = QPushButton('Preview Render')
        self.btn_render_prev.clicked.connect(self.preview_setup)

        self.btn_render_final = QPushButton('Final Render')
        self.btn_render_final.clicked.connect(self.final_setup)

        self.main_layout.addWidget(self.btn_project_setup)
        self.main_layout.addWidget(self.btn_render_prev)
        self.main_layout.addWidget(self.btn_render_final)

    def setup_project(self):

        # Set project fps
        pm.currentUnit(time='pal')

        # load arnold plugin
        pm.loadPlugin('mtoa.bundle')

        # Set render resolution
        self.set_render_settings('final')

        # set gamma to 1.0
        pm.SCENE.defaultArnoldRenderOptions.display_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.light_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.shader_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.texture_gamma.set(1.0)

        # activate animation and set file name to filenam.#.exr
        pm.SCENE.defaultRenderGlobals.animation.set(True)
        pm.SCENE.defaultRenderGlobals.periodInExt.set(1)

        # Todo: set start end frame range

    def preview_setup(self):
        """
        Set render settings to draft settings
        :return:
        """
        self.set_render_settings('draft')

    def final_setup(self):
        """
        Set resolution and aa samples to final render resolution if settings were
        changed
        :return:
        """
        self.set_render_settings('final')

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

def open():
    dialog = MainWindow(parent=mayaMainWindow)
    dialog.show()