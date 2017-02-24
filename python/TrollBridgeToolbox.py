import logging

import pymel.core as pm
from maya import OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import tbt_utils
reload(tbt_utils)

logger = logging.getLogger('TrollBridgeToolbox')
mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)


# projectSetup
# setCamera
# renderPasses
# frameRange
# startFrame
# endFrame
# renderSettings

class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.resolution = None
        self.aa_samples = None
        self.node_name = 'tbt_settings'
        self.buttons = []

        self.setWindowFlags(Qt.Window)
        self.setProperty("saveWindowPref", True)
        self.setMinimumWidth(300)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.__setup_widgets()

        self.update_status()
        
    def __setup_widgets(self):
        """Setup menu widgets and add to main layout"""

        # Default project settings button
        btn_project_setup = PushButton('Set up Project', self)
        btn_project_setup.clicked.connect(self.setup_project)
        btn_project_setup.setProperty('status', 'projectSetup')
        self.main_layout.addWidget(btn_project_setup)
        
        self.buttons.append(btn_project_setup)

        # camera height
        h_line = QFrame()
        h_line.setFrameStyle(QFrame.HLine)
        self.main_layout.addWidget(h_line)

        btn_camera_setup = PushButton('Set Camera', self)
        btn_camera_setup.clicked.connect(self.set_aspect_ratio)
        btn_camera_setup.setProperty('status', 'setCamera')

        self.main_layout.addWidget(btn_camera_setup)
        
        self.buttons.append(btn_camera_setup)

        # Add frame range spin boxes
        self.__frame_range_widget()

        # Setup renderpasses
        btn_renderpasses = PushButton('Setup Render Passes', self)
        btn_renderpasses.clicked.connect(self.setup_render_layer)
        btn_renderpasses.setProperty('status', 'renderPasses')

        self.main_layout.addWidget(btn_renderpasses)
        
        self.buttons.append(btn_renderpasses)

        # Render settings
        self.__render_settings_widget()

    def __render_settings_widget(self):
        """
        Render settings buttons grouped and added to main layout
        """

        btn_render_prev = PushButton('Preview Render', self, button_type='draft')
        btn_render_prev.clicked.connect(self.preview_setup)
        btn_render_prev.setProperty('type', 'previewRender')
        btn_render_prev.setProperty('status', 'draft')

        btn_render_final = PushButton('Final Render', self, button_type='final')
        btn_render_final.clicked.connect(self.final_setup)
        btn_render_final.setProperty('type', 'finalRender')
        btn_render_final.setProperty('status', 'final')

        btn_render_final_oar = PushButton('Final Render OAR', self, button_type='final_oar')
        btn_render_final_oar.clicked.connect(self.final_oar_setup)
        btn_render_final_oar.setProperty('type', 'finalOarRender')
        btn_render_final_oar.setProperty('status', 'final_oar')

        btn_render_final_anim = PushButton('Final Render Animation', self, button_type='final_anim')
        btn_render_final_anim.clicked.connect(self.final_render_animation)
        btn_render_final_anim.setProperty('type', 'finalAnimRender')
        btn_render_final_anim.setProperty('status', 'final_anim')

        layout = QVBoxLayout()
        layout.addWidget(btn_render_prev)
        layout.addWidget(btn_render_final_oar)
        layout.addWidget(btn_render_final)
        layout.addWidget(btn_render_final_anim)
        layout.addStretch(1)

        group = QGroupBox('Render Settings')
        group.setLayout(layout)

        self.buttons += [
            btn_render_prev,
            btn_render_final,
            btn_render_final_oar,
            btn_render_final_anim]

        self.main_layout.addWidget(group)

    def __frame_range_widget(self):

        self.field_start_frame = QSpinBox()
        self.field_start_frame.setValue(1)
        self.field_end_frame = QSpinBox()
        self.field_end_frame.setValue(50)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.field_start_frame)
        h_layout.addWidget(self.field_end_frame)

        btn_set_frame_range = PushButton('Set Frame Range', self)
        btn_set_frame_range.clicked.connect(self.set_frame_range)
        btn_set_frame_range.setProperty('status', 'frameRange')
        
        self.buttons.append(btn_set_frame_range)

        layout = QVBoxLayout()
        layout.addLayout(h_layout)
        layout.addWidget(btn_set_frame_range)
        layout.addStretch(1)

        group = QGroupBox('Frame Range')
        group.setLayout(layout)

        self.main_layout.addWidget(group)

    def update_status(self, button=None):
        """Update the status of the widgets
        Args:
            button (QPushButton): The button object which sent the event
        """
        if not self.buttons:
            return

        status = tbt_utils.get_status(self.node_name)
        if not status:
            return

        for i in self.buttons:
            type_ = i.property('type')
            if type_ and ('render' in type_.lower()):
                attr_name = self.node_name + '.renderSettings'
                value = bool(status.get(attr_name) == i.property('status'))
            else:
                attr_name = self.node_name + '.' + i.property('status')
                value = status.get(attr_name)

            if value:
                i.setStyleSheet('background-color: green')
            else:
                i.setStyleSheet('background-color: ')

    def setup_project(self):
        tbt_utils.setup_project()

    def get_status(self):
        tbt_utils.get_status(self.node_name)

    def create_node(self):
        tbt_utils.create_node(self.node_name)

    def setup_render_layer(self):
        tbt_utils.setup_render_layer()

    def set_frame_range(self):
        """Set the frame range in the maya scene and the render globals"""
        start_f = int(self.field_start_frame.value())
        end_f = int(self.field_end_frame.value())
        tbt_utils.set_frame_range(start_f, end_f)

    def set_aspect_ratio(self):
        tbt_utils.set_aspect_ratio()

    def preview_setup(self):
        tbt_utils.preview_setup()

    def final_setup(self):
        tbt_utils.final_setup()

    def final_oar_setup(self):
        tbt_utils.final_oar_setup()

    def final_render_animation(self):
        tbt_utils.final_render_animation()


class PushButton(QPushButton):

    def __init__(self, name, parent=None, **kwargs):
        super(PushButton, self).__init__(parent)
        self.setText(name)
        self.type = kwargs.get('button_type')
        self.parent = parent
        
    def mouseReleaseEvent(self, event):
        QPushButton.mouseReleaseEvent(self, event)
        if self.parent:
            self.parent.update_status(button=self)



def open():
    dialog = MainWindow(parent=mayaMainWindow)
    dialog.show()