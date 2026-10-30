#!/usr/bin/env python3
"""Free TTS adapters. Generation is transactional; never reuse stale narration."""
import argparse
import array
import asyncio
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out' / 'voice'
DEFAULT_VOICE = 'ms-MY-OsmanNeural'
MODEL = 'facebook/mms-tts-zlm'
REVISION = 'main'  # HF caches the resolved revision; no remote Python code is executed.
POLISH = 'highpass=f=75,equalizer=f=250:t=q:w=0.8:g=-1.5,equalizer=f=3000:t=q:w=0.8:g=1.2,acompressor=threshold=0.125:ratio=2:attack=15:release=180:makeup=1.2'


def run(args, **kwargs):
    return subprocess.run([str(v) for v in args], check=True, capture_output=True, **kwargs)


def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'default=nw=1:nk=1', path], text=True).stdout)


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', html.unescape(text)).casefold()
                   if c.isalnum())


def map_boundaries(line, boundaries):
    """Match service tokens to ORIGINAL subtitle words, including joined/split words.

    Refuse partial/mismatched alignments rather than silently highlighting wrong words.
    All times are seconds relative to the decoded line audio.
    """
    words = line.split()
    original = ''.join(normalize(w) for w in words)
    spoken = ''.join(normalize(b['text']) for b in boundaries)
    if not boundaries or original != spoken:
        return []
    spans, cursor = [], 0
    for b in boundaries:
        n = len(normalize(b['text']))
        if n:
            spans.append((cursor, cursor + n, b))
            cursor += n
    result, cursor = [], 0
    for index, word in enumerate(words):
        end = cursor + len(normalize(word))
        matches = [b for a, z, b in spans if a < end and z > cursor]
        if not matches:
            return []
        result.append({'index': index, 'text': word,
                       'start': min(b['start'] for b in matches),
                       'end': max(b['end'] for b in matches)})
        cursor = end
    return result


def insert_pauses(path, words):
    """Add breaths in real gaps, then shift boundaries by exactly the inserted samples."""
    if not words:
        return words
    with wave.open(str(path), 'rb') as f:
        params, raw = f.getparams(), f.readframes(f.getnframes())
    rate = params.framerate
    events = []
    for left, right in zip(words, words[1:]):
        punctuation = left['text']
        pause = .32 if '...' in punctuation or '…' in punctuation else .075 if punctuation.endswith(',') else .09 if punctuation.endswith(('.', '!', '?')) else 0
        # Do not cut speech if the service reports overlapping word boundaries.
        if pause and right['start'] >= left['end']:
            position = round((left['end'] + right['start']) / 2 * rate)
            position = max(0, min(len(raw) // 2, position))
            events.append((position, round(pause * rate)))
    events.sort()
    data, cursor = bytearray(), 0
    for position, samples in events:
        data.extend(raw[cursor * 2:position * 2])
        data.extend(b'\0\0' * samples)
        cursor = position
    data.extend(raw[cursor * 2:])
    with wave.open(str(path), 'wb') as f:
        f.setparams(params)
        f.writeframes(data)
    return [
        {**w, 'start': w['start'] + sum(n / rate for pos, n in events if pos / rate <= w['start']),
         'end': w['end'] + sum(n / rate for pos, n in events if pos / rate < w['end'])}
        for w in words]


def polish(source, dest):
    run(['ffmpeg', '-v', 'error', '-y', '-i', source, '-af', POLISH,
         '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', dest])


async def edge_generate(lines, folder, settings):
    import edge_tts
    # Respect the session proxy and CA trust. No ssl=False or direct fallback.
    ca = os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE')
    if ca:
        import ssl
        import edge_tts.communicate
        edge_tts.communicate._SSL_CTX = ssl.create_default_context(cafile=ca)
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    for i, line in enumerate(lines, 1):
        compressed, decoded = folder / f'{i}.mp3', folder / f'{i}.raw.wav'
        boundaries = []
        speech = edge_tts.Communicate(line, voice=settings['voice'], rate=settings['rate'],
                                     pitch=settings['pitch'], volume=settings['volume'],
                                     boundary='WordBoundary', proxy=proxy,
                                     connect_timeout=15, receive_timeout=45)
        with compressed.open('wb') as f:
            async for part in speech.stream():
                if part['type'] == 'audio':
                    f.write(part['data'])
                elif part['type'] == 'WordBoundary':
                    boundaries.append({'text': part['text'], 'start': part['offset'] / 10_000_000,
                                       'end': (part['offset'] + part['duration']) / 10_000_000})
        run(['ffmpeg', '-v', 'error', '-y', '-i', compressed, '-ar', '24000', '-ac', '1', decoded])
        words = map_boundaries(line, boundaries)
        if not words:
            print(f'Baris {i}: sempadan perkataan tidak sepadan; gunakan anggaran.', flush=True)
        words = insert_pauses(decoded, words)
        save_line(folder, i, line, decoded, 'edge', settings['voice'], words)
        compressed.unlink()
        decoded.unlink()


def mms_generate(lines, folder, settings):
    import numpy as np
    import torch
    from scipy.io.wavfile import write
    from transformers import AutoTokenizer, VitsModel, set_seed
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    options = {'revision': REVISION, 'trust_remote_code': False}
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, **options)
        model = VitsModel.from_pretrained(MODEL, local_files_only=True, **options)
    except OSError:
        # Fail promptly on explicit policy denial instead of Hub's repeated identical retries.
        import ssl
        import urllib.request
        ca = os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE')
        request = urllib.request.Request(f'https://huggingface.co/{MODEL}/resolve/{REVISION}/config.json', method='HEAD')
        with urllib.request.urlopen(request, timeout=20, context=ssl.create_default_context(cafile=ca)):
            pass
        tokenizer = AutoTokenizer.from_pretrained(MODEL, **options)
        model = VitsModel.from_pretrained(MODEL, **options)
    model = model.to('cpu').eval()
    model.speaking_rate = .92
    # MMS has no reliable word events. Synthesize clauses for natural pauses, preserving text.
    for i, line in enumerate(lines, 1):
        audio = []
        for j, clause in enumerate(re.findall(r'.+?(?:\.{3}|[,.!?]|$)', line)):
            if not clause.strip():
                continue
            set_seed(8100 + i * 100 + j)
            inputs = tokenizer(clause, return_tensors='pt')
            with torch.inference_mode():
                samples = model(**inputs).waveform[0].cpu().numpy()
            pause = .38 if clause.endswith('...') else .14 if clause.endswith(',') else .22
            audio.extend([samples, np.zeros(round(model.config.sampling_rate * pause), dtype=np.float32)])
        decoded = folder / f'{i}.raw.wav'
        write(decoded, model.config.sampling_rate, np.concatenate(audio))
        save_line(folder, i, line, decoded, 'mms', MODEL, [])
        decoded.unlink()


def say_generate(lines, folder, settings):
    if not shutil.which('say'):
        raise RuntimeError('macOS say tiada')
    for i, line in enumerate(lines, 1):
        source = folder / f'{i}.aiff'
        run(['say', '-v', 'Amira', '-r', '165', '-o', source, line])
        save_line(folder, i, line, source, 'say', 'Amira', [])
        source.unlink()


def save_line(folder, index, line, raw, engine, voice, words):
    dest = folder / f'{index}.wav'
    polish(raw, dest)
    seconds = duration(dest)
    if not math.isfinite(seconds) or seconds <= 0:
        raise RuntimeError(f'Audio kosong bagi baris {index}')
    # Ensure generated PCM contains a signal, not just a silent valid WAV.
    with wave.open(str(dest), 'rb') as f:
        pcm = array.array('h', f.readframes(f.getnframes()))
    if not pcm or max(abs(v) for v in pcm) < 32:
        raise RuntimeError(f'Audio senyap bagi baris {index}')
    if words and any(not (0 <= w['start'] < w['end'] <= seconds + .1) for w in words):
        print(f'Baris {index}: cap masa di luar audio; gunakan anggaran.', flush=True)
        words = []
    (folder / f'{index}.json').write_text(json.dumps({
        'line': line, 'engine': engine, 'voice': voice, 'duration': seconds,
        'timing': 'word-boundary' if words else 'estimated', 'words': words
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'[{engine} / {voice}] {index}/8 · {seconds:.2f}s · {"cap masa sebenar" if words else "anggaran"}', flush=True)


def settings_from_env():
    return {'voice': os.environ.get('VOICE', DEFAULT_VOICE),
            'rate': os.environ.get('VOICE_RATE', '-8%'),
            'pitch': os.environ.get('VOICE_PITCH', '-3Hz'),
            'volume': os.environ.get('VOICE_VOLUME', '+0%')}


def validate(folder, lines):
    for i, line in enumerate(lines, 1):
        meta = json.loads((folder / f'{i}.json').read_text())
        if meta['line'] != line or not (folder / f'{i}.wav').is_file():
            raise ValueError('Cache narasi tidak sepadan')
        if abs(duration(folder / f'{i}.wav') - meta['duration']) > .05:
            raise ValueError('Durasi cache berubah')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=['edge', 'mms', 'say'])
    parser.add_argument('--folder', type=Path)
    args = parser.parse_args()
    lines = json.loads((ROOT / 'src/narration.json').read_text())
    settings = settings_from_env()
    if args.worker:
        if args.worker == 'edge':
            asyncio.run(edge_generate(lines, args.folder, settings))
        else:
            {'mms': mms_generate, 'say': say_generate}[args.worker](lines, args.folder, settings)
        return
    requested = os.environ.get('VOICE_ENGINE', 'auto')
    if requested not in ['auto', 'edge', 'mms', 'say', 'none']:
        parser.error('VOICE_ENGINE mesti auto, edge, mms, say atau none')
    if requested == 'auto':
        chain = ['edge', 'mms', 'say']
    elif requested == 'none':
        chain = []
    else:
        chain = ['edge', 'mms', 'say'][['edge', 'mms', 'say'].index(requested):]
    # Cache keys include code and dependency versions so tuning never reuses old audio.
    versions = {}
    for name in ['edge-tts', 'transformers', 'torch']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    key = hashlib.sha256(json.dumps([lines, settings, requested, versions, Path(__file__).read_text()], sort_keys=True).encode()).hexdigest()
    manifest = OUT / 'manifest.json'
    if os.environ.get('VOICE_FORCE') != '1' and manifest.exists():
        try:
            old = json.loads(manifest.read_text())
        except (OSError, ValueError):
            old = {}
        if old.get('key') == key and old.get('engine') != 'none':
            try:
                validate(OUT, lines)
                print(f"Suara: {old['engine']} / {old['voice']} (cache disahkan)", flush=True)
                return
            except (OSError, ValueError, subprocess.SubprocessError) as e:
                print(f'Cache tidak sah: {e}', flush=True)
    for cmd in ['ffmpeg', 'ffprobe']:
        if not shutil.which(cmd):
            raise RuntimeError(f'{cmd} diperlukan')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    chosen, voice, failures = 'none', None, []
    with tempfile.TemporaryDirectory(prefix='voice-', dir=OUT.parent) as temp:
        staging = Path(temp)
        for engine in chain:
            try:
                # A broken online service cannot hang the fallback chain indefinitely.
                result = subprocess.run([sys.executable, __file__, '--worker', engine, '--folder', str(staging)],
                                        timeout=int(os.environ.get('VOICE_TIMEOUT', '300')), check=False)
                if result.returncode:
                    raise RuntimeError(f'kod keluar {result.returncode}')
                validate(staging, lines)
                chosen = engine
                voice = json.loads((staging / '1.json').read_text())['voice']
                break
            except (OSError, ValueError, subprocess.SubprocessError, RuntimeError) as e:
                print(f'Enjin {engine} gagal: {e}; cuba enjin seterusnya.', flush=True)
                failures.append({'engine': engine, 'error': str(e)})
                for path in staging.iterdir():
                    path.unlink()
        # No partial output or stale WAV survives a fallback to no voice.
        OUT.mkdir(exist_ok=True)
        for i in range(1, 9):
            for suffix in ['wav', 'json']:
                dest = OUT / f'{i}.{suffix}'
                if chosen != 'none':
                    os.replace(staging / dest.name, dest)
                else:
                    dest.unlink(missing_ok=True)
        manifest.write_text(json.dumps({'key': key, 'engine': chosen, 'voice': voice,
                                        'settings': settings, 'failures': failures}, indent=2) + '\n')
    print(f'Suara: {chosen} / {voice or "tiada suara; sari kata sahaja"}', flush=True)
    if chosen == 'none' and os.environ.get('VOICE_REQUIRED') == '1':
        raise SystemExit('VOICE_REQUIRED=1: tiada enjin berjaya')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError, RuntimeError, ImportError) as error:
        print(f'Ralat suara: {error}', file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr.decode(errors='replace') if isinstance(error.stderr, bytes) else error.stderr, file=sys.stderr)
        raise SystemExit(1)
