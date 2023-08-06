from __future__ import division
import pyaudio
import requests
import json
from collections import deque
import math
import audioop
import wave
import subprocess
import os
from termcolor import colored
import sys
import logging


class LongListener(object):
    """
    This is the listener object that can listen, transcribe, and return results
    """
    def __init__(self, vis=False,
                 fixed_silence_threshold=None,
                 silence_std_multilplier=3.5,  # how many std out fires the trigger?
                 silence_limit=1,
                 prev_audio=0.5):
        """
        Set a bunch of constants
        """
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'
        self.speech_api = {
            'url': 'https://www.google.com/speech-api/v2/recognize',
            'params': {
                'output': 'json',
                'key': 'AIzaSyCnl6MRydhw_5fLXIdASxkLJzcJh5iX0M4',
                'lang': 'en-US'
            },
            'headers': {
                'Content-type': 'audio/x-flac; rate=44100',
                'User-Agent': self.user_agent,
            }
        }
        self.wav_to_flac_command = ['flac', '--best', '-f', '-s']
        self.chunk = 1024  # in bytes
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.output_filename = "output"
        self.fixed_silence_threshold = fixed_silence_threshold
        self.silence_threshold = None
        self.silence_std_multilplier = silence_std_multilplier
        self.silence_limit = silence_limit
        self.prev_audio = prev_audio

        self.sample_size = None
        self.started = False
        self.first_pass = True
        self.visualization = vis
        self.logger = logging.getLogger()

    def transcribe(self, speech):
        """
        Transcribes speech using the configured API, returns dictionary
        """
        r = requests.post(self.speech_api['url'], speech, params=self.speech_api['params'], headers=self.speech_api['headers'])

        self.logger.debug('Google Speech Response: ', r.text)

        if r.text.split('\n')[0] == u'{"result":[]}':  # google returns two json objects, first one might be empty
            text = r.text.split('\n')[1]
        else:
            text = r.text.split('\n')[0]

        try:
            data = json.loads(text)
        except ValueError:
            data = {}

        return data

    def listen(self):
        """
        Listen long time, returns flacified data
        """
        # initialize
        self.sample_size = None
        self.started = False
        self.first_pass = True
        p = pyaudio.PyAudio()
        device_info = p.get_default_input_device_info()
        self.sample_size = p.get_sample_size(self.format)
        self.rate = int(device_info['defaultSampleRate'])
        self.channels = int(device_info['maxInputChannels'])

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        frames = []
        chunks_per_second = self.rate / self.chunk
        rolling_window = deque(maxlen=self.silence_limit * chunks_per_second)
        silence_threshold_window = deque(maxlen=self.silence_limit * chunks_per_second)
        # Prepend audio to give a little buffer of silence at the start
        previous_audio = deque(maxlen=self.prev_audio * chunks_per_second)

        #
        while True:
            cur_data = stream.read(self.chunk)
            rolling_window.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

            if self.visualization:
                self.terminal_visual(rolling_window)

            # adaptive silence threshold
            if self.fixed_silence_threshold:
                self.silence_threshold = self.fixed_silence_threshold
            else:
                self.silence_threshold = mean(rolling_window) + self.silence_std_multilplier * std(rolling_window)

            silence_threshold_window.append(self.silence_threshold)

            if self.started:
                if sum([1 for x in zip(rolling_window, silence_threshold_window) if x[0] > x[1]]):
                    frames.append(cur_data)
                else:
                    # We're finished
                    break
            else:
                if sum([x > self.silence_threshold for x in rolling_window]) > 0:
                    self.started = True
                else:
                    previous_audio.append(cur_data)

        final_frames = list(previous_audio) + frames

        self.logger.debug('Recording Captured: ' + str(len(final_frames) / chunks_per_second) + ' seconds')

        flac_data = self.flaccify(final_frames)

        stream.stop_stream()
        stream.close()
        p.terminate()

        return flac_data

    def flaccify(self, frames):
        """
        Take pyaudio data, save as a .wav file, then convert it to .flac
        file, then create a flac-formatted data object, clean up the files,
        and return the data
        """
        wf = wave.open(self.output_filename + ".wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sample_size)
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        conversion_command = self.wav_to_flac_command
        conversion_command.append(self.output_filename + '.wav')
        subprocess.call(conversion_command)

        with open(self.output_filename + '.flac', 'rb') as f:
            speech = f.read()

        os.remove(self.output_filename + '.wav')
        os.remove(self.output_filename + '.flac')

        return speech

    def terminal_visual(self, rolling_window, height=20, maximum_intensity=10000):
        """
        Makes a nifty visualization based on detected audio levels.
        Prints output, doesn't return anything
        """
        level_size = maximum_intensity / height

        if not self.first_pass:
            wipe(height)
        if self.first_pass:
            self.first_pass = False

        display = []
        for i in range(height):
            line_display = ''
            level = (i + 1) * level_size
            for j in rolling_window:
                line_display += get_visualizer_character(j, level, level / maximum_intensity, self.silence_threshold)
            display.append(line_display)

        for d in reversed(display):
            print(d)


def wipe(n):
    """
    Moves the cursor up and clears lines, for use with
    terminal visualizations where we want to overwrite
    (multiline progress bar or something)
    """
    for nn in range(n):
        sys.stdout.write("\x1b[A")    # moves up a line
        sys.stdout.write("\r\x1b[K")  # clears the line


def get_visualizer_character(n, level, level_rank, threshold):
    """
    Figure out which character to return based on the level, level's rank
    compared to maximum, and the silence threshold.  This is for the terminal
    visualization.
    """
    attrs = []
    if level > threshold:
        attrs.append('bold')
    q, r = divmod(n, level)
    if q > 0:
        return colored('|', level_color(level_rank), attrs=attrs)
    else:
        return ' '


def level_color(level_rank):
    """
    Figure out what color the characters in the visualization should be
    based on the level's rank compared to maximum.
    """
    if level_rank > 0.85:
        return 'red'
    elif level_rank > 0.7:
        return 'yellow'
    elif level_rank > 0.3:
        return 'green'
    elif level_rank > 0.15:
        return 'cyan'
    else:
        return 'blue'


def mean(list):
    return sum(list) / len(list)


def std(list):
    var = 1 / len(list) * sum([(mean(list) - i)**2 for i in list])
    return math.sqrt(var)
