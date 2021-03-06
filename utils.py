import random
import pathlib

import numpy
import librosa


class Preprocess(object):
    def __init__(self, sr, n_fft, hop_length, n_mels, fmin, fmax, top_db,
                 length):
        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax
        self.top_db = top_db

        if length is None:
            self.length = None
        else:
            self.length = length
        self.output_dim = 1

    def __call__(self, path):
        # load data(trim and normalize)
        raw, _ = librosa.load(path, self.sr)
        raw, _ = librosa.effects.trim(raw, self.top_db)
        raw += 1
        raw *= (2 ** 16 - 1) / 2
        raw += numpy.random.uniform(size=raw.shape)
        raw /= (2 ** 16 - 1) / 2
        raw -= 1
        raw = raw.astype(numpy.float32)

        # padding/triming
        if self.length is not None:
            if len(raw) <= self.length:
                # padding
                pad = self.length - len(raw)
                raw = numpy.concatenate(
                    (raw, numpy.zeros(pad, dtype=numpy.float32)))
            else:
                # triming
                start = random.randint(0, len(raw) - self.length - 1)
                raw = raw[start:start + self.length]

        # make mel spectrogram
        spectrogram = librosa.feature.melspectrogram(
            raw, self.sr, n_fft=self.n_fft, hop_length=self.hop_length,
            n_mels=self.n_mels, fmin=self.fmin, fmax=self.fmax)
        spectrogram = librosa.power_to_db(
            spectrogram, ref=numpy.max)
        spectrogram += 80
        spectrogram /= 80
        if self.length is not None:
            spectrogram = spectrogram[:, :self.length // self.hop_length]
        spectrogram = spectrogram.astype(numpy.float32)

        # expand dimensions
        raw = numpy.expand_dims(raw, 0)  # expand channel
        return raw, spectrogram


def get_LJSpeech_paths(root):
    filepaths = sorted([
        str(path) for path in pathlib.Path(root).glob('wavs/*.wav')])
    metadata_path = pathlib.Path(root).joinpath('metadata.csv')
    return filepaths, metadata_path


def get_VCTK_paths(root):
    filepaths = sorted([
        str(path) for path in pathlib.Path(root).glob('wav48/*/*.wav')])
    metadata_paths = sorted([
        str(path) for path in pathlib.Path(root).glob('txt/*/*.txt')])
    return filepaths, metadata_paths
