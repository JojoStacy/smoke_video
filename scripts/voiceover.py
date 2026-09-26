"""Generates audio/vo.wav + audio/timing.json with Kokoro TTS (offline).

Model files (download once from github.com/thewh1teagle/kokoro-onnx releases, model-files-v1.0):
  KOKORO_MODEL=kokoro-v1.0.onnx  KOKORO_VOICES=voices-v1.0.bin
"""
import json
import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro(os.environ.get("KOKORO_MODEL", "kokoro-v1.0.onnx"), os.environ.get("KOKORO_VOICES", "voices-v1.0.bin"))
# warm female blend; British phonemes sit closer to Kenyan English than American ones
voice = 0.55 * k.get_voice_style("af_heart") + 0.45 * k.get_voice_style("bf_emma")

LINES = [
    ("intro", "Sasa! Smoke is the app for real conversations, and real connections."),
    ("feature", "And now? We've got Play to Win."),
    ("handle", "New on Smoke? Just drop the handle of the friend who invited you."),
    ("counter", "Boom. Their chance counter goes up. Referral confirmed."),
    ("game", "Then play, climb the leaderboard, and crack open the treasure chest."),
    ("free", "It's totally free to play. Pure skill, no gambling. And every invite grows the Smoke fam."),
    ("outro", "Smoke. Play to Win."),
]
OUTRO_AT = 25.3  # land the tagline on the end card

sr, gap, t = 24000, 0.35, 0.4
out, timing = [np.zeros(int(sr * t))], []
for key, text in LINES:
    s, _ = k.create(text, voice=voice, speed=1.08, lang="en-gb")
    d = len(s) / sr
    timing.append({"key": key, "start": round(t, 3), "end": round(t + d, 3), "text": text})
    pad = max(gap, OUTRO_AT - (t + d)) if key == "free" else gap
    out += [s, np.zeros(int(sr * pad))]
    t += d + pad

os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
sf.write(os.path.join(ROOT, "audio/vo.wav"), np.concatenate(out), sr)
json.dump(timing, open(os.path.join(ROOT, "audio/timing.json"), "w"), indent=1)
print(json.dumps(timing, indent=1))
