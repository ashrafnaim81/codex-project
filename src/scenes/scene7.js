import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
import {icon} from '../icons.js';
export default function(c,t,p,m){box(c,100,430,435,820,'#d3e5bd');box(c,545,430,435,820,'#f0bbb6');text(c,'KEBAIKAN',318,495,39);text(c,'KEBURUKAN',763,495,39);const good=['Roti','Tapai','Keju','Tempe','Penisilin','Baja organik','Rawatan kumbahan'],bad=['Makanan rosak','Gigi reput','Keracunan makanan','Tanaman rosak','Selesema','Beguk','Campak','Kurap'];good.forEach((s,i)=>{if(p>(i+1)*.045){icon(c,145,565+i*85,i,false);text(c,s,340,576+i*85,27);}});bad.forEach((s,i)=>{if(p>.36+(i+1)*.062){icon(c,585,555+i*80,i,true);text(c,s,790,566+i*80,24);}});}
