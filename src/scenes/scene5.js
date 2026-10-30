import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
export default function(c,t,p,m){text(c,`HARI ${p<.3?'1':p<.68?'5':'7'}`,540,520,85);roti(c,{y:850,t,mouth:m,mould:p});text(c,'Mikroorganisma bertumbuh!',540,1190,40);for(let i=0;i<8;i++)spark(c,200+i*95,600+Math.sin(i*3)*70,t);}
