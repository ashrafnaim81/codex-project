exports.text=(c,s,x,y,size=42,color='#372536')=>{c.fillStyle=color;c.font=`bold ${size}px sans-serif`;c.textAlign='center';c.fillText(s,x,y)};
exports.rect=(c,x,y,w,h,color,r=20)=>{c.fillStyle=color;c.strokeStyle='#372536';c.lineWidth=7;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();c.stroke()};
exports.spark=(c,x,y,t)=>{c.save();c.translate(x,y);c.rotate(t);c.strokeStyle='#fff1ae';c.lineWidth=6;c.beginPath();c.moveTo(-15,0);c.lineTo(15,0);c.moveTo(0,-15);c.lineTo(0,15);c.stroke();c.restore()};
exports.bg=(c,color)=>{c.fillStyle=color;c.fillRect(75,410,930,900)};
