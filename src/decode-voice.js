const {execFileSync} = require('child_process');

// ffmpeg emits 24 kHz mono float32: 96,000 bytes per second. Allow one
// extra second for rounding and resampler padding in addition to the probed
// duration. Node's default 1 MiB buffer is too small for ordinary narration.
module.exports = function decodeVoice(file, duration) {
  const maxBuffer = Math.ceil((duration + 1) * 24000 * 4);
  const bytes = execFileSync('ffmpeg', [
    '-v', 'error', '-i', file, '-f', 'f32le', '-ar', '24000', '-ac', '1', 'pipe:1'
  ], {maxBuffer});
  if (bytes.length % 4 !== 0) throw new Error(`Invalid decoded audio: ${file}`);
  return new Float32Array(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
};
