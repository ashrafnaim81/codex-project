import fs from 'node:fs';
import {execFileSync} from 'node:child_process';

export const narration = JSON.parse(fs.readFileSync(new URL('./narration.json', import.meta.url)));

export function readWordTimings(file, line, duration) {
  try {
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));
    const tokens = line.split(/\s+/);
    if (data.line !== line || data.timing !== 'word-boundary' || data.words.length !== tokens.length) return [];
    let previous = -1;
    for (const [i, word] of data.words.entries()) {
      if (word.index !== i || word.text !== tokens[i] || !Number.isFinite(word.start) ||
          !Number.isFinite(word.end) || word.start < previous || word.start < 0 ||
          word.end <= word.start || word.end > duration + .1) return [];
      previous = word.start;
    }
    return data.words;
  } catch { return []; }
}

export function buildTimeline(dir = 'out/voice') {
  let start = 0;
  return narration.map((line, i) => {
    const file = `${dir}/${i + 1}.wav`;
    const voiced = fs.existsSync(file);
    const audio = voiced ? Number(execFileSync('ffprobe', [
      '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', file
    ], {encoding: 'utf8'})) : 0;
    if (voiced && (!Number.isFinite(audio) || audio <= 0)) throw Error(`Audio tidak sah: ${file}`);
    const duration = voiced ? audio + 1.2 : Math.max(5, line.split(/\s+/).length / 2.05 + .8);
    const words = voiced ? readWordTimings(`${dir}/${i + 1}.json`, line, audio) : [];
    const scene = {index: i, line, start, duration, audio, file: voiced ? file : null,
      timing: words.length ? 'word-boundary' : 'estimated', words};
    start += duration;
    return scene;
  });
}

export function at(t, timeline) {
  return timeline.find(s => t < s.start + s.duration) || timeline.at(-1);
}

// Real timings stop highlighting during breaths. Focus keeps the current subtitle page visible.
export function subtitleState(scene, t) {
  if (scene.words?.length) {
    const active = scene.words.findIndex(w => t >= w.start && t < w.end);
    const preceding = scene.words.findLastIndex(w => t >= w.start);
    return {active, focus: Math.max(0, active >= 0 ? active : preceding)};
  }
  const count = scene.line.split(/\s+/).length;
  const span = scene.audio || scene.duration - .5;
  const focus = Math.max(0, Math.min(count - 1, Math.floor(t / span * count)));
  return {active: t >= 0 && t < span ? focus : -1, focus};
}
