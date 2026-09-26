// Renders src/index.html frame-by-frame with Playwright and pipes the frames into ffmpeg.
// Usage: node scripts/render.mjs [--stills 1,5,9] [--out out/play_to_win.mp4]
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith('--') && a.push([v.slice(2), arr[i + 1]]), a), []));
const FPS = 30, DURATION = 28.5;
const timing = JSON.parse(fs.readFileSync(path.join(root, 'audio/timing.json'), 'utf8'));
const ffmpeg = process.env.FFMPEG || 'ffmpeg';

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || undefined });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.addInitScript(t => { window.RENDERING = true; window.TIMING = t; }, timing);
await page.goto('file://' + path.join(root, 'src/index.html'));
await page.evaluate(() => document.fonts.ready);

if (args.stills) {
  fs.mkdirSync(path.join(root, 'out/stills'), { recursive: true });
  for (const s of args.stills.split(',').map(Number)) {
    // warm up stateful animations (leaderboard easing) by stepping to the time
    for (let t = Math.max(0, s - 1); t <= s; t += 1 / FPS) await page.evaluate(t => render(t), t);
    await page.screenshot({ path: path.join(root, `out/stills/t${s}.png`) });
  }
} else {
  const out = path.join(root, args.out || 'out/play_to_win.mp4');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const ff = spawn(ffmpeg, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(root, 'audio/mix.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(DURATION * FPS);
  for (let i = 0; i < N; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stderr.write(`frame ${i}/${N}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await browser.close();
