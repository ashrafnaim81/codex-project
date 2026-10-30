import fs from 'node:fs';
import {execFileSync, spawnSync} from 'node:child_process';

function measurement(stderr) {
  const match = stderr.match(/\{\s*"input_i"[\s\S]*?\}/);
  if (!match) throw Error('ffmpeg tidak memulangkan ukuran LUFS');
  const result = JSON.parse(match[0]);
  for (const key of ['input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset']) {
    if (!Number.isFinite(Number(result[key]))) throw Error(`Ukuran audio tidak sah: ${key}`);
  }
  return result;
}

export function normalizeMix(input = 'out/mix.wav', output = 'out/mix-master.wav', report = 'out/loudness.json') {
  // Analyse then apply measured gain: never guess that a single volume multiplier is -14 LUFS.
  // execFileSync returns stdout only; use spawnSync for the loudnorm JSON on stderr.
  const first = analyze(input);
  const filter = [
    'loudnorm=I=-14:TP=-1.5:LRA=11',
    `measured_I=${first.input_i}`, `measured_TP=${first.input_tp}`,
    `measured_LRA=${first.input_lra}`, `measured_thresh=${first.input_thresh}`,
    `offset=${first.target_offset}`, 'linear=true:print_format=json'
  ].join(':');
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', input, '-af', filter,
    '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', output], {stdio: ['ignore', 'pipe', 'pipe']});
  let after = analyze(output);
  const corrections = [];
  // Dynamic loudnorm can miss the target on sparse effects. Measure and correct,
  // with oversampled peak limiting and compensated lookahead (no subtitle delay).
  for (let i = 0; i < 4 && (Math.abs(Number(after.input_i) + 14) > .4 || Number(after.input_tp) > -1.5); i++) {
    const gain = Math.max(-6, Math.min(6, -14 - Number(after.input_i)));
    const temp = `${output}.correcting.wav`;
    try {
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', output, '-af',
        `volume=${gain}dB,aresample=96000,alimiter=limit=0.78:level=false:latency=true`,
        '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', temp]);
      fs.renameSync(temp, output);
    } finally { fs.rmSync(temp, {force: true}); }
    after = analyze(output);
    corrections.push(after);
  }
  fs.writeFileSync(report, JSON.stringify({targetLUFS: -14, input: first, corrections, output: after}, null, 2));
  if (Math.abs(Number(after.input_i) + 14) > .75 || Number(after.input_tp) > -1.3) {
    throw Error(`Sasaran mastering tidak tercapai: ${after.input_i} LUFS / ${after.input_tp} dBTP`);
  }
  console.log(`Campuran akhir: ${after.input_i} LUFS · ${after.input_tp} dBTP`);
  return output;
}

export function analyze(input) {
  const result = spawnSync('ffmpeg', ['-hide_banner', '-i', input, '-af',
    'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], {encoding: 'utf8'});
  if (result.error) throw result.error;
  if (result.status !== 0) throw Error(result.stderr);
  return measurement(result.stderr);
}
