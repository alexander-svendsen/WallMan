$(document).keydown(function(e){
    if (e.keyCode == 37) {
        if (prevDirection != "left"){
            left(username);
            prevDirection = "left"
        }
        return false;
    }
    else if (e.keyCode == 38) {
        if (prevDirection != "up"){
            up(username);
            prevDirection = "up"
        }
        return false;
    }
    else if (e.keyCode == 39) {
        if (prevDirection != "right"){
            right(username);
            prevDirection = "right"
        }
        return false;
    }
    else if (e.keyCode == 40) {
        if (prevDirection != "down"){
            down(username);
            prevDirection = "down"
        }
        return false;
    }
});

var canvas,
    c, // c is the canvas' context 2D
    container,
    touchID = -1,
    radius = 40,
    touchPos = new Vector2(0,0),
    touchStartPos = new Vector2(0,0),
    vector = new Vector2(0,0);

var mouseX, mouseY,
// is this running in a touch capable environment?
    touchable = 'createTouch' in document,
    touches = []; // array of touch vectors



function resetCanvas (e) {
    // resize the canvas - but remember - this clears the canvas too.
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.radius = (canvas.width + canvas.height)/100;
    //make sure we scroll to the top left.
    window.scrollTo(0,0);
}


function setupController(){
    setInterval(draw, 1000/35);
    setupCanvas();

    if(touchable) {
        canvas.addEventListener( 'touchstart', onTouchStart, false );
        canvas.addEventListener( 'touchmove', onTouchMove, false );
        canvas.addEventListener( 'touchend', onTouchEnd, false );
        window.onorientationchange = resetCanvas;
        window.onresize = resetCanvas;
    } else {

        canvas.addEventListener( 'mousemove', onMouseMove, false );
        canvas.addEventListener( 'mousedown', onMouseStart, false );
        canvas.addEventListener( 'mouseup', onMouseEnd, false );
        window.onorientationchange = resetCanvas;
        window.onresize = resetCanvas;
    }
}
function draw() {
    c.clearRect(0,0,canvas.width, canvas.height);
    if(touchable) {
        for(var i=0; i<touches.length; i++)
        {
            var touch = touches[i];
            if (touch.identifier == touchID){
                //TESTING PURPOSES
                c.beginPath();
                c.fillStyle = "white";
                c.fillText("touch id : "+touch.identifier+" x:"+touch.clientX+" y:"+touch.clientY, touch.clientX+30, touch.clientY-30);
                //--------------

                c.beginPath();
                c.strokeStyle = "cyan";
                c.lineWidth = 6;
                c.arc(touchStartPos.x, touchStartPos.y, radius,0,Math.PI*2,true);
                c.stroke();
                c.beginPath();
                c.strokeStyle = "cyan";
                c.lineWidth = 2;
                c.arc(touchStartPos.x, touchStartPos.y, 60,0,Math.PI*2,true);
                c.stroke();
                c.beginPath();
                c.strokeStyle = "cyan";
                c.arc(touchPos.x, touchPos.y, radius, 0,Math.PI*2, true);
                c.stroke();
            }
        }
    }
    else {

        //TESTING PURPOSES
        c.fillStyle	 = "white";
        c.fillText("mouse : "+mouseX+", "+mouseY, mouseX, mouseY);
        //----------------

        if (touchID > 0){
            c.beginPath();
            c.strokeStyle = "cyan";
            c.lineWidth = 6;
            c.arc(touchStartPos.x, touchStartPos.y, 40,0,Math.PI*2,true);
            c.stroke();
            c.beginPath();
            c.strokeStyle = "cyan";
            c.lineWidth = 2;
            c.arc(touchStartPos.x, touchStartPos.y, 60,0,Math.PI*2,true);
            c.stroke();
            c.beginPath();
            c.strokeStyle = "cyan";
            c.arc(touchPos.x, touchPos.y, 40, 0,Math.PI*2, true);
            c.stroke();
        }

    }

}

function onTouchStart(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID<0){
            touchID = touch.identifier;
            touchStartPos.reset(touch.clientX, touch.clientY);
            touchPos.copyFrom(touchStartPos);
            vector.reset(0,0);
        }
    }
    touches = e.touches;

}

function onTouchMove(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)

    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID == touch.identifier){
            touchPos.reset(touch.clientX, touch.clientY);
            vector.copyFrom(touchPos);
            vector.minusEq(touchStartPos);
            break;
        }
    }
    touches = e.touches;
    getDirection()
}

function onTouchEnd(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    touches = e.touches;
    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID == touch.identifier){
            touchID = -1;
            vector.reset(0,0);
            break;
        }
    }
}

function onMouseMove(e) {
    mouseX = event.offsetX;
    mouseY = event.offsetY;
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    if(touchID == 1){
        touchPos.reset(event.offsetX, event.offsetY);
        vector.copyFrom(touchPos);
        vector.minusEq(touchStartPos);
    }
    getDirection()
}

function onMouseStart(e){
    if(touchID<0){
        touchID = 1;
        touchStartPos.reset(event.offsetX, event.offsetY);
        touchPos.copyFrom(touchStartPos);
        vector.reset(0,0);
    }
}

function onMouseEnd(e){
    if(touchID == 1){
        touchID = -1;
        vector.reset(0,0);
    }
}

function getDirection(){
    if (vector.magnitude() > radius){
        x =  (vector.x*vector.x);
        y =  (vector.y*vector.y);
        if (x > y){
            if (vector.x < 0){
                if (prevDirection != "left"){
                    left(username);
                    prevDirection = "left"
                }
            }
            else{
                if (prevDirection != "right"){
                    right(username);
                    prevDirection = "right"
                }
            }
        }
        else{
            if (vector.y < 0){
                if (prevDirection != "up"){
                    up(username);
                    prevDirection = "up"
                }
            }
            else{
                if (prevDirection != "down"){
                    down(username);
                    prevDirection = "down"
                }
            }
        }
    }

}
function setupCanvas() {

    canvas = document.createElement( 'canvas' );
    c = canvas.getContext( '2d' );
    container = document.createElement( 'div' );
    container.className = "drawcanvas";

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild( container );
    container.appendChild(canvas);

    c.strokeStyle = "#ffffff";
    c.lineWidth =2;
}
