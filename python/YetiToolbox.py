from maya import OpenMayaUI as omui
from PySide.QtCore import *
from PySide.QtGui import *
from shiboken import wrapInstance

import os
import logging

import YetiHelpers
reload(YetiHelpers)

logger = logging.getLogger('YetiToolbox')

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QWidget)


class LineEdit(QWidget):

    def __init__(self, label, text=None):
        super(LineEdit, self).__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(str(label))
        self.line_edit = QLineEdit()
        if text:
            self.line_edit.setText(str(text))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)

    def text(self):
        return self.line_edit.text()

class ExportDialog(QDialog):

    def __init__(self, time_range, samples, output_path, parent=None):
        super(ExportDialog, self).__init__(parent)
        self.setWindowTitle('Create Cache Settings')

        self.time_range = time_range
        self.samples = samples
        self.output_path = output_path

        self.layout_edits = QGridLayout()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.edit_time_start = LineEdit('Start', time_range[0])
        self.edit_time_stop = LineEdit('Stop', time_range[1])
        self.edit_samples = LineEdit('Samples', samples)
        self.edit_path = LineEdit('Export Path', output_path)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.send_values)
        buttons.rejected.connect(self.reject)

        self.layout_edits.addWidget(self.edit_time_start, 0, 0)
        self.layout_edits.addWidget(self.edit_time_stop, 0, 1)
        self.layout_edits.addWidget(self.edit_samples, 1, 0)

        self.main_layout.addWidget(self.edit_path)
        self.main_layout.addLayout(self.layout_edits)
        self.main_layout.addWidget(buttons)

    def send_values(self):
        self.time_range = (float(self.edit_time_start.text()), float(self.edit_time_stop.text()))
        self.samples = int(self.edit_samples.text())
        self.accept()

class YetiMainWidget(QWidget):

    def __init__(self, parent=None):
        super(YetiMainWidget, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setProperty("saveWindowPref", True)
        self.setMinimumWidth(300)
        self.setWindowTitle('Yeti Toolbox')

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.__setup_widgets()

    def __setup_widgets(self):
        self.btn_create_cache = QPushButton('Create Cache')
        self.btn_create_cache.clicked.connect(self.create_cache)

        self.btn_set_source = QPushButton('Set Image Source Directory')
        self.btn_set_source.clicked.connect(self.set_image_src)

        self.main_layout.addWidget(self.btn_create_cache, 0, 0)
        self.main_layout.addWidget(self.btn_set_source, 1, 0)

    def create_cache(self):
        selection = YetiHelpers.get_selection()
        nodes = YetiHelpers.get_yeti_nodes(selection)
        time_range = YetiHelpers.get_time_range()

        # Open setting dialog for export
        output_path = YetiHelpers.get_project_dir(_type='fileCache')
        output_path = os.path.join(output_path, 'yeti')
        dialog = ExportDialog(time_range, samples=3, output_path=output_path, parent=self)

        if dialog.exec_():
            time_range = dialog.time_range
            samples = dialog.samples
            output_path = dialog.output_path
            # iterate through nodes and create the caches
            #print time_range, samples, output_path
            for n in nodes:
                YetiHelpers.create_cache(n, _range=time_range, samples=samples, cache_dir=output_path)

    def set_image_src(self):
        default_dir = YetiHelpers.get_project_dir(_type='sourceImages')
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.resize(500, 100)
        dialog.setWindowTitle('Set Image Source Path')
        dialog.setTextValue(str(default_dir))

        ok = dialog.exec_()
        path = dialog.textValue()

        if ok:
            YetiHelpers.set_image_path(path, selection=False)
            logger.info('Set path to: {}'.format(path))

def open():
    yeti_dialog = YetiMainWidget(parent=mayaMainWindow)
    yeti_dialog.show()