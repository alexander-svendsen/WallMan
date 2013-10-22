var tasksURI =  "http://" + $(location).attr('host');
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
    return ajax(tasksURI + '/move', 'POST', {"name" : username, "direction" : "right"});
};
var left = function(username){
    return ajax(tasksURI + '/move', 'POST', {"name" : username, "direction" : "left"});
};
var up = function(username){
    return ajax(tasksURI + '/move', 'POST', {"name" : username, "direction" : "up"});
};
var down = function(username){
    return ajax(tasksURI + '/move', 'POST', {"name" : username, "direction" : "down"});
};