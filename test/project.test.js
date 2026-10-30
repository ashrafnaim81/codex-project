import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {buildTimeline,at,narration} from '../src/timeline.js';import {effect,wav,RATE} from '../src/sfx.js';
test('lapan babak berterusan dan durasi mengambil WAV sebenar',()=>{const dir=fs.mkdtempSync(path.join(os.tmpdir(),'mikro-'));try{wav(path.join(dir,'1.wav'),new Float32Array(RATE*2));const t=buildTimeline(dir);assert.equal(t.length,8);assert.equal(t[0].duration,3.2);assert.equal(t[0].audio,2);for(let i=1;i<8;i++)assert.equal(t[i].start,t[i-1].start+t[i-1].duration);assert.equal(at(3.3,t).index,1);assert.equal(narration[0],'Hai. Ini gambar saya... sebelum.');}finally{fs.rmSync(dir,{recursive:true});}});
test('semua kesan bunyi terhingga dan deterministik',()=>{for(const name of ['whoosh','pop','ding','zip','slam','hiss','tick','chime','buzz','scratch','sting','hum']){const a=effect(name,.1);assert.equal(a.length,2400);assert.ok(a.every(Number.isFinite));assert.ok(a.some(v=>v!==0));assert.deepEqual(a,effect(name,.1));}});

test('sari kata menggunakan cap masa sebenar dan tiada serlahan ketika jeda', async()=>{
  const {subtitleState,readWordTimings}=await import('../src/timeline.js');
  const scene={line:'Hai. Sebelum.',audio:3,duration:4.2,words:[
    {index:0,text:'Hai.',start:.2,end:.5}, {index:1,text:'Sebelum.',start:2,end:2.7}]};
  assert.deepEqual(subtitleState(scene,.3),{active:0,focus:0});
  assert.deepEqual(subtitleState(scene,1.5),{active:-1,focus:0});
  assert.deepEqual(subtitleState(scene,2.1),{active:1,focus:1});
  assert.equal(subtitleState({...scene,words:[]},1.6).active,1);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'subtitle-'));const file=path.join(dir,'1.json');
  try{
    fs.writeFileSync(file,JSON.stringify({...scene,timing:'word-boundary'}));
    assert.equal(readWordTimings(file,scene.line,3).length,2);
    assert.deepEqual(readWordTimings(file,'Teks berubah.',3),[]);
    scene.words[1].start=-2;
    fs.writeFileSync(file,JSON.stringify({...scene,timing:'word-boundary'}));
    assert.deepEqual(readWordTimings(file,scene.line,3),[]);
  }finally{fs.rmSync(dir,{recursive:true});}
});

test('campuran dinormalkan kepada -14 LUFS tanpa mengubah tempoh', async()=>{
  const {normalizeMix,analyze}=await import('../src/audio.js');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'loudness-'));
  try{
    const input=path.join(dir,'raw.wav'),output=path.join(dir,'master.wav');
    const signal=Float32Array.from({length:RATE*4},(_,i)=>Math.sin(2*Math.PI*230*i/RATE)*.06);
    wav(input,signal);
    normalizeMix(input,output,path.join(dir,'report.json'));
    const stats=analyze(output);
    assert.ok(Math.abs(Number(stats.input_i)+14)<.5,stats.input_i);
    assert.ok(Number(stats.input_tp)<-1,stats.input_tp);
    const {execFileSync}=await import('node:child_process');
    const seconds=Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',output],{encoding:'utf8'}));
    assert.ok(Math.abs(seconds-4)<.02);
  }finally{fs.rmSync(dir,{recursive:true});}
});
