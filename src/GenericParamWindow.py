# This Python file uses the following encoding: utf-8
import os
import math
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog, QMessageBox, QWidget, QVBoxLayout
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Signal, Slot
from moviepy.editor import VideoFileClip


class GenericParamWindow(QtWidgets.QWidget):
    ui = None
    noise_threshold = 0.02
    max_silence_duration = 300
    start_offset = 150
    stop_offset = 150
    input_filename = ""
    output_filename = ""
    max_sound_profile_duration = 30  # in seconds
    input_filename_extension = [".mp4", ".avi", ".flv", ".mkv", ".vob",
                                ".webm", ".wmv", ".mov", ".mpg"]
    output_filename_extension = [".mp4", ".webm"]

    nextWindow = Signal(str, str, float, int, int, int)

    # Called once, when window is created
    def __init__(self):
        super(GenericParamWindow, self).__init__()

        # Create objects
        self.error_dialog = QMessageBox()
        self.sound_profile = SoundProfileWidget()

        # Load UI
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "GenericParamForm.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.ui.input_file_line_edit.setText("")
        self.ui.output_file_line_edit.setText("")

        # Connect buttons
        self.ui.next_button.clicked.connect(self.on_next_button_clicked)
        self.ui.browse_input_file_button.clicked.connect(self.on_browse_input_file_button_clicked)
        self.ui.browse_output_file_button.clicked.connect(self.on_browse_output_file_button_clicked)
        self.ui.sound_profile_push_button.clicked.connect(self.on_sound_profile_button_clicked)

    # Called each time the window is showed
    def start(self):
        # Hide progress bar
        self.ui.progress_bar.hide()

    def extensions_list(self,extlist):
        exts = ""
        for ext in extlist:
            exts = exts + " " + ext
        return exts

    def check_input_file(self):
        error_msg = ""

        file, input_extension = os.path.splitext(self.input_filename)

        if self.input_filename == "":
            error_msg = "Input file name should be specified."
        elif not os.path.isfile(self.input_filename):
            error_msg = "Input file does not exist."
        elif not input_extension in self.input_filename_extension:
            exts = self.extensions_list(self.input_filename_extension)
            error_msg = "Supported input video formats are:" + exts + "."

        return error_msg

    # Check data consistency
    def check_data(self):

        error_msg = self.check_input_file()

        if error_msg == "":
            file, output_extension = os.path.splitext(self.output_filename)

            if self.output_filename == "":
                error_msg = "Output file name should be specified."
            elif not output_extension in self.output_filename_extension:
                exts = self.extensions_list(self.output_filename_extension)
                error_msg = "Supported output video formats are:" + exts + "."
            elif self.input_filename == self.output_filename:
                error_msg = "Input and output file should be different."
            elif self.noise_threshold < 0:
                error_msg = "'Noise threshold' should be a positive number."
            elif self.max_silence_duration < 0:
                error_msg = "'Maximum silence duration' should be a positive number."
            elif ((self.start_offset < 0) or (self.stop_offset < 0)):
                error_msg = "Start and stop offsets should be positive numbers."
            elif self.start_offset + self.stop_offset > self.max_silence_duration:
                error_msg = "'Maximum silence duration' should be at least equal" + \
                "to the sum of start and stop offsets."

        return error_msg

    # Called when user press 'Sound profile' button
    def on_sound_profile_button_clicked(self):
        # Get input file entered by user
        self.input_filename = self.ui.input_file_line_edit.text()

        # Check whether input file entered by user is a valid video file
        error_msg = self.check_input_file()

        # If input file is valid
        if error_msg == "":
            self.on_progress(0)

            # Create a video clip from input file
            videoclip = VideoFileClip(self.input_filename)

            self.on_progress(9)

            # Extract audio from video clip (if video is long, keep only first seconds)
            audio_fps = videoclip.audio.fps
            duration = min(videoclip.duration, self.max_sound_profile_duration)
            sound_array = videoclip.audio.subclip(0, duration).to_soundarray(fps=audio_fps)

            self.on_progress(13)

            # Compute volume
            n_sound = np.shape(sound_array)[0]  # We have n_sound / customFps = duration in seconds
            volume_fn = lambda p : math.sqrt(p[0]**2 + p[1]**2)
            volumes = np.zeros(n_sound)
            times = np.arange(0, duration, 1/audio_fps)
            for i in range(n_sound):
                volumes[i] = volume_fn(sound_array[i])

            self.on_progress(63)

            # Make a plot of the volume
            title = 'Sound profile of ' + self.input_filename
            if videoclip.duration != duration:
                title += "\n(truncated to first " + str(duration) + " seconds)"

            self.sound_profile.update_plot(title, times, volumes)

            self.on_progress(100)

            # Show plot and hide progress bar
            self.sound_profile.showMaximized()
            self.ui.progress_bar.hide()

        # If input file entered by user is invalid, show an error message.
        else:
            self.error_dialog.setIcon(QMessageBox.Warning)
            self.error_dialog.setText(error_msg)
            self.error_dialog.show()

    # Called when user press the '...' button to select input file
    def on_browse_input_file_button_clicked(self):
        exts = ""
        for ext in self.input_filename_extension:
            exts = exts + " *" + ext
        exts = "Video Files (" + exts + ")"
        file = QFileDialog.getOpenFileName(self, "Choose input video", "", exts)
        input_filename = file[0]
        self.ui.input_file_line_edit.selectAll()
        self.ui.input_file_line_edit.insert(input_filename)

    # Called when user press the '...' button to select output file
    def on_browse_output_file_button_clicked(self):
        exts = ""
        for ext in self.output_filename_extension:
            exts = exts + " *" + ext
        ext = "Video Files (" + ext + ")"
        file = QFileDialog.getSaveFileName(self, exts)
        output_filename = file[0]
        self.ui.output_file_line_edit.selectAll()
        self.ui.output_file_line_edit.insert(output_filename)

    # Called when user press 'Next' button
    def on_next_button_clicked(self):
        # Get data entered by user
        self.input_filename = self.ui.input_file_line_edit.text()
        self.output_filename = self.ui.output_file_line_edit.text()
        self.noise_threshold = self.ui.noise_threshold_spinbox.value()
        self.max_silence_duration = self.ui.max_silence_spinbox.value()
        self.start_offset = self.ui.start_offset_spinbox.value()
        self.stop_offset = self.ui.stop_offset_spinbox.value()

        # Check data consistency
        error_msg = self.check_data()

        # If data is ok, emit it
        if error_msg == "":
            self.nextWindow.emit(self.input_filename,
                                 self.output_filename,
                                 self.noise_threshold,
                                 self.max_silence_duration,
                                 self.start_offset,
                                 self.stop_offset)
        # Otherwise, display the error message
        else:
            self.error_dialog.setIcon(QMessageBox.Warning)
            self.error_dialog.setText(error_msg)
            self.error_dialog.show()

    # Called automatically when a computational routine has progressed
    # (there are two routines using this progress bar:
    #  on_sound_profile_button_clicked and on_next_button_clicked)
    def on_progress(self, percent):
        self.ui.progress_bar.show()
        self.ui.progress_bar.setValue(percent)

# Class for plotting sound profile
class SoundProfileWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.fig = Figure(tight_layout = True)

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        unwanted_buttons = ['Subplots', 'Save']
        for action in self.toolbar.actions():
            if action.text() in unwanted_buttons:
                self.toolbar.removeAction(action)

        lay = QVBoxLayout(self)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.canvas)

        self.axe = self.fig.add_subplot(111)
        self.line, *_ = self.axe.plot([])

        self.axe.grid(True, which='major', axis='y', color='r', linewidth=2)
        self.axe.grid(True, which='minor', axis='y')
        self.axe.set_xlabel('time [s]', fontsize=19)
        self.axe.set_ylabel('volume', fontsize=19)

        self.axe.yaxis.set_major_locator(MultipleLocator(0.05))
        self.axe.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        self.axe.yaxis.set_minor_locator(MultipleLocator(0.01))

    @Slot(list)
    def update_plot(self, title, x_data, y_data):
        self.fig.suptitle(title, fontsize=25)

        self.line.set_data(x_data, y_data)

        self.axe.set_xlim(0, x_data[-1])
        self.axe.set_ylim(min(y_data), max(0.1, max(y_data)/2))
        self.canvas.draw()
