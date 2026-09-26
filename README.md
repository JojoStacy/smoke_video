# Smoke – Play to Win explainer video

28.5s, 1080×1920 portrait explainer. Output: `out/play_to_win.mp4`.

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

## Folders
| Folder | What goes in it |
|---|---|
| `assets/screenshots/` | App screenshots and promo images |
| `assets/brand/` | Logo, wordmark, chest/bottle/sea artwork, fonts |
| `assets/voiceover/` | Recorded voiceover + the script (`script.md`) |
| `assets/music/` | Optional licensed music track |
| `src/` | The animated scenes (`index.html`) |
| `scripts/` | Voiceover, audio mix and render scripts |
| `audio/` | Generated voiceover, timings and final mix |
| `out/` | Rendered video (`play_to_win.mp4`) |
