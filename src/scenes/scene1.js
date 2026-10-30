import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
export default function(c,t,p,m){box(c,95,420,890,850,'#453546');box(c,150,500,260,300,'#c88a4b');roti(c,{x:280,y:650,t,scale:.65});text(c,'SEBELUM',280,850,34,'#fff2c9');roti(c,{x:680,y:900,t,mouth:m,mould:1,glasses:true});text(c,'Sekarang…',680,1160,40,'#fff2c9');c.fillStyle='rgba(255,230,140,.09)';c.beginPath();c.moveTo(540,400);c.lineTo(200,1250);c.lineTo(950,1250);c.fill();}
