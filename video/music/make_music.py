"""Nappe cinématique originale de 10,5 s : Ré mineur -> Si bémol -> Fa,
impact grave au changement d'accord (4,5 s, zoom de la caméra), scintillement aigu
qui monte sur la fin. Sortie : WAV stéréo 48 kHz."""
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
DUR = 10.5
t = np.arange(int(SR * DUR)) / SR
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def saw_voice(freq, detune_cents, phase):
    out = np.zeros_like(t)
    for d in detune_cents:
        f = freq * 2 ** (d / 1200)
        vib = 1 + 0.0015 * np.sin(2 * np.pi * 4.8 * t + phase)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR + phase
        for n in range(1, 9):
            out += np.sin(n * ph) / n
    return out / len(detune_cents)


def window(start, end, fade):
    w = np.clip((t - start) / fade + 0.5, 0, 1) * np.clip((end - t) / fade + 0.5, 0, 1)
    return np.sin(w * np.pi / 2) ** 2


# (début, fin, notes MIDI)
chords = [
    (-1.0, 4.5, [38, 50, 57, 62, 65]),  # Ré mineur
    (4.5, 7.5, [34, 46, 53, 62, 65]),  # Si bémol
    (7.5, 12.0, [41, 53, 60, 65, 69]),  # Fa
]

lp = butter(4, 1600, "low", fs=SR, output="sos")
channels = []
for ch, det in enumerate(([-7, 0, 6], [-5, 1, 8])):
    pad = np.zeros_like(t)
    for start, end, notes in chords:
        w = window(start, end, 1.4)
        for i, m in enumerate(notes):
            amp = 0.9 if i == 0 else 0.55
            pad += amp * w * saw_voice(hz(m), det, phase=ch * 1.3 + i)
    pad = sosfilt(lp, pad)

    # Scintillement aigu (La5, Do6, Fa6) qui apparaît progressivement après 5 s.
    shimmer = sum(np.sin(2 * np.pi * hz(m) * t + ch + k) for k, m in enumerate([81, 84, 89]))
    shimmer *= np.clip((t - 5.0) / 4.0, 0, 1) ** 2 * (1 + 0.3 * np.sin(2 * np.pi * 0.7 * t + ch))
    pad += 0.18 * shimmer

    # Impact grave (type timbale) au changement d'accord.
    tb = t - 4.5
    boom = np.where(tb >= 0, np.sin(2 * np.pi * 48 * tb * (1 + 0.4 * np.exp(-tb * 8))) * np.exp(-tb * 1.6) * np.clip(tb / 0.012, 0, 1), 0)
    pad += 2.2 * boom
    channels.append(pad)

sig = np.stack(channels)

# Réverbération : réponse impulsionnelle de bruit décroissant (2,8 s), différente par canal.
ir_len = int(SR * 2.8)
ir_t = np.arange(ir_len) / SR
ir_lp = butter(2, 5000, "low", fs=SR, output="sos")
wet = []
for ch in range(2):
    ir = sosfilt(ir_lp, rng.standard_normal(ir_len)) * np.exp(-ir_t * 2.4)
    wet.append(fftconvolve(sig[ch], ir)[: sig.shape[1]])
wet = np.stack(wet)
wet *= np.abs(sig).max() / np.abs(wet).max()
mix = 0.65 * sig + 0.5 * wet

# Enveloppe globale : entrée douce, fin en fondu.
env = np.clip(t / 2.0, 0, 1) ** 1.5 * np.clip((DUR - t) / 1.2, 0, 1)
mix *= env
mix /= np.abs(mix).max()
mix *= 10 ** (-3 / 20)

pcm = (mix.T * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes(pcm.tobytes())
