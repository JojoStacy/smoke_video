"""Builds audio/mix.wav: synthesized amapiano-style beat + SFX + voiceover (ducked).

Run after scripts/voiceover.py. Everything is generated offline with numpy.
"""
import json
import os

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
DUR = 28.5
N = int(SR * DUR)
rng = np.random.default_rng(3)


def t_(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=0.2):
    e = np.ones(n)
    na, nr = int(SR * a), min(n, int(SR * r))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.exp(-np.linspace(0, 6, nr))
    return e


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def lowpass(x, k=0.05):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


# ---------------- music ----------------
BPM = 112
beat = 60 / BPM
music = np.zeros(N)


def kick():
    t = t_(0.35)
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def log_drum(freq):
    # amapiano "log drum": pitched, gliding, slightly saturated
    t = t_(0.45)
    f = freq * (1 + 0.6 * np.exp(-t * 25))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    return np.tanh(2.2 * x) * 0.8


def shaker():
    n = rng.standard_normal(int(SR * 0.06))
    n = n - lowpass(n, 0.3)
    return n * env(len(n), 0.002, 0.05) * 0.5


def clap():
    n = rng.standard_normal(int(SR * 0.18))
    n = n - lowpass(n, 0.15)
    e = np.exp(-t_(0.18) * 22)
    return n * e * 0.6


def pad(freqs, d):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.3 * t)) for f in freqs) / len(freqs)
    return x * env(len(t), 0.4, 0.6)


chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 246.94, 293.66], [164.81, 196.0, 246.94]]  # Am F G Em
bass_notes = [55.0, 43.65, 49.0, 41.2]
bar = beat * 4
nbars = int(DUR / bar) + 1
for b in range(nbars):
    t0 = b * bar
    ch = b % 4
    add(music, pad(chords[ch], bar), t0, 0.10)
    for k in range(4):
        add(music, kick(), t0 + k * beat, 0.55)
        add(music, clap(), t0 + k * beat + beat / 2 if k % 2 else t0 + k * beat + beat, 0.0)
    add(music, clap(), t0 + beat, 0.22)
    add(music, clap(), t0 + 3 * beat, 0.22)
    for k in range(16):
        add(music, shaker(), t0 + k * beat / 4, 0.18 if k % 2 else 0.1)
    # syncopated log drum pattern
    for pos in [0, 0.75, 1.5, 2.5, 3.25]:
        add(music, log_drum(bass_notes[ch] * 2), t0 + pos * beat, 0.45)

# ---------------- SFX ----------------
sfx = np.zeros(N)


def whoosh(d=0.5):
    n = rng.standard_normal(int(SR * d))
    e = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    return lowpass(n, 0.08) * e * 1.5


def blip(f=900, d=0.08):
    t = t_(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 40)


def ding(f=1320):
    t = t_(0.9)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 5)


def pop():
    t = t_(0.09)
    f = 600 + 900 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)


def coin(f):
    t = t_(0.25)
    return (np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.5 * t) * 0.6) * np.exp(-t * 14)


def boom():
    t = t_(1.0)
    f = 40 + 80 * np.exp(-t * 12)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    n = lowpass(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 6)
    return x + n * 2


def glass():
    out = np.zeros(int(SR * 0.8))
    for _ in range(14):
        f = rng.uniform(2500, 6000)
        tt = t_(rng.uniform(0.1, 0.4))
        s = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18)
        i = int(rng.uniform(0, 0.25) * SR)
        out[i:i + len(s)] += s[: len(out) - i]
    return out * 0.4


for at in [4.6, 6.65, 10.4, 13.85, 16.1, 22.9]:
    add(sfx, whoosh(), at - 0.2, 0.35)
for at in [5.1]:
    add(sfx, boom(), at, 0.5)
for i in range(7):  # typing kevo254
    add(sfx, blip(1800, 0.03), 7.5 + i * 0.15, 0.15)
add(sfx, blip(900), 9.4, 0.4)
add(sfx, ding(1046), 9.45, 0.25)
add(sfx, blip(700), 10.8, 0.3)
add(sfx, ding(1318), 11.4, 0.35)
add(sfx, ding(1760), 11.55, 0.25)
add(sfx, blip(900), 13.35, 0.4)
for i in range(9):  # candy pops
    add(sfx, pop(), 14.1 + i * 0.22, 0.35)
add(sfx, blip(900), 16.7, 0.4)
add(sfx, glass(), 17.0, 0.6)
add(sfx, boom(), 17.05, 0.35)
add(sfx, boom(), 23.25, 0.8)  # chest opens
for i in range(40):  # coin shower
    add(sfx, coin(rng.uniform(1800, 3200)), 23.3 + i * 0.045 + rng.uniform(0, 0.03), 0.18)
add(sfx, ding(1568), 24.4, 0.3)

# ---------------- voiceover + ducking ----------------
vo, vsr = sf.read(os.path.join(ROOT, "audio/vo.wav"))
if vo.ndim > 1:
    vo = vo.mean(axis=1)
idx = np.arange(0, len(vo) * SR / vsr) * vsr / SR
vo = np.interp(idx, np.arange(len(vo)), vo)
vo_buf = np.zeros(N)
add(vo_buf, vo, 0.0, 1.0)

timing = json.load(open(os.path.join(ROOT, "audio/timing.json")))
duck = np.ones(N)
for seg in timing:
    a, b = int((seg["start"] - 0.15) * SR), int((seg["end"] + 0.2) * SR)
    duck[max(a, 0):b] = 0.35
duck = lowpass(duck, 0.0008)

fade = np.ones(N)
fade[-int(SR * 1.2):] = np.linspace(1, 0, int(SR * 1.2))
fade[:int(SR * 0.3)] = np.linspace(0, 1, int(SR * 0.3))

mix = music * 0.55 * duck * fade + sfx * 0.8 * fade + vo_buf * 1.1
mix = np.tanh(mix * 0.9) * 0.95  # soft limiter
sf.write(os.path.join(ROOT, "audio/mix.wav"), np.stack([mix, mix], axis=1), SR)
print("wrote audio/mix.wav", round(len(mix) / SR, 2), "s, peak", round(float(np.abs(mix).max()), 3))
