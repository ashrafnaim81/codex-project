module.exports=(t)=>{let f=[261.6,329.6,392,349.2][Math.floor(t*2)%4];return Math.sin(2*Math.PI*f*t)*Math.exp(-(t%0.5)*8)*.035};
