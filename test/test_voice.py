import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path

spec = importlib.util.spec_from_file_location('voice', Path(__file__).parents[1] / 'scripts/voice.py')
voice = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice)


class WordTimingTests(unittest.TestCase):
    def test_punctuation_and_service_token_splitting(self):
        words = voice.map_boundaries('Hai. Mikroorganisma... sebelum.', [
            {'text': 'Hai', 'start': .1, 'end': .3},
            {'text': 'Mikro', 'start': .4, 'end': .7},
            {'text': 'organisma', 'start': .7, 'end': 1.2},
            {'text': 'sebelum', 'start': 1.9, 'end': 2.5}])
        self.assertEqual([w['text'] for w in words], ['Hai.', 'Mikroorganisma...', 'sebelum.'])
        self.assertEqual(words[1]['start'], .4)
        self.assertEqual(words[1]['end'], 1.2)
        self.assertEqual(voice.map_boundaries('Hai.', [{'text': 'Hello', 'start': 0, 'end': 1}]), [])

    def test_pause_insertion_shifts_actual_word_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'test.wav'
            with wave.open(str(path), 'wb') as f:
                f.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                f.writeframes(b'\0\0' * (24000 * 3))
            words = [
                {'index': 0, 'text': 'saya...', 'start': .2, 'end': .8},
                {'index': 1, 'text': 'sebelum,', 'start': 1., 'end': 1.5},
                {'index': 2, 'text': 'hai.', 'start': 2., 'end': 2.5}]
            shifted = voice.insert_pauses(path, words)
            self.assertAlmostEqual(shifted[0]['end'], .8)
            self.assertAlmostEqual(shifted[1]['start'], 1.32)
            self.assertAlmostEqual(shifted[2]['start'], 2.395)
            with wave.open(str(path), 'rb') as f:
                self.assertEqual(f.getnframes(), round(3.395 * 24000))

    def test_polished_audio_keeps_duration_and_contains_signal(self):
        import math
        import struct
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp) / 'raw.wav', Path(temp) / 'clean.wav'
            with wave.open(str(source), 'wb') as f:
                f.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                f.writeframes(b''.join(struct.pack('<h', int(9000 * math.sin(i * 2 * math.pi * 440 / 24000))) for i in range(24000)))
            voice.save_line(Path(temp), 1, 'Ujian.', source, 'test', 'test', [])
            self.assertAlmostEqual(voice.duration(Path(temp) / '1.wav'), 1, places=3)


class FallbackTests(unittest.TestCase):
    def test_fails_closed_and_removes_stale_voice_when_every_engine_fails(self):
        from unittest.mock import patch
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'voice'
            output.mkdir()
            for i in range(1, 9):
                (output / f'{i}.wav').write_bytes(b'stale')
                (output / f'{i}.json').write_text('{}')
            calls = []
            def fail(args, **kwargs):
                calls.append(args[args.index('--worker') + 1])
                return subprocess.CompletedProcess(args, 1)
            with patch.object(voice, 'OUT', output), patch.object(voice.sys, 'argv', ['voice.py']), \
                 patch.dict(voice.os.environ, {'VOICE_ENGINE': 'auto', 'VOICE_REQUIRED': '0', 'VOICE_FORCE': '1'}), \
                 patch.object(voice.subprocess, 'run', side_effect=fail):
                voice.main()
            self.assertEqual(calls, ['edge', 'mms', 'say'])
            self.assertFalse(any(output.glob('*.wav')))
            self.assertEqual(json.loads((output / 'manifest.json').read_text())['engine'], 'none')


    def test_second_engine_commits_all_lines_and_cache_skips_regeneration(self):
        from unittest.mock import patch
        import json
        import subprocess
        lines = json.loads((voice.ROOT / 'src/narration.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'voice'
            calls = []
            def generate(args, **kwargs):
                engine = args[args.index('--worker') + 1]
                calls.append(engine)
                if engine == 'edge':
                    return subprocess.CompletedProcess(args, 1)
                folder = Path(args[args.index('--folder') + 1])
                for i, line in enumerate(lines, 1):
                    (folder / f'{i}.wav').write_bytes(b'test-only')
                    (folder / f'{i}.json').write_text(json.dumps({
                        'line': line, 'duration': 1, 'voice': 'test-fallback'}))
                return subprocess.CompletedProcess(args, 0)
            with patch.object(voice, 'OUT', output), patch.object(voice.sys, 'argv', ['voice.py']), \
                 patch.dict(voice.os.environ, {'VOICE_ENGINE': 'auto', 'VOICE_REQUIRED': '1', 'VOICE_FORCE': '0'}), \
                 patch.object(voice.subprocess, 'run', side_effect=generate), \
                 patch.object(voice, 'duration', return_value=1):
                voice.main()
                voice.main()
            self.assertEqual(calls, ['edge', 'mms'])
            self.assertEqual(len(list(output.glob('*.wav'))), 8)
            self.assertEqual(json.loads((output / 'manifest.json').read_text())['engine'], 'mms')


if __name__ == '__main__':
    unittest.main()
