;var playFlagGame = (function(root) {
    
    // http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
    var shuffle = function(array) {
        var currentIndex = array.length;
        var temp, randomIndex;

      // While there remain elements to shuffle...
      while (0 !== currentIndex) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        // And swap it with the current element.
        temp = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temp;
      }

      return array;
    }

    var cycleGroups = function(groupIds) {
        var currentIndex = 0;
        shuffle(groupIds);
        return function getNextGroup() {
            if(currentIndex >= groupIds.length) {
                currentIndex = 0;
            };
            return shuffle(groupIds[currentIndex++]);
        };

    };
    
    var scoreCard = function() {
        var score = [0, 0];
        return function updateResult(is_correct) {
            ++score[1];
            if(is_correct) {
                ++score[0];
            }
            return score.join(' / ');
        }
    };
    
    var upateScoreView = function(text) {
        document.getElementById('game_score').textContent = text;
    };

    var toggleCorrectView = function(is_correct) {
        var el = document.getElementById('item').parentElement;
        if(is_correct === undefined) {
            el.className = el.className.replace(/ ?(in)?correct/, '');
        }
        else {
            el.className += is_correct ? ' correct' : ' incorrect';    
        }
    };

    var groupViewer = function(countries, nextGroup) {

        var randomInt = function(max) {
          return Math.floor(Math.random() * max);
        };
        
        return function showNextGroup() {
            var group = nextGroup();
            var co_id = group[randomInt(group.length)];
            var correct = countries[co_id];
            var item = document.getElementById('item');
            var imgs = item.querySelectorAll('img');
            var par = item.parentElement;
            group.forEach(function(id, i) {
                var co = countries[id];
                var img = imgs[i];
                img.src = co.image;
                img.dataset.id = co.id;
                img.dataset.correct = correct.id;
            });
            
            document.getElementById('co-name').textContent = correct.name;
            toggleCorrectView();
        }
    };

    return function playGame(countries, groupIds) {
        var nextView = groupViewer(countries, cycleGroups(groupIds));
        var updateScore = scoreCard();
        [].forEach.call(document.querySelectorAll('#item img'), function(el) {
            el.addEventListener('click', function clickHandler() {
                var is_correct = (this.dataset.correct == this.dataset.id);
                toggleCorrectView(is_correct);
                upateScoreView(updateScore(is_correct));
                setTimeout(function() { nextView(); }, 1000);
            });
        });

        document.getElementById('next_button').addEventListener(
            'click',
            function nextButtonHandler() {
                upateScoreView(updateScore(false));
                nextView();
            }
        );

        nextView();
    };
}(this));
