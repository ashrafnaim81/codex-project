const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{execFileSync}=require('node:child_process');
const decode=require('../src/decode-voice');
test('decodes a 20-second voice line without Node pipe buffer overflow',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'terra-voice-'));
 try{
  const file=path.join(dir,'line.wav');
  execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=20','-ar','24000','-ac','1',file]);
  const samples=decode(file,20);
  assert.equal(samples.length,20*24000);
  assert.ok(samples.some(x=>Math.abs(x)>.01));
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
