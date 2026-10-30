const base=require('./characters');
function face(c,o,color,shape='oval'){c.save();c.translate(o.x||540,o.y||850);c.scale(o.scale||1,o.scale||1);base(c,0,0,color,o.t||0,o.mouth||0,shape);c.restore()}
function line(c,x,y,x2,y2,color='#342532',width=8){c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke()}
module.exports={face,line};
