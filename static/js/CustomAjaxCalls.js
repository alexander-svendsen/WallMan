var tasksURI = 'http://129.242.22.192:8080/';
var ajax = function(uri, method, data) {
    var request = {
        url: uri,
        type: method,
        contentType: "application/json",
        accepts: "application/json",
        cache: false,
        dataType: 'json',
        data: JSON.stringify(data)
    };
    return $.ajax(request);
};

var right = function(username){
    ajax(tasksURI + 'move', 'POST', {"name" : username, "direction" : "right"});
};
var left = function(username){
    ajax(tasksURI + 'move', 'POST', {"name" : username, "direction" : "left"});
};
var up = function(username){
    ajax(tasksURI + 'move', 'POST', {"name" : username, "direction" : "up"});
};
var down = function(username){
    ajax(tasksURI + 'move', 'POST', {"name" : username, "direction" : "down"});
};