import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import yaml
from pydub import AudioSegment
from scipy.io import wavfile


def norm_audios(audio_dir):
    audio_files = [x for x in os.listdir(audio_dir) if x.endswith('.wav')]
    for audio in audio_files:
        os.system('ffmpeg-normalize {} -nt peak -o {}_normalized.wav'.format(
            audio.split('.')[0], audio.split('.')[0]))


def mix_audios(audio_dir):
    sounds = [AudioSegment.from_wav(x) for x in os.listdir(
        audio_dir) if x.endswith('_normalized.wav')]
    mixed = None
    for sound in sounds:
        if mixed is None:
            mixed = sound
        else:
            mixed.overlay(sound)
    mixed.export('mixed_normalized.wav', format='wav')


def prepare_data(audio_dir):
    norm_audios(audio_dir)
    mix_audios(audio_dir)
    audio_files = [x for x in os.listdir(
        audio_dir) if x.endswith('_normalized.wav')]
    audios_data = list()
    for audio in audio_files:
        rate, data = wavfile.read(audio)
        if rate != 44100:
            data = signal.resample(data, 44100)
        audios_data.append(data)

    return audios_data


def get_spectograms(audios_data):
    spectograms = list()
    for data in audios_data:
        # spec = (Array of sample frequencies, Array of segment times, STFT of x)
        #  By default, the last axis of spec[2] corresponds to the segment times
        spec = signal.stft(data, window=signal.get_window(
            'hann', 2048), noverlap=512)
        spectograms.append(spec)

    return spectograms


def get_audios(yaml_path):
    with open(yaml_path, 'r') as stream:
        metadata = yaml.load(stream)
        stem_dir = metadata['stem_dir']
        stems = metadata['stems']
        vocal = []
        non_vocal = []
        for stem in stems:
            if stems[stem]['instrument'] == 'female singer' or stems[stem]['instrument'] == 'male singer':
                vocal.append(stems[stem]['filename'])
            else:
                non_vocal.append(stems[stem]['filename'])

        return stem_dir, vocal, non_vocal
