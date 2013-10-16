
$(document).ready(function(){
    function PlayerScore(rank, name, score){
        var self = this;
        self.rank = rank;
        self.orignalName = name
        if (name.length > 10){
            self.name = name.slice(0,7) + "..."
        }
        else{
           self.name = name;
        }
        self.score = score;
        if (name == username){
            self.me = true;
        }
        else{
            self.me = false;
        }
    }

    function AppViewModel() {
        var self = this;
        self.seconds = ko.observable(0);  // seconds since last update
        self.index = 0;
        self.timeLeft = ko.observable('\u221e');

        self.scoreArrayMaxLength = 5;
        // Score dict - would come from the server

        self.scoreArray = ko.observableArray([PlayerScore("?", username, "?")]);
        self.fullScoreArray = new Array();
        self.addScore = function(rank, name, score) {
            if (name == username)
                self.index = self.fullScoreArray.length;
            self.fullScoreArray.push(new PlayerScore(rank, name, score));
        };
        self.addShowAbleScore = function(rank, name, score){
            self.scoreArray.push(new PlayerScore(rank, name, score));
        };
        self.sliceScoreArray = function(){
            var start = self.index - 2;
            var end = self.index + 3;
            if (start < 0){
                start = 0;
                end = 5;
            }
            if(end > self.fullScoreArray.length){
                end = self.fullScoreArray.length;
                start = end - 5;
                if (start < 0)
                    start = 0;

            }
            for (var i = start; i < end; i++) {
                self.addShowAbleScore(self.fullScoreArray[i].rank,
                                      self.fullScoreArray[i].orignalName,
                                      self.fullScoreArray[i].score);
            }

        };

        self.clearScore = function() {
            self.scoreArray.removeAll();
            self.fullScoreArray = new Array();
        };

    }

    window.vm = new AppViewModel();
    // Activates knockout.js
    ko.applyBindings(vm);

    // Hack to allow to update a value periodically
    var sec = 0;
    var countdown = 0;
    var timerID
    setInterval( function(){
        window.vm.seconds(++sec%60);
    } , 1000);

    var sortFunction = function(a, b){
        return b[1] - a[1]
    };

    //Ajax call to update the score
    setInterval( function(){

        $.getJSON(tasksURI + '/status', function(json){
            var array = Array();
            if (Object.keys(json["score"]).length <= 0)
                return;

            window.vm.clearScore();
            for (var key in json["score"]) {
                array.push([key, json["score"][key]])
            }
            array.sort(sortFunction);
            for (var i = 0; i < array.length; i++) {
                window.vm.addScore(i +1, array[i][0], array[i][1]);
            }
            window.vm.sliceScoreArray();
            sec = 0;
            if (json["time_left"]){
                countdown = json["time_left"];
                if (countdown <= 0){
                    window.vm.timeLeft = 0;
                    if (timerID)
                        clearInterval(timerID);
                    return;
                }
                window.vm.timeLeft(countdown + 's');
                if (json["started"] == true)
                    startCountDown()
            }
        });
    }, 5000);

    var startCountDown = function(){
        if (timerID)
            clearInterval(timerID);
        timerID = setInterval( function(){
            if (countdown <= 0)
                clearInterval(timerID);
            else
                window.vm.timeLeft(--countdown + 's');
        }, 1000);
    };


});
