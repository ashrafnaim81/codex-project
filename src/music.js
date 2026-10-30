import {RATE} from './sfx.js';
export function music(duration){const notes=[261.63,329.63,392,329.63,220,261.63,349.23,392];return Float32Array.from({length:Math.ceil(duration*RATE)},(_,i)=>{const t=i/RATE,beat=t%.5,f=notes[Math.floor(t/.5)%notes.length];const fade=Math.min(1,t/2,(duration-t)/2);return fade*(Math.sin(2*Math.PI*f*t)*Math.exp(-beat*9)*.045+Math.sin(2*Math.PI*f/2*t)*.018);});}
