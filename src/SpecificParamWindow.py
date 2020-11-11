# This Python file uses the following encoding: utf-8

import os
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import QAbstractItemView, QMessageBox, QSpinBox, QItemDelegate
from PySide2.QtCore import QFile, Qt, Signal, QObject
from PySide2.QtUiTools import QUiLoader
from proglog import ProgressBarLogger
from VideoTools import VideoTools

COL_START_SILENCE = 0
COL_STOP_SILENCE = 1
COL_DURATION = 2
COL_START_OFFSET = 3
COL_STOP_OFFSET = 4
MS_TO_SEC = 0.001


class SpecificParamWindow(QtWidgets.QWidget):
    ui = None
    silence_list = []
    video_tools = VideoTools()

    previousWindow = Signal()

    # Called once, when window is created
    def __init__(self):
        super(SpecificParamWindow, self).__init__()

        self.input_filename = ""
        self.output_filename = ""
        self.noise_threshold = 0.02
        self.max_silence_duration = 300
        self.start_offset = 150
        self.stop_offset = 150
        self.spinbox_delegate = SpinBoxDelegate()

        # Creation of objects
        self.error_dialog = QMessageBox()
        self.progress_bar_logger = MyBarLogger()

        # Load UI
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "SpecificParamForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Set silence table widget properties
        self.ui.silence_list_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.silence_list_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        header = self.ui.silence_list_table_widget.horizontalHeader()
        header.setSectionResizeMode(COL_START_SILENCE, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_STOP_SILENCE, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_DURATION, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COL_START_OFFSET, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(COL_STOP_OFFSET, QtWidgets.QHeaderView.Stretch)

        # Connect buttons and progress bar
        self.ui.silence_preview_push_button.clicked.connect(self.on_silence_preview_push_button_clicked)
        self.ui.generate_push_button.clicked.connect(self.on_generate_push_button_clicked)
        self.ui.previous_push_button.clicked.connect(self.on_previous_push_button_clicked)
        self.ui.quit_push_button.clicked.connect(self.on_quit_push_button_clicked)
        self.video_tools.video_generation_progress.connect(self.on_video_generation_progress)
        self.progress_bar_logger.video_generation_progress.connect(self.on_video_generation_progress)

    # Called each time the window is showed
    def start(self, input_filename, output_filename, noise_threshold,
              max_silence_duration, start_offset, stop_offset):

        # Hide progress bar
        self.ui.progress_bar.hide()

        # Save data entered by user
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.noise_threshold = noise_threshold
        self.max_silence_duration = max_silence_duration
        self.start_offset = start_offset
        self.stop_offset = stop_offset

        # Find silences in the input video, with parameters entered by user
        self.silence_list = self.video_tools.compute_silences(self.input_filename,
                                                              self.noise_threshold,
                                                              self.max_silence_duration,
                                                              self.start_offset,
                                                              self.stop_offset)
        # Fill silence table widget with silences found.
        self.fill_silence_table()
        if len(self.silence_list) > 0:
            self.ui.silence_list_table_widget.selectRow(0)
        else:
            self.ui.silence_preview_push_button.setEnabled(False)

        # Connect button for previewing silences
        self.ui.silence_list_table_widget.cellChanged.connect(self.on_cell_changed)

    def fill_silence_table(self):
        n_silence = len(self.silence_list)

        for i in range(n_silence):
            # Add one line
            self.ui.silence_list_table_widget.insertRow(i)
            sil = self.silence_list[i]

            # Fill line with silence data
            item = QtWidgets.QTableWidgetItem("{:.3f}".format(sil.start_time))
            self.ui.silence_list_table_widget.setItem(i, COL_START_SILENCE, item)
            item = QtWidgets.QTableWidgetItem("{:.3f}".format(sil.stop_time))
            self.ui.silence_list_table_widget.setItem(i, COL_STOP_SILENCE, item)
            item = QtWidgets.QTableWidgetItem("{:.3f}".format(sil.duration()))
            self.ui.silence_list_table_widget.setItem(i, COL_DURATION, item)

            # Columns containing start and stop offsets are editable spinboxes
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, sil.start_offset)
            self.ui.silence_list_table_widget.setItem(i, COL_START_OFFSET, item)
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, sil.stop_offset)
            self.ui.silence_list_table_widget.setItem(i, COL_STOP_OFFSET, item)

            self.ui.silence_list_table_widget.setItemDelegateForColumn(COL_START_OFFSET, self.spinbox_delegate)
            self.ui.silence_list_table_widget.setItemDelegateForColumn(COL_STOP_OFFSET, self.spinbox_delegate)

            # Set cells that are not allowed to be changed by user
            self.set_cell_changeable(i, COL_START_SILENCE, False)
            self.set_cell_changeable(i, COL_STOP_SILENCE, False)
            self.set_cell_changeable(i, COL_DURATION, False)
            self.set_cell_changeable(i, COL_START_OFFSET, sil.start_offset_changeable)
            self.set_cell_changeable(i, COL_STOP_OFFSET, sil.stop_offset_changeable)


    def set_cell_changeable(self, row, col, changeable):
        if changeable:
            self.ui.silence_list_table_widget.item(row, col). setBackground(Qt.white)
        else:
            self.ui.silence_list_table_widget.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ui.silence_list_table_widget.item(row, col).setBackground(Qt.lightGray)

    # Called when user press 'Previous' button
    def on_previous_push_button_clicked(self):
        # Empty silence table widget.
        old_len = self.ui.silence_list_table_widget.rowCount()
        for _ in range(old_len):
            self.ui.silence_list_table_widget.removeRow(0)

        # Disconnect button for previewing silences
        self.ui.silence_list_table_widget.cellChanged.disconnect(self.on_cell_changed)

        # Ask to get back to first window (GenericParamWindow)
        self.previousWindow.emit()

    # Called when user press 'Generate' button
    def on_generate_push_button_clicked(self):
        self.ui.progress_bar.show()
        self.video_tools.write_video(self.input_filename, self.output_filename, self.silence_list, self.progress_bar_logger)
        self.close()

    # Called automatically when generation routine has progressed
    def on_video_generation_progress(self, percent):
        self.ui.progress_bar.setValue(percent)

    # Called when user press 'Cancel' button
    def on_quit_push_button_clicked(self):
        self.close()

    # Called when user press 'Preview silence' button
    def on_silence_preview_push_button_clicked(self):
        indexes = self.ui.silence_list_table_widget.selectionModel().selectedRows()
        assert len(indexes) == 1
        row = indexes[0].row()
        playtime_before = self.ui.playtime_before_spin_box.value()
        playtime_after = self.ui.playtime_after_spin_box.value()

        silence = self.silence_list[row]

        self.video_tools.preview_video(self.input_filename, playtime_before, playtime_after, silence)

    # Called when user change a cell in silence table widget
    def on_cell_changed(self, row, col):
        assert (0 <= row < len(self.silence_list)), 'Fatal error'
        assert col in (COL_START_OFFSET, COL_STOP_OFFSET), 'Fatal error'

        # Get changed data
        data = self.ui.silence_list_table_widget.item(row, col).data(Qt.DisplayRole)

        if col == COL_START_OFFSET:
            self.silence_list[row].start_offset = data
        else:
            self.silence_list[row].stop_offset = data

        # If invalid data entered by user, open a warning box.
        if (self.silence_list[row].start_offset + self.silence_list[row].stop_offset) * MS_TO_SEC > self.silence_list[row].duration():
            self.error_dialog.setIcon(QMessageBox.Warning)
            self.error_dialog.setText("You have set start_offset + stop_offset greater than silence duration. Therefore, this silence will not be cut.")
            self.error_dialog.show()


# Allow to set limits for spinboxes for start and stop offsets of silences in the silence table widget.
class SpinBoxDelegate(QItemDelegate):

    def createEditor(self, parent, *_):
        editor = QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(1000000)
        editor.setSingleStep(50)

        return editor

# Progress bar of video generation
class MyBarLogger(ProgressBarLogger, QObject):
    mp3_progress_start = 12
    mp3_progress_stop = 16
    mp3_progress_delta = mp3_progress_stop - mp3_progress_start
    mp4_progress_start = mp3_progress_stop + 1
    mp4_progress_stop = 98
    mp4_progress_delta = mp4_progress_stop - mp4_progress_start

    video_generation_progress = Signal(int)

    def __init__(self):
        ProgressBarLogger.__init__(self)
        QObject.__init__(self)
        self.progress_factor = 0

    def callback(self, **changes):
        if 't' in self.state['bars']:
            idx = self.state['bars']['t']['index']
            if idx < 0:
                self.progress_factor = self.mp4_progress_delta / self.state['bars']['t']['total']
            else:
                val = self.mp4_progress_start + self.progress_factor * idx
                self.video_generation_progress.emit(val)
        elif 'chunk' in self.state['bars']:
            idx = self.state['bars']['chunk']['index']
            if idx < 0:
                self.progress_factor = self.mp3_progress_delta / self.state['bars']['chunk']['total']
            else:
                val = self.mp3_progress_start + self.progress_factor * idx
                self.video_generation_progress.emit(val)
