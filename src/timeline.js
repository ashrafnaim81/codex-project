import fs from 'node:fs';import {execFileSync} from 'node:child_process';
export const narration=JSON.parse(fs.readFileSync(new URL('./narration.json',import.meta.url)));
export function buildTimeline(dir='out/voice'){let start=0;return narration.map((line,i)=>{const file=`${dir}/${i+1}.wav`;const voiced=fs.existsSync(file);const audio=voiced?Number(execFileSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',file],{encoding:'utf8'})):0;const duration=voiced?audio+1.2:Math.max(5,line.split(/\s+/).length/2.05+.8);const scene={index:i,line,start,duration,audio,file:voiced?file:null};start+=duration;return scene;});}
export function at(t,timeline){return timeline.find(s=>t<s.start+s.duration)||timeline.at(-1);}
