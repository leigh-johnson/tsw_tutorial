/************************************* 
Code is based on the walkthough here: http://thecodeplayer.com/walkthrough/matrix-rain-animation-html5-canvas-javascript 
**************************************/
var cnvs = document.getElementById('code-canvas');
var cntxt = cnvs.getContext('2d');


var chars = 'ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑ하악안알암압앙앞애액앵야얀약양얘어억언얼엄업엉에여역연열염엽영예잎잉으을움워월위'; // om
chars = chars.split(''); // make array
var font_size = 14;

// see: http://blog.codepen.io/2013/07/29/full-screen-canvas/
function resizeCanvas() {
  cnvs.width = window.innerWidth;
  setTimeout(function() {
    cnvs.height = window.innerHeight;
  }, 0);
};
window.onresize = resizeCanvas();
resizeCanvas();


var columns = cnvs.width/font_size;
var drops = [];
for(var x=0;x<columns;x++){
  drops[x]=1;
}

function draw(){
  
  cntxt.fillStyle = 'rgba(0,0,0,0.05)';
  cntxt.fillRect(0,0,cnvs.width,cnvs.height);
  cntxt.fillStyle = '#0F0';
  cntxt.font = font_size + 'px helvetica';
  
  for(var i=0;i<drops.length;i++){
    var txt = chars[Math.floor(Math.random()*chars.length)];
    cntxt.fillText(txt,i*font_size, drops[i]*font_size);
    
    if(drops[i]*font_size>cnvs.height&&Math.random()>0.975){
      drops[i] = 0; // back to the top!   
    }
    drops[i]++;
  }
}

setInterval(draw, 32);