const fs=require('fs'),{execFileSync}=require('child_process'),lines=require('./lines.json');
let start=0;
module.exports=lines.map((line,i)=>{
  const file=`out/voice/${i+1}.wav`,voiced=fs.existsSync(file);
  const audio=voiced?Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',file],{encoding:'utf8'})):0;
  if(voiced&&(!Number.isFinite(audio)||audio<=0))throw Error(`Audio tidak sah: ${file}`);
  const duration=audio?audio+1:Math.max(6,line.split(' ').length/2);
  let words=[];
  try{const m=JSON.parse(fs.readFileSync(`out/voice/${i+1}.json`,'utf8')),tokens=line.split(' ');if(m.line===line&&m.words.length===tokens.length&&m.words.every((w,j)=>w.index===j&&w.text===tokens[j]&&Number.isFinite(w.start)&&Number.isFinite(w.end)&&w.start>=0&&w.end>w.start&&w.end<=audio+.1&&(j===0||w.start>=m.words[j-1].start)))words=m.words}catch{}
  const scene={line,start,duration,audio,file:audio?file:null,words};start+=duration;return scene;
});
