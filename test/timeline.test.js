const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{execFileSync}=require('node:child_process');
test('durasi WAV dan cap masa dipakai hanya untuk teks yang sepadan',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'terra-timeline-')),cwd=process.cwd(),modulePath=path.join(cwd,'src/timeline.js'),lines=require('../src/lines.json');
 try{
  fs.mkdirSync(path.join(dir,'out/voice'),{recursive:true});
  execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=2','-ar','24000',path.join(dir,'out/voice/1.wav')]);
  const words=lines[0].split(' ').map((text,index)=>({index,text,start:index*.25,end:index*.25+.2}));
  fs.writeFileSync(path.join(dir,'out/voice/1.json'),JSON.stringify({line:lines[0],words}));
  process.chdir(dir);delete require.cache[require.resolve(modulePath)];let timeline=require(modulePath);
  assert.equal(timeline[0].audio,2);assert.equal(timeline[0].duration,3);assert.equal(timeline[1].start,3);assert.equal(timeline[0].words.length,words.length);
  fs.writeFileSync(path.join(dir,'out/voice/1.json'),JSON.stringify({line:'Teks berbeza',words}));delete require.cache[require.resolve(modulePath)];timeline=require(modulePath);assert.deepEqual(timeline[0].words,[]);
 }finally{process.chdir(cwd);fs.rmSync(dir,{recursive:true,force:true})}
});
