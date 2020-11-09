# SilenceRemover
 
Software description:
======================

This sofware automatically remove long silences from video files.

Basically, you can choose:
* The noise threshold; all parts of the video where audio volume is below this threshold is considered as silence.
  A plot showing the evolution of volume in your video help you choose this parameter.
* The maximum duration you allow for a silence; all silences whose duration are greater will be cut.
* The time to keep at the beginning and at the end of a silence cut. 
  These durations can be set for all silences cut or for each silence cut individually. 
  Each silence cut can be previewed to help you adjusting these parameters.

Supported input video format are: .mp4, .avi, .flv, .mkv, .vob, .webm, .wmv, .mov, .mpg

Supported output video format are: .mp4, .webm

Author: 
=======

Astrid Casadei

License: 
========

See LICENSE file.

Installation:
=============

(The following will work for Window only, and maybe only for Window 10. If you have another operating system, please do the installation from sources.)

* Install ffmpeg (this step is optional)
* Download archive SilenceRemover-1.0.0.zip
* Unzip archive in a folder of your choice.
* Go in this folder and launch SilenceRemover.exe. (This should launch the software.)

Installation from sources:
==========================

Note: version number of dependancies are given as a guide. The software may work with other versions.

Windows
-------

* Install python 3.8 or 3.9 (this should also install pip)
* Install ffmpeg (this step is optional)
* Open a terminal (on Windows this can be done by launching 'cmd' or 'powershell'). 
* Enter the following line:
  python -m pip install PySide2==5.15.1 numpy==1.19.3 matplotlib==3.2.2 moviepy==1.0.3 proglog==0.1.9 pygame==2.0.0
* Download sources of SilenceRemover from github: 
  go to https://github.com/astridcasadei/SilenceRemover/tree/v1.0.0 and click 'Code' and 'Download zip'.
* Unzip the file you dowloaded in a folder of your choice.
* In the terminal, go to the folder where you unziped the file, and go to the subfolder "src". For instance:
  cd "C:\Users\YourName\Downloads\SilenceRemover-1.0.0\src"
* Enter the following line:
  python SilenceRemover.py
  (This should launch the software.)

Ubuntu
-------

* Open a terminal.
* Install python 3.8 or 3.9 and pip:
  sudo apt-get install python3.8 python3-distutils pkg-config freetype* python3-pip
  (Some packages above may not be necessary but I got trouble and I'm not sure...)
* Check 'python3 --version' return python 3.8 or 3.9 
* Install ffmpeg (this is optional):
  sudo apt-get install ffmpeg
* Install the following python modules:
  python3 -m pip install PySide2==5.15.1 numpy==1.19.3 matplotlib==3.2.2 moviepy==1.0.3 proglog==0.1.9 pygame==2.0.0
* Download sources of SilenceRemover from github: 
  go to https://github.com/astridcasadei/SilenceRemover/tree/v1.0.0 and click 'Code' and 'Download zip'.
* In the terminal, go to the folder where you downloaded the file:
  cd path/to/file
* Unzip it:
  unzip SilenceRemover-1.0.0.zip
* Go to src subfolder:
  cd src
* Enter the following line:
  python3 SilenceRemover.py
  (This should launch the software.)
  
  

Usage example
==============

* Download some test video, for example https://github.com/astridcasadei/SilenceRemover/blob/v1.0.0/test/alphabet1.mp4.
* Play video alphabet1.mp4: you can see it is a (french) spelling of the alphabet with silences between some letters.
* Launch SilenceRemover (see 'Installation' or 'Installation from sources' paragraphs).
* Browse input video file and select alphabet1.mp4.
* Browse output video file and choose alphabet1_without_silences.mp4.
* Click on 'Sound profile'. You can see that noise level never exceed 0.01.
* Close 'sound profile' window.
* Set 'noise threshold' to 0.01.
* Enter 350ms as 'max silence duration'. This means that for each part of the video where the sound level is below 0.01 for more than 350s, the corresponding silence will be cut.
* Enter 150ms as start and stop offsets. These are the durations which will be kept by default at the beginning and at the end of each silence cut.
* Click 'Next'; after some time, the window displays a list of 11 silences.
* Select the line of the 7th silence in the table (the one which last 1.7s).
* Ask for 1 second before and after silence previewed.
* Click on 'Silence preview' button: you can see the corresponding silence has been cut.
* On the line of the selected silence, enter a start offset of 500ms and a stop offset of 500ms also.
* Click again on 'Silence preview': this time, a more significant part of the silence has been kept.
* Click on the 'Generate' button.
* Play alphabet1_without_silences.mp4: you can see silences has been removed.

Known issues
============

On Ubuntu, the 'Preview silence' functionality does not seem to work properly.