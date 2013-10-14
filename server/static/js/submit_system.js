$("#playerProp").on("submit", function(e) {
    e.preventDefault();
    var button = $('#joinButton');

    var inputField = $('#appendedInputButton');
    var username = inputField.val();

    if (username.length == 0){
        button.toggleClass('btn-primary', false);
        button.toggleClass('btn-danger', true);
        $('#errorContainer').toggleClass('error', true);
        var input = $('#appendedInputButton');
        input.attr("placeholder", "Must have one");
        input.css('border-color', '#b94a48');
        return;
    }

    button.prop('disabled', true);
    inputField.prop('disabled', true);

    button.toggleClass('btn-primary', true);
    button.toggleClass('btn-danger', false);
    $('#errorContainer').toggleClass('error', false);
    ajax(tasksURI + '/join', 'POST', {"name" : username}).success(redirect(username));
});

var redirect = function(username){
    $.cookie("username", username);
    $.cookie("refresh", true);
    window.location.replace("/static/control.html");
};