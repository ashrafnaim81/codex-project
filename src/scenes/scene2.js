import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
export default function(c,t,p,m){box(c,90,420,900,850,'#e4c493');text(c,'IMBAS KEMBALI · KEDAI ROTI',540,500,37);box(c,160,930-p*90,760,270+p*90,'#f4deb0',100);yisa(c,{x:510,y:780-p*70,t,mouth:m});text(c,'YISA',510,1020,42);text(c,'Gas membuat doh mengembang',540,1210,32);for(let i=0;i<5;i++)spark(c,210+i*150,590+Math.sin(t+i)*30,t);}
