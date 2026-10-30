#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out/voice
if command -v say >/dev/null 2>&1; then
  engine=say
elif command -v espeak-ng >/dev/null 2>&1; then
  engine=espeak-ng
else
  echo "Tiada say/espeak-ng: teruskan tanpa suara; sari kata dikekalkan."
  exit 0
fi
for i in {1..8}; do
  text=$(node --input-type=module -e "import fs from 'node:fs'; console.log(JSON.parse(fs.readFileSync('src/narration.json'))[$i-1])")
  if [ "$engine" = say ]; then
    say -v Amira -r 180 -o "out/voice/$i.aiff" "$text"
    ffmpeg -v error -y -i "out/voice/$i.aiff" -ar 24000 -ac 1 "out/voice/$i.wav"
    rm "out/voice/$i.aiff"
  else
    espeak-ng -v ms -s 180 -w "out/voice/$i.wav" "$text"
  fi
done
