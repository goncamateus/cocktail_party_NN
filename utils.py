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
        singer = audio.split('_STEM')[0]
        final_dir = os.path.join('NormAudios', singer)
        if not (os.path.exists(final_dir)):
            os.makedirs(final_dir)
        os.system('ffmpeg-normalize {} -nt peak -o {}.wav'.format(
            os.path.join(audio_dir, audio), os.path.join(final_dir, audio.split('.')[0])))


def mix_audios(audio_dir, vocals, non_vocals, names=['mixed', 'vocals', 'non_vocals']):
    sounds = [AudioSegment.from_wav(os.path.join(audio_dir, x)) for x in os.listdir(
        audio_dir) if x.endswith('.wav')]
    voices = [AudioSegment.from_wav(os.path.join(audio_dir, x)) for x in os.listdir(
        audio_dir) if x in vocals]
    instruments = voices = [AudioSegment.from_wav(os.path.join(audio_dir, x)) for x in os.listdir(
        audio_dir) if x in non_vocals]
    print(vocals, non_vocals)
    mixed = None
    mixv = None
    mixn = None
    for sound in sounds:
        if mixed is None:
            mixed = sound
        else:
            mixed.overlay(sound)
    for sound in voices:
        if mixv is None:
            mixv = sound
        else:
            mixv.overlay(sound)
    for sound in instruments:
        if mixn is None:
            mixn = sound
        else:
            mixn.overlay(sound)
    mixed.export('{}.wav'.format(os.path.join(
        audio_dir, names[0])), format='wav')
    if mixv is not None:
        voc = os.path.join(audio_dir, 'Vocals')
        if not (os.path.exists(voc)):
            os.makedirs(voc)
        mixv.export('{}.wav'.format(os.path.join(voc, names[1])), format='wav')
    if mixn is not None:
        nvoc = os.path.join(audio_dir, 'Non_Vocals')
        if not (os.path.exists(nvoc)):
            os.makedirs(nvoc)
        mixn.export('{}.wav'.format(
            os.path.join(nvoc, names[2])), format='wav')


def prepare_data(audio_dir, yaml_path, norm_dir='NormAudios'):
    norm_audios(audio_dir)
    stems, vocals, non_vocals = get_audios(yaml_path)
    singer = stems.split('_STEMS')[0]
    path = os.path.join(norm_dir, singer)
    mix_audios(path,  vocals, non_vocals)
    audio_files = [x for x in os.listdir(
        path) if x.endswith('.wav')]
    audios_data = list()
    for audio in audio_files:
        rate, data = wavfile.read(os.path.join(path, audio))
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
