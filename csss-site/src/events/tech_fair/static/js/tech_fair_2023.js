const laptop = document.getElementById("laptop");
const laptopDiv = document.getElementById("laptop-div");
var mouseIn = false;

function onload() {
    updateBanner();

    laptopDiv.addEventListener("mouseenter", (event) => {
        //event.target.getSVGDocument().getElementById("main").setAttribute("fill", "#97f");
        mouseIn = true;
    }, false);
    laptopDiv.addEventListener("mouseleave", (event) => {
        //event.target.getSVGDocument().getElementById("main").setAttribute("fill", "black");
        mouseIn = false;
    }, false);

    window.requestAnimationFrame(update);
}

function update(timeStamp) {
    let amount = mouseIn ? -8 : 18;
    laptop.style.marginLeft = parseInt(laptop.style.marginLeft) + amount + "px";
    if (parseInt(laptop.style.marginLeft) <= 0) {
        laptop.style.marginLeft = "0px";
    } else if(parseInt(laptop.style.marginLeft) >= 240) {
        laptop.style.marginLeft = "240px";
    }
    window.requestAnimationFrame(update);
}

function updateBanner() {
    document.getElementById("info-banner").hidden = false;
    document.getElementById("info-banner").style.height = document.getElementById("info-text").clientHeight + 24 + "px";
    console.log("yep");
}


