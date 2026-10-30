#!/usr/bin/env python3
"""Generate a complete set of voice lines with an ordered free fallback chain."""
import asyncio, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINES = json.loads((ROOT / 'src/lines.json').read_text())
DEST = ROOT / 'out/voice'
VOICE = os.getenv('VOICE', 'ms-MY-OsmanNeural')

def run(*args):
    subprocess.run(list(map(str, args)), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def clean(s):
    return ''.join(c for c in unicodedata.normalize('NFKC', s).casefold() if c.isalnum())

def align(line, boundaries):
    words = line.split()
    if ''.join(map(clean, words)) != ''.join(clean(b['text']) for b in boundaries):
        return []
    spans, pos = [], 0
    for b in boundaries:
        end = pos + len(clean(b['text']))
        if end > pos: spans.append((pos, end, b))
        pos = end
    out, pos = [], 0
    for i, word in enumerate(words):
        end = pos + len(clean(word))
        matches = [b for a,z,b in spans if a < end and z > pos]
        if not matches: return []
        out.append({'index':i,'text':word,'start':min(b['start'] for b in matches),'end':max(b['end'] for b in matches)})
        pos = end
    return out

def pauses(path, words):
    if not words: return words
    with wave.open(str(path),'rb') as f:
        params, data = f.getparams(), f.readframes(f.getnframes())
    rate = params.framerate
    events=[]
    for a,b in zip(words,words[1:]):
        gap=.30 if '...' in a['text'] else .07 if a['text'].endswith(',') else .08 if a['text'].endswith(('.','!','?')) else 0
        if gap and b['start']>=a['end']:
            sample=round((a['end']+b['start'])*rate/2)
            if 0<=sample<=len(data)//2: events.append((sample,round(gap*rate)))
    chunks=[]; previous=0
    for pos,n in events:
        chunks += [data[previous*2:pos*2], b'\0\0'*n]; previous=pos
    chunks.append(data[previous*2:])
    with wave.open(str(path),'wb') as f:
        f.setparams(params); f.writeframes(b''.join(chunks))
    return [{**w,'start':w['start']+sum(n/rate for pos,n in events if pos/rate<=w['start']),
             'end':w['end']+sum(n/rate for pos,n in events if pos/rate<w['end'])} for w in words]

def output(folder, number, raw, line, words):
    dst=folder/f'{number}.wav'
    run('ffmpeg','-v','error','-y','-i',raw,'-af',
        'highpass=f=75,equalizer=f=250:t=q:w=0.8:g=-1.5,equalizer=f=3000:t=q:w=0.8:g=1,acompressor=threshold=0.125:ratio=2:attack=15:release=180:makeup=1.2',
        '-ar','24000','-ac','1','-c:a','pcm_s16le',dst)
    with wave.open(str(dst),'rb') as f:
        duration=f.getnframes()/f.getframerate(); frames=f.readframes(f.getnframes())
    if duration<=0 or not any(frames): raise RuntimeError('Audio kosong')
    if words and any(not (0<=w['start']<w['end']<=duration+.1) for w in words): words=[]
    (folder/f'{number}.json').write_text(json.dumps({'line':line,'words':words},ensure_ascii=False))
    print(f'  {number}/8: {duration:.2f}s, {"cap masa perkataan" if words else "anggaran"}',flush=True)

async def edge(folder):
    import edge_tts
    ca=os.getenv('SSL_CERT_FILE') or os.getenv('REQUESTS_CA_BUNDLE')
    if ca:
        import ssl, edge_tts.communicate
        edge_tts.communicate._SSL_CTX=ssl.create_default_context(cafile=ca)
    for i,line in enumerate(LINES,1):
        mp3=folder/f'{i}.mp3'; raw=folder/f'{i}.raw.wav'; boundaries=[]
        speak=edge_tts.Communicate(line,voice=VOICE,rate=os.getenv('VOICE_RATE','-8%'),pitch=os.getenv('VOICE_PITCH','-3Hz'),volume=os.getenv('VOICE_VOLUME','+0%'),boundary='WordBoundary',proxy=os.getenv('HTTPS_PROXY') or os.getenv('https_proxy'),connect_timeout=15,receive_timeout=45)
        with mp3.open('wb') as f:
            async for item in speak.stream():
                if item['type']=='audio': f.write(item['data'])
                elif item['type']=='WordBoundary': boundaries.append({'text':item['text'],'start':item['offset']/1e7,'end':(item['offset']+item['duration'])/1e7})
        run('ffmpeg','-v','error','-y','-i',mp3,'-ar','24000','-ac','1',raw)
        output(folder,i,raw,line,pauses(raw,align(line,boundaries)))
        mp3.unlink(); raw.unlink()

def mms(folder):
    import numpy as np, torch
    from scipy.io.wavfile import write
    from transformers import AutoTokenizer, VitsModel, set_seed
    model_id='facebook/mms-tts-zlm'
    torch.set_num_threads(min(4,os.cpu_count() or 1))
    # Prefer a fully cached model. A first run downloads from Hugging Face.
    try:
        tokenizer=AutoTokenizer.from_pretrained(model_id,trust_remote_code=False,local_files_only=True)
        model=VitsModel.from_pretrained(model_id,trust_remote_code=False,local_files_only=True)
    except OSError:
        import urllib.request, ssl
        ca=os.getenv('SSL_CERT_FILE') or os.getenv('REQUESTS_CA_BUNDLE')
        request=urllib.request.Request(f'https://huggingface.co/{model_id}/resolve/main/config.json',method='HEAD')
        with urllib.request.urlopen(request,timeout=20,context=ssl.create_default_context(cafile=ca)): pass
        tokenizer=AutoTokenizer.from_pretrained(model_id,trust_remote_code=False)
        model=VitsModel.from_pretrained(model_id,trust_remote_code=False)
    model=model.eval()
    model.speaking_rate=.92
    for i,line in enumerate(LINES,1):
        audio=[]
        for j,part in enumerate(re.findall(r'.+?(?:\.{3}|[,.!?]|$)',line)):
            if not part.strip(): continue
            set_seed(1000+i*100+j)
            with torch.inference_mode(): samples=model(**tokenizer(part,return_tensors='pt')).waveform[0].numpy()
            audio.extend([samples,np.zeros(round(model.config.sampling_rate*(.32 if part.endswith('...') else .12)),dtype=np.float32)])
        raw=folder/f'{i}.raw.wav'; write(raw,model.config.sampling_rate,np.concatenate(audio)); output(folder,i,raw,line,[]); raw.unlink()

def say(folder):
    if not shutil.which('say'): raise RuntimeError('macOS say tidak tersedia')
    for i,line in enumerate(LINES,1):
        raw=folder/f'{i}.aiff';run('say','-v','Amira','-r','165','-o',raw,line);output(folder,i,raw,line,[]);raw.unlink()

def main():
    requested=os.getenv('VOICE_ENGINE','auto')
    chains={'auto':['edge','mms','say'],'edge':['edge','mms','say'],'mms':['mms','say'],'say':['say'],'none':[]}
    if requested not in chains: raise ValueError('VOICE_ENGINE mesti auto, edge, mms, say atau none')
    DEST.mkdir(parents=True,exist_ok=True)
    selected='none'
    with tempfile.TemporaryDirectory(prefix='voice-',dir=DEST.parent) as tmp:
        folder=Path(tmp)
        for engine in chains[requested]:
            print(f'Mencuba enjin {engine}...',flush=True)
            try:
                if engine=='edge': asyncio.run(asyncio.wait_for(edge(folder),timeout=120))
                elif engine=='mms': mms(folder)
                else: say(folder)
                if not all((folder/f'{i}.wav').is_file() for i in range(1,9)): raise RuntimeError('Baris tidak lengkap')
                selected=engine;break
            except Exception as e:
                print(f'{engine} gagal: {type(e).__name__}: {e}',file=sys.stderr,flush=True)
                for p in folder.iterdir(): p.unlink()
        for i in range(1,9):
            for ext in ['wav','json']:
                dest=DEST/f'{i}.{ext}'
                if selected=='none': dest.unlink(missing_ok=True)
                else: os.replace(folder/dest.name,dest)
    print(f'Suara digunakan: {selected}' + (f' / {VOICE}' if selected=='edge' else ' / Amira' if selected=='say' else ' / facebook/mms-tts-zlm' if selected=='mms' else ''),flush=True)
    if selected=='none' and os.getenv('VOICE_REQUIRED')=='1': raise SystemExit('Tiada enjin suara berjaya')

if __name__=='__main__': main()
