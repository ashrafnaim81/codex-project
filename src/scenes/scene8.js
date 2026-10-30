import {box,text,wrap,ease,particles,spark} from '../draw.js';
import roti from '../characters/roti.js';import yisa from '../characters/yisa.js';import rizo from '../characters/rizo.js';
export default function(c,t,p,m){particles(c,t,35);roti(c,{y:740,t,mouth:m,glasses:p<.23});if(p>.23&&p<.5){c.save();c.translate(700+(p-.23)*500,800+(p-.23)*800);c.rotate(p*8);box(c,-45,-20,90,40,'#292238',8);c.restore();}wrap(c,'Mikroorganisma: kecil tetapi pengaruhnya besar!',540,1050,800,52,'#492639');text(c,'Sains Tahun 6 · Unit 3',540,1240,34);}
