# Smoke – Play to Win explainer video

28.5s, 1920×1080 landscape explainer. Output: `out/play_to_win.mp4`.

## Build
```bash
npm install
pip install kokoro-onnx soundfile numpy imageio-ffmpeg
python3 scripts/voiceover.py      # audio/vo.wav + audio/timing.json (needs Kokoro model files, see script)
python3 scripts/audio.py          # audio/mix.wav (music + SFX + ducked VO)
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") node scripts/render.mjs
node scripts/render.mjs --stills 2.5,8.9,23.9   # preview stills in out/stills/
```
Scenes live in `src/index.html` (`render(t)` draws the frame at time `t`); open it in a browser for a live preview.
