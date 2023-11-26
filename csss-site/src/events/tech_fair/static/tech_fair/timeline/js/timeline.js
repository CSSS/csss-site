// if a string is broken into an array, each element that is itself an array should be colored
const FRONT_PAGE_MESSAGES = [
    "// welcome to Tech Fair!",
    "// located at SFU's Burnaby campus",
    "// computing science is cool!",
    "// computer science is cool!",
    "// thousands of students!",
    "// we might have cake",
    "// on top of a mountain",
    "// meet local vancouver companies!",
    "// build your professional image!",
    //"// reasons you should join tech fair:\n// 1. to make connections\n// 2. it's fun!",
    //["gameobject.GetComponent<", ["Brain", "#4a7a96"], ">().LevelUp();"],
    //"long i = *(long*) &f;\ni = 0x5f3759df - (i >> 1); \n// hmmm, maybe not...",
    "cout << \"n=\" << this->booths.size() << endl;",
    "goto tech_fair;",
    "let booth = new CompanyBooth(info);",
    //"for(booth in companyBooths) {\n\tSFU_CSSS.TechFair.create(booth);\n}",
    "Tech Fair received signal SIGSEV, \nSegmentation fault.",
    "// :)",
    //"// the coolest event on campus",
    "// static webpages rule!",
    "// be there or be rectangle",
    "adsflghja;dfhj;kldgsdaf\n:q!", //"adsflghja;dfhj;kldgsdaf\n~ \n:q!",
    "(write (car tech_fair_events))",
    "// run by the 【 SFU CSSS 】",
    "// ↑↑↓↓←→←→BA\n",
    //"// ∀ companies ∃ a perfect one",
    //"[1]+  Stopped\tvi tech_fair.cpp\ncsss@CR:~/tf/$ git add *\ncsss@CR:~/tf/$ git commit -m \"stuff\"",
    "// now with more colours!",
    "// bigger than a bread box!",
    "// Tech Fair: Where Ideas Ignite!\n// - ChatGPT",
    "// Computing Science Student Society \n// (CSSS)",
    //"if let Booth(info) = tech_fair {\n\t//TODO: this\n}",
    "// TODO: make tech fair awesome",
    "// run anually",
    "csss@CR:~/tf/$ fg\nbash: fg: current: no such job",
    "// meet your next co-op!",
    "// lots of tech companies!",
    "<h1>SFU_CSSS.TechFair(2023);</h1>",
];

// todo: add line numbers
function typeMessage(lastIndex) {
    // when a person types a word there are 3 main ways:
    // 1. type word fully, really quickly
    // 2. type word quickly and with a mistake (two letters backwards), then backspace to fix the mistake
    // 3. type word with a 1 or 2 pauses in the middle

    const MIN_KEYPRESS_TIME = 20;
    const MAX_KEYPRESS_TIME = 90;
    
    let randIndex = lastIndex;
    while (randIndex == lastIndex) {
        if (randIndex == -1) {
            randIndex = Math.floor(Math.random() * 2);            
        } else {
            randIndex = Math.floor(Math.random() * FRONT_PAGE_MESSAGES.length);
        }
    }
    let word = FRONT_PAGE_MESSAGES[randIndex];
    
    // TODO: do text coloring & do one word at a time! (broken up manually into a list)
    let element = document.getElementById("before-cursor");
    let typeLetter = function(i) {
        var keypressTime = Math.floor(MIN_KEYPRESS_TIME + Math.random() * (MAX_KEYPRESS_TIME - MIN_KEYPRESS_TIME));
        if (element.textContent.length < word.length) {
            if (word[i] == "\t") {
                element.textContent += "\t";
            } else {
                element.textContent += word[i];
            }
            if (word[i] == " " || word[i] == "." || word[i] == "(" || word[i] == "\t" || word[i] == "\n" || word[i] == ">" || word[i] == ";") {
                if (Math.random() > 0.8) {
                    keypressTime += 175;
                } else if (Math.random() > 0.95) {
                    // long pause
                    keypressTime += 340;
                }
            }
            setTimeout(() => { typeLetter(i+1) }, keypressTime);
        } else {
            setTimeout(eraseMessage, waitTime);
        }
    }
    typeLetter(0);

    const MIN_WAIT_TIME = 4000;
    const MAX_WAIT_TIME = 8000;
    var waitTime = Math.floor(MIN_WAIT_TIME + Math.random() * (MAX_WAIT_TIME - MIN_WAIT_TIME));
    
    let eraseMessage = function() {
        let eraseLetter = function() {
            if (element.textContent.length != 0) {
                element.textContent = element.textContent.substring(0, element.textContent.length-1);
                setTimeout(() => { eraseLetter() }, MIN_KEYPRESS_TIME);
            } else {
                setTimeout(() => { typeMessage(randIndex); }, 500);
            }
        }
        eraseLetter();
    }
}

function onload() {
    setTimeout(() => { typeMessage(-1); }, 500);
}