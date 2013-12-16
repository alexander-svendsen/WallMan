/*!
 * virtual joystick
 *
 * Inspired by the solution found in:
 * http://seb.ly/2011/04/multi-touch-game-controller-in-javascripthtml5-for-ipad/
 * And some code is taken from the same guy at his github: https://github.com/sebleedelisle/JSTouchController/blob/master/TouchControl.html
 * The touch events and the drawing code is taken from it, the rest have I tweaked myself to make it
 * pc browser friendly and to be able to control your player
 */


//My own code
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

//my own code
var mylatesttap;
function doubletap() {

    var now = new Date().getTime();
    var timesince = now - mylatesttap;
    //Tweeked it. 200ms Seems like a good time for double click
    if((timesince < 200) && (timesince > 0)){
        ajax(tasksURI + '/doubletap', 'POST', {"name" : username});
    }
    mylatesttap = new Date().getTime();

}

//some their code, tweaked a little
var canvas,
    context,
    container,
    mouseX,
    mouseY,
    touchID = -1,
    radius = 40,
    color = "#FFDA50",
    currentPos = [0,0],
    startPos = [0,0],
    movementPos = [0,0],
    touchable = 'createTouch' in document,
    touches = [];


// my code again
function resetCanvas (e) {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.radius = (canvas.width + canvas.height)/100;
    window.scrollTo(0,0); //Makes us scroll to the top left
}


function setupController(){
    setInterval(draw, 1000/35);  // Draw interval
    setupCanvas();

    //The touch events are their code. the mouse events is my code, inspired by their code
    if(touchable) {
        canvas.addEventListener( 'touchstart', onTouchStart, false );
        canvas.addEventListener( 'touchmove', onTouchMove, false );
        canvas.addEventListener( 'touchend', onTouchEnd, false );
    } else {

        canvas.addEventListener( 'mousemove', onMouseMove, false );
        canvas.addEventListener( 'mousedown', onMouseStart, false );
        canvas.addEventListener( 'mouseup', onMouseEnd, false );
    }
    window.onorientationchange = resetCanvas;
    window.onresize = resetCanvas;
}


function draw() {
    //their code, tweaked
    context.clearRect(0,0,canvas.width, canvas.height);
    if(touchable) {
        for(var i=0; i<touches.length; i++)
        {
            var touch = touches[i];
            if (touch.identifier == touchID){
                context.beginPath();
                context.strokeStyle = color;
                context.lineWidth = 6;
                context.arc(startPos[0], startPos[1], radius,0,Math.PI*2,true);
                context.stroke();
                context.beginPath();
                context.strokeStyle = color;
                context.lineWidth = 2;
                context.arc(startPos[0], startPos[1], 60,0,Math.PI*2,true);
                context.stroke();
                context.beginPath();
                context.strokeStyle = color;
                context.arc(currentPos[0], currentPos[1], radius, 0,Math.PI*2, true);
                context.stroke();
            }
        }
    }
    else { // code we added to have the mouse click drawing, the same code as above
        if (touchID > 0){
            context.beginPath();
            context.strokeStyle = color;
            context.lineWidth = 6;
            context.arc(startPos[0], startPos[1], 40,0,Math.PI*2,true);
            context.stroke();
            context.beginPath();
            context.strokeStyle = color;
            context.lineWidth = 2;
            context.arc(startPos[0], startPos[1], 60,0,Math.PI*2,true);
            context.stroke();
            context.beginPath();
            context.strokeStyle = color;
            context.arc(currentPos[0], currentPos[1], 40, 0,Math.PI*2, true);
            context.stroke();
        }
    }
}

//Their code, tweaked
function onTouchStart(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    doubletap();
    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID<0){
            touchID = touch.identifier;
            startPos = [touch.clientX, touch.clientY];
            currentPos = startPos;
        }
    }
    touches = e.touches;

}


//Their code, tweaked
function onTouchMove(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)

    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID == touch.identifier){
            currentPos = [touch.clientX, touch.clientY];
            movementPos = [currentPos[0] - startPos[0], currentPos[1] - startPos[1]];
            getDirection();
            break; //since only need the one correct touch
        }
    }
    touches = e.touches;

}


//Their code, tweaked
function onTouchEnd(e) {
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    touches = e.touches;
    for(var i = 0; i<e.changedTouches.length; i++){
        var touch =e.changedTouches[i];
        if(touchID == touch.identifier){
            touchID = -1;
            break;
        }
    }
}

//The same as the touch event only for the mouse, inspired by their code
function onMouseStart(e){
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    doubletap();
    if(touchID<0){
        touchID = 1;
        startPos = [event.offsetX, event.offsetY];
        currentPos = startPos;
    }
}

//The same as the touch event only for the mouse, some their code tweaked
function onMouseMove(e) {
    mouseX = event.offsetX;
    mouseY = event.offsetY;
    e.preventDefault(); // Prevent the browser from doing its default thing (scroll, zoom)
    if(touchID == 1){
        currentPos =[event.offsetX, event.offsetY];
        movementPos = [currentPos[0] - startPos[0], currentPos[1] - startPos[1]];
        getDirection();
    }

}

//The same as the touch event only for the mouse, inspired by their code
function onMouseEnd(e){
    if(touchID == 1){
        touchID = -1;
    }
}

//My code to send the player movements
function getDirection(){
    var length =  Math.sqrt((movementPos[0]*movementPos[0])+(movementPos[1]*movementPos[1]));
    if (length > radius){
        var x = movementPos[0] * movementPos[0];
        var y = movementPos[1] * movementPos[1];  //To test which movement pos is the largest
        if (x > y){
            if (movementPos[0] < 0){
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
            if (movementPos[1] < 0){
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

//Their code, tweaked a little for our solution
function setupCanvas() {
    canvas = document.createElement( 'canvas' );
    context = canvas.getContext( '2d' );

    container = document.createElement( 'div' );
    container.className = "drawcanvas";

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild( container );
    container.appendChild(canvas);

    context.strokeStyle = "#000000";
    context.lineWidth = 2;
}

