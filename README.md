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

TODO

Installation:
=============

(The following will work for Window only, and maybe only for Window 10. If you have another operating system, please do the installation from sources.)

* Install ffmpeg (this step is optional)
* Download archive SilenceRemover-1.0.0.zip
* Unzip archive in a folder of your choice.
* Go in this folder and launch SilenceRemover.exe. (This should launch the software.)

Installation from sources:
==========================

* Install python 3.9 (this should also install pip)
* Install ffmpeg (this step is optional)
* Open a terminal (on Window this can be done by launching 'cmd' or 'powershell'). 
* Enter the following line:
  pip install PySide2==5.15.1 numpy==1.19.3 matplotlib==3.2.2 moviepy==1.0.3 proglog==0.1.9 pygame==2.0.0
* Download sources of SilenceRemover from github
* In the terminal, go in the folder where you downloaded the sources.
* Enter the following line:
  python SilenceRemover.py
  (This should launch the software.)
  
