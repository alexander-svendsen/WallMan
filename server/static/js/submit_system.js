$("#playerProp").on("submit", function(e) {
    e.preventDefault();
//    var button = $('#joinButton');
//
    var inputField = $('#appendedInputButton');
    var input = inputField.val();

    var terminal = $('#console');
    terminal.first().contents().first().remove();
    while(terminal.first().contents().first()[0].nodeName == "#text"){
        terminal.first().contents().first().remove();
    }
    if (input.length == 0){
//        button.toggleClass('btn-primary', false);
//        button.toggleClass('btn-danger', true);
//        $('#errorContainer').toggleClass('error', true);
//        var input = $('#appendedInputButton');
//        input.attr("placeholder", "Must have one");
//        input.css('border-color', '#b94a48');
        terminal.append('<p class="error">Error: Must have a username</p>');
        return;
    }
    terminal.append('<p>'+ input + '</p>');
//    button.prop('disabled', true);
    inputField.prop('disabled', true);

//    button.toggleClass('btn-primary', true);
//    button.toggleClass('btn-danger', false);
//    $('#errorContainer').toggleClass('error', false);
    ajax(tasksURI + '/join', 'POST', {"name" : input}).success(redirect(input));
});

var redirect = function(username){
    $.cookie("username", username);
    $.cookie("refresh", true);
    window.location.replace("/static/control.html");
};