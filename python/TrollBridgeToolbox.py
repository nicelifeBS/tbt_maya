import pymel.core as pm
from maya import OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import logging
logger = logging.getLogger('TrollBridgeToolbox')

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)

RESOLUTION = {'final': [2048, 878],
              'draft': [1024, 439]}

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
        self.set_resolution('final')


        # set gamma to 1.0
        pm.SCENE.defaultArnoldRenderOptions.display_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.light_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.shader_gamma.set(1.0)
        pm.SCENE.defaultArnoldRenderOptions.texture_gamma.set(1.0)

        # activate animation and set file name to filenam.#.exr
        pm.SCENE.defaultRenderGlobals.animation.set(True)
        pm.SCENE.defaultRenderGlobals.periodInExt.set(1)

    def preview_setup(self):
        """
        Set render settings to draft settings
        :return:
        """
        # get resolution
        w = pm.SCENE.defaultResolution.width.get()
        h = pm.SCENE.defaultResolution.height.get()
        self.resolution = w, h

        # set resolution to draft
        self.set_resolution('draft')

        # change AA samples
        self.aa_samples = pm.SCENE.defaultArnoldRenderOptions.AASamples.get()
        pm.SCENE.defaultArnoldRenderOptions.AASamples.set(3)

    def final_setup(self):
        """
        Set resolution and aa samples to final render resolution if settings were
        changed
        :return:
        """
        if self.resolution:
            self.set_resolution('final')
        if self.aa_samples:
            pm.SCENE.defaultArnoldRenderOptions.AASamples.set(self.aa_samples)

    def set_resolution(self, preset, pixel_ar=1.0):
        if preset in RESOLUTION.keys():
            width, height = RESOLUTION[preset]
        else:
            return

        pm.SCENE.defaultResolution.width.set(width)
        pm.SCENE.defaultResolution.height.set(height)
        pm.SCENE.defaultResolution.pixelAspect.set(pixel_ar)

def open():
    dialog = MainWindow(parent=mayaMainWindow)
    dialog.show()