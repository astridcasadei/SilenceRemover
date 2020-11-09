# This Python file uses the following encoding: utf-8
import sys
from GenericParamWindow import GenericParamWindow
from SpecificParamWindow import SpecificParamWindow
from PySide2.QtWidgets import QApplication, QDesktopWidget

SOFTWARE_NAME = "Silence Remover"


# Flipping from second to first window
def toFrame1():
    frame2.hide()
    frame1.start()
    frame1.show()


# Flipping from first to second window
def toFrame2(input_filename, output_filename, noise_threshold, max_silence_duration, start_offset, stop_offset):
    frame2.start(input_filename,
                 output_filename,
                 noise_threshold,
                 max_silence_duration,
                 start_offset,
                 stop_offset)
    frame1.hide()
    frame2.show()


if __name__ == "__main__":
    app = QApplication([])

    # Creation of windows
    frame1 = GenericParamWindow()
    frame2 = SpecificParamWindow()
    frame1.setWindowTitle(SOFTWARE_NAME)
    frame2.setWindowTitle(SOFTWARE_NAME)

    # Moving frames to center of the screen
    bottom_right = QDesktopWidget().availableGeometry().bottomRight()
    x_max = bottom_right.x()
    y_max = bottom_right.y()
    frame1_width = min(frame1.width() + 0, x_max)
    frame1_height = min(frame1.height() + 200, y_max)  # workaround because "height()" seem to underestimate real height
    frame1.move((x_max - frame1_width) / 2, (y_max - frame1_height) / 2)
    frame2_width = min(frame2.width() + 0, x_max)
    frame2_height = min(frame2.height() + 400, y_max)  # workaround because "height()" seem to underestimate real height
    frame2.move((x_max - frame2_width) / 2, (y_max - frame2_height) / 2)

    # Connexions of frames
    frame1.nextWindow.connect(toFrame2)
    frame2.previousWindow.connect(toFrame1)
    frame2.video_tools.silence_computation_progress.connect(frame1.on_progress)

    # Display first window
    frame1.start()
    frame1.show()

    # Qt loop
    sys.exit(app.exec_())
