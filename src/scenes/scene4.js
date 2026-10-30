import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
export default function(c,t,p,m){rizo(c,{x:300+160*ease(p*5),y:650,t,mouth:m});text(c,'RIZO · SPORA KULAT',540,455,40);const a=['Air','Suhu sesuai','Udara','Nutrien','Keasidan sesuai'];a.forEach((s,i)=>{let on=p>(i+1)/7;box(c,210,830+i*73,660,63,on?'#d2e2a0':'#f0ddcb',15);text(c,s,470,875+i*73,35);if(on)text(c,'✓',800,875+i*73,40,'#32674a');});}
