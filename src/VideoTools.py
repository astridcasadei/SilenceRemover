# This Python file uses the following encoding: utf-8

import os
import re
import numpy as np
import pygame
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
from PySide2.QtCore import Signal, QObject
from SilenceData import SilenceData

MS_TO_SEC = 0.001
EPS = 1e-4


class VideoTools(QObject):

    silence_comput_progress = Signal(int)
    video_generation_progress = Signal(int)

    def compute_silences(self, filename, noise_threshold, max_silence_duration,
                         start_offset_def, stop_offset_def):
        start_stop_list, video_duration = self.compute_silences_start_and_stop(filename,
                                                                               noise_threshold,
                                                                               max_silence_duration * MS_TO_SEC)
        silence_list = []
        iden = 0
        for (start, stop) in start_stop_list:
            start_offset = start_offset_def
            stop_offset = stop_offset_def
            start_offset_changeable = stop_offset_changeable = True
            if abs(start) < EPS:
                start_offset = 0
                start_offset_changeable = False
            if abs(stop - video_duration) < EPS:
                stop_offset = 0
                stop_offset_changeable = False
            silence = SilenceData(id, start, stop, start_offset, stop_offset,
                                  start_offset_changeable, stop_offset_changeable)
            silence_list.append(silence)
            iden += 1
        return silence_list

    def compute_silences_start_and_stop(self, filename, noise_threshold, max_silence_duration):

        self.silence_comput_progress.emit(1)

        # Open video clip
        videoclip = VideoFileClip(filename)
        self.silence_comput_progress.emit(3)

        # Compute volume array from video file
        audio_fps = videoclip.audio.fps
        sound_array = videoclip.audio.subclip().to_soundarray(fps=audio_fps)
        n_sound = np.shape(sound_array)[0]  # We have n / customFps = duration_in_seconds
        self.silence_comput_progress.emit(17)

        volume_fn = lambda p : p[0]*p[0] + p[1]*p[1]
        volumes = np.array(list(map(volume_fn, sound_array)))
        self.silence_comput_progress.emit(85)

        # Find silences
        start = 0  # Current silence begins at 'start' index and ends just before 'stop' index
        silence_list = []
        square_noise_threshold = noise_threshold**2

        for i in range(n_sound+1):

            if ((i == n_sound) or (volumes[i] > square_noise_threshold)):
                stop = i
                silence_duration = (stop - start) / audio_fps
                if silence_duration > max_silence_duration:

                    start_time = start / audio_fps
                    stop_time = stop / audio_fps
                    silence_list.append([start_time, stop_time])
                start = i + 1

        video_duration = videoclip.duration
        self.silence_comput_progress.emit(100)
        videoclip.close()
        return silence_list, video_duration

    def preview_video(self, filename, playtime_before, playtime_after, silence):
        videoclip = VideoFileClip(filename)

        start = max(0, silence.start_time - playtime_before)
        stop = min(videoclip.duration, silence.stop_time + playtime_after)
        start_cut = silence.start_cut()
        stop_cut = silence.stop_cut()

        if start_cut < stop_cut:
            cliplist = []

            if start < start_cut:
                cliplist.append(videoclip.subclip(start, start_cut))
            if stop_cut < stop:
                cliplist.append(videoclip.subclip(stop_cut, stop))

            assert len(cliplist) > 0
            tmpclip = concatenate_videoclips(cliplist)
        else:
            tmpclip = videoclip.subclip(start, stop)

        pygame.display.set_caption('Silence cut preview')
        os.environ['SDL_VIDEO_WINDOW_POS']='%d,%d' %(0,30)

        aud = tmpclip.audio.set_fps(44100)
        tmpclip = tmpclip.without_audio().set_audio(aud)
        tmpclip.preview()
        pygame.display.quit()

        videoclip.close()

    def write_video(self, input_filename, output_filename, silence_list, progress_bar_logger):
        self.video_generation_progress.emit(0)

        videoclip = VideoFileClip(input_filename)

        # Choose output audio/video bitrate based on values for input video
        # (Note : in fact specifying bitrate is only relevant for some codecs, e.g. libx264)
        output_video_bitrate = '24000k'
        output_audio_bitrate = '190k'

        tmpfilename = "tmpfile.out"
        os.system("ffmpeg -i \"%s\" 2> %s" % (input_filename, tmpfilename))
        tmpfile = open(tmpfilename, 'r')
        lines = tmpfile.readlines()
        tmpfile.close()
        os.remove(tmpfilename)

        for line in lines:
            line = line.strip()
            if line.startswith('Stream #0:0'):
                search = re.search('(\d+ kb/s)', line)
                if search is not None:
                    output_video_bitrate = search.group(1)
                    output_video_bitrate = output_video_bitrate[:-3]
                else:
                    print("Note: took default video bitrate")
            if line.startswith('Stream #0:1'):
                search = re.search('(\d+ kb/s)', line)
                if search is not None:
                    output_audio_bitrate = search.group(1)
                    output_audio_bitrate = output_audio_bitrate[:-3]
                else:
                    print("Note: took default audio bitrate")

        # Choose output audio fps based on value for input video
        output_audio_fps = 48000
        infos = ffmpeg_parse_infos(input_filename)
        if 'audio_fps' in infos:
            output_audio_fps = infos['audio_fps']

        # Remove pseudo-silences
        clean_silence_list = []
        for silence in silence_list:
            if silence.start_cut() < silence.stop_cut():
                clean_silence_list.append(silence)

        n_sil = len(clean_silence_list)

        # Subclip before the first silence (if exist)
        subclips = []
        start_time = 0
        if n_sil > 0:
            stop_time = clean_silence_list[0].start_cut()
        else:
            stop_time = videoclip.duration

        if start_time < stop_time:
            subclips.append(videoclip.subclip(start_time, stop_time))

        # Subclips between silences
        for i in range(n_sil-1):
            start_time = clean_silence_list[i].stop_cut()
            stop_time = clean_silence_list[i+1].start_cut()
            subclips.append(videoclip.subclip(start_time, stop_time))
            val = i / (n_sil-1) * 11
            self.video_generation_progress.emit(val)

        # Subclip after last silence (if exist)
        if n_sil > 0:
            start_time = clean_silence_list[n_sil-1].stop_cut()
            stop_time = videoclip.duration
            if start_time != stop_time:
                subclips.append(videoclip.subclip(start_time, stop_time))

        self.video_generation_progress.emit(11)

        # Create final clip
        final_clip = concatenate_videoclips(subclips)

        final_clip.write_videofile(output_filename,
                                   fps=videoclip.fps,
                                   audio_fps=output_audio_fps,
                                   bitrate=output_video_bitrate,
                                   audio_bitrate=output_audio_bitrate,
                                   preset='ultrafast',  # 'placebo' = very slow but smaller file size,
                                                        # 'ultrafast' = a lot faster but silghtly
                                                        #        higher file size (and same quality)
                                   logger=progress_bar_logger)

        self.video_generation_progress.emit(99)
        videoclip.close()
        self.video_generation_progress.emit(100)
