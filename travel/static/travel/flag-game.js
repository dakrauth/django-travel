;const playFlagGame = (function(root) {

    // http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
    const shuffle = array => {
        let currentIndex = array.length;

        // While there remain elements to shuffle...
        while(0 !== currentIndex) {

            // Pick a remaining element...
            const randomIndex = Math.floor(Math.random() * currentIndex--);

            // And swap it with the current element.
            const temp = array[currentIndex];
            array[currentIndex] = array[randomIndex];
            array[randomIndex] = temp;
        }

      return array;
    }

    const scoreCard = (() => {
        const score = [0, 0];
        return is_correct => {
            ++score[1];
            is_correct && ++score[0];
            return score.join(' / ');
        }
    })();

    const View = {
        upateScore(is_correct) {
            document.getElementById('game_score').textContent = scoreCard(is_correct);
        },
        toggleCorrect(is_correct) {
            let el = document.getElementById('item').parentElement;
            if(is_correct === undefined) {
                el.className = el.className.replace(/ ?(in)?correct/, '');
            }
            else {
                el.className += is_correct ? ' correct' : ' incorrect';
            }
        },
        updateImage(img, country, correct_id) {
            img.src = country.image;
            img.dataset.id = country.id;
            img.dataset.correct = correct_id;
        }
    };

    const randomInt = max => Math.floor(Math.random() * max);

    const groupCycler = (countries, groupIds) => {
        let currentIndex = 0;
        shuffle(groupIds);
        const next = () => {
            if(currentIndex >= groupIds.length) {
                currentIndex = 0;
            };
            return shuffle(groupIds[currentIndex++]);
        };
        return () => {
            const group = next();
            const co_id = group[randomInt(group.length)];
            const correct = countries[co_id];
            const imgs = item.querySelectorAll('#item img');
            for(const [i, id] of group.entries()) {
                View.updateImage(imgs[i], countries[id], correct.id)
            }

            document.getElementById('co-name').textContent = correct.name;
            View.toggleCorrect();
        }
    };

    return (countries, groupIds) => {
        const cycler = groupCycler(countries, groupIds);
        for(const el of document.querySelectorAll('#item img')) {
            el.addEventListener('click', () => {
                const is_correct = (el.dataset.correct == el.dataset.id);
                View.toggleCorrect(is_correct);
                View.upateScore(is_correct);
                setTimeout(() => cycler(), 1000);
            });
        }

        document.getElementById('next_button').addEventListener('click', () => {
            View.upateScore(false);
            cycler();
        });

        cycler();
    };
}(window));
