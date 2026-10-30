import {eyes,spark} from '../draw.js';
export default function virus(c,{x=540,y=700,t=0,mouth=0,emotion='neutral',scale=1}={}){c.save();c.translate(x,y);c.scale(scale,scale);c.strokeStyle='#301d2d';c.lineWidth=8;
 const kind='virus'; if(kind==='virus'||kind==='protozoa')for(let i=0;i<22;i++){let a=i*Math.PI/11;c.beginPath();c.moveTo(Math.cos(a)*100,Math.sin(a)*90);c.lineTo(Math.cos(a)*130,Math.sin(a)*120);c.stroke();}
 c.fillStyle='#b59add';c.beginPath();c.ellipse(0,0,kind==='protozoa'?135:105,kind==='protozoa'?80:105,0,0,7);c.fill();c.stroke();eyes(c,t,mouth,false,emotion);
 if(kind==='alga'){spark(c,110,-110,t);}if(kind==='bacteria'){c.beginPath();c.arc(-140,90,20,0,7);c.fill();c.beginPath();c.roundRect(120,50,25,85,12);c.fill();c.beginPath();for(let i=0;i<40;i++){let x=-145+i*7,y=155+Math.sin(i*.4)*15;i?c.lineTo(x,y):c.moveTo(x,y);}c.stroke();}c.restore();}
