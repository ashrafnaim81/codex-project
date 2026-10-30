#!/usr/bin/env bash
set -eu
mkdir -p out/voice
for i in {0..7}; do
 line=$(node -e "console.log(require('./src/lines.json')[$i])")
 n=$((i+1))
 if command -v say >/dev/null; then say -v Amira -o "out/voice/$n.aiff" "$line"; ffmpeg -v error -y -i "out/voice/$n.aiff" -ar 24000 -ac 1 "out/voice/$n.wav"; rm "out/voice/$n.aiff"
 elif command -v espeak-ng >/dev/null; then espeak-ng -v ms -w "out/voice/$n.wav" "$line"
 else rm -f "out/voice/$n.wav"; fi
done
