const randomInt = max => Math.floor(Math.random() * max);

const shuffle = array => {
    // http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
    let currentIndex = array.length;

    // While there remain elements to shuffle, pick one randomly and swap
    while(0 !== currentIndex) {
        const randomIndex = Math.floor(Math.random() * currentIndex--);
        const temp = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temp;
    }

  return array;
}

class ScoreCard {
    constructor() {
        this.correct = 0;
        this.total = 0;
    }
    update(isCorrect) {
        ++this.total;
        isCorrect && ++this.correct;
        return this;
    }
    toString() {
        return `${this.correct} / ${this.total}`;
    }
}

class View {
    constructor() {
        this.item = document.getElementById('item');
        this.images = [...this.item.querySelectorAll('img')];
        this.nextBtn = document.getElementById('next-button')
    }
    updateScore(score) {
        document.getElementById('game-score').textContent = score;
    }
    toggleCorrect(isCorrect) {
        let el = this.item.parentElement;
        if(isCorrect === undefined) {
            el.className = el.className.replace(/ ?(in)?correct/, '');
        }
        else {
            el.className += isCorrect ? ' correct' : ' incorrect';
        }
    }
    updateImage(index, country) {
        const img = this.images[index]
        img.src = country.image;
        img.dataset.code = country.code;
    }
}

const loadData = async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    return data;
};

class FlagData {
    constructor(data) {
        this.countries = data.countries.reduce((accum, value) => {
            accum[value.code] = value;
            return accum;
        }, {});
        this.groups = data.groups;
    }
}

class Controller {
    constructor(flags, view) {
        this.currentIndex = 0;
        this.flags = flags;
        this.view = view;
        this.scoreCard = new ScoreCard();
        shuffle(this.flags.groups);
    }
    next() {
        if(this.currentIndex >= this.flags.groups.length) {
            this.currentIndex = 0;
        };
        return shuffle(this.flags.groups[this.currentIndex++]);
    }
    cycle() {
        const group = this.next();
        this.currentCorrect = this.flags.countries[group[randomInt(group.length)]];
        for(const [i, id] of group.entries()) {
            this.view.updateImage(i, this.flags.countries[id])
        }

        document.getElementById('co-name').textContent = this.currentCorrect.name;
        this.view.toggleCorrect();
    }
    play() {
        for(const el of this.view.images) {
            el.addEventListener('click', () => {
                const isCorrect = (el.dataset.code === this.currentCorrect.code);
                this.view.toggleCorrect(isCorrect);
                this.view.updateScore(this.scoreCard.update(isCorrect));
                setTimeout(() => this.cycle(), 1000);
            });
        }

        this.view.nextBtn.addEventListener('click', () => {
            this.view.updateScore(this.scoreCard.update(false));
            this.cycle();
        });

        this.cycle();
    }
};

export const playFlagGame = async (url) => {
    let data = await loadData(url);
    const controller = new Controller(new FlagData(data), new View());
    controller.play()
};
