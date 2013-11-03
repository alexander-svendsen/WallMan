$("#playerProp").on("submit", function(e) {
    e.preventDefault();
    var inputField = $('#appendedInputButton');
    var input = inputField.val();

    var terminal = $('.console');
    terminal.first().contents().first().remove();
    while(terminal.first().contents().first()[0].nodeName == "#text"){
        terminal.first().contents().first().remove();
    }
    if (input.length == 0){
        terminal.append('<p class="error">Error: Must have a username</p>');
        return;
    }
    terminal.append('<p>'+ input + '</p>');
    ajax(tasksURI + '/join', 'POST', {"name" : input}).success(redirect(input));
});

var redirect = function(username){
    $.cookie("username", username);
    $.cookie("refresh", true);
    window.location.href = "/static/control.html";
};