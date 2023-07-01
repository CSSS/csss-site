const PX       = 100 / 128;
const BALLV    = 12 * PX;
const PADDLEV  = 12 * PX;
const SPEED    = 10;
const START    = { "x": 50, "y": 10 };

let v = {
	"x": 1,
	"y": 1
};
let pv = 1; // paddle velocity
let mx = 50;
let my = 50;

let ball, userPaddle, paddle;
let pong = false;

function updateBall(delta) {
	if (ball === undefined || !pong) return;

	let x = parseFloat(ball.style.left);
	let y = parseFloat(ball.style.top);

	x += v.x * BALLV * delta;
	y += v.y * BALLV * delta;

	upt = parseFloat(userPaddle.style.top);
	pt = parseFloat(paddle.style.top);

	// collision with player paddle
	if (x < 12*PX && y > upt - 16*PX && y < upt + 16*PX) {
		v.x = 1;
	}

	// collision with paddle
	if (x > 100 - 12*PX && y > pt - 16*PX && y < pt + 16*PX) {
		v.x = -1;
	}

	// collision with center blockleft wall

	// left wall
	if (x > 50 - 20*PX && y > 50 - 16*PX && y < 50 + 16*PX && x < 50 - 16*PX)
		v.x = -1;
	// right wall
	if (x < 50 + 20*PX && y > 50 - 16*PX && y < 50 + 16*PX && x > 50 + 16*PX)
		v.x = 1;
	// top wall
	if (x > 50 - 16*PX && y > 50 + 16*PX && y < 50 + 20*PX && x < 50 + 16*PX)
		v.y = 1;
	// bottom wall
	if (x > 50 - 16*PX && y > 50 - 20*PX && y < 50 - 16*PX && x < 50 + 16*PX)
		v.y = -1;

	if (x < 8*PX || x > 100 - 8*PX) {
		x = START.x;
		y = START.y;
		v.x *= -1;
		v.y *= -1;
	}

	if (y >= 100 - 4*PX || y <= 4*PX) {
		v.y *= -1;
	}

	ball.style.left = `${x}%`;
	ball.style.top = `${y}%`;
}

function updateUserPaddle(delta) {
	if (userPaddle === undefined || !pong) return;

	let y = parseFloat(userPaddle.style.top);
	let dy = my - y;

	if (Math.abs(dy) < 4*PX)
		return;

	y += Math.sign(dy) * PADDLEV * delta;

	if (y > 100 - 16*PX)
		y = 100 - 16*PX;

	if (y < 16*PX)
		y = 16*PX;

	userPaddle.style.top = `${y}%`;
}

function updatePaddle(delta) {
	if (paddle === undefined || !pong) return;

	let y = parseFloat(paddle.style.top);
	let bx = parseFloat(ball.style.left);
	let by = parseFloat(ball.style.top);

	if (bx > 25) {
		let dy = by - y;

		if (Math.abs(dy) < 4*PX)
			return;

		pv = Math.sign(dy);
		y += pv * PADDLEV * delta;
	} else {
		y += pv * PADDLEV * delta;
	}

	if (y > 100 - 16*PX) {
		pv *= -1;
		y = 100 - 16*PX;
	}

	if (y < 16*PX) {
		pv *= -1;
		y = 16*PX;
	}

	paddle.style.top = `${y}%`;
}

let prev;

function animate(time) {
	let delta = 0;

	if (prev === undefined)
		prev = time;
	else
		delta = (time - prev) / 500;

	updateBall(delta);
	updateUserPaddle(delta);
	updatePaddle(delta);

	prev = time;

	console.log(`${pong}, ${time}, ${delta}`);
	window.requestAnimationFrame(animate);
}

let selected = null;

window.onload = () => {
	// scrolling

	let header       = document.getElementById("header");
	let box          = document.getElementById("pong-box");
	let scrollPrompt = document.getElementById("scroll-prompt");
	let topPrompt    = document.getElementById("top-prompt");

	window.onscroll = () => {
		if (window.scrollY > 256) {
			//scrollPrompt.style.visibility = "hidden";
			//topPrompt.style.visibility = "visible";
		} else {
			//scrollPrompt.style.visibility = "visible";
			//topPrompt.style.visibility = "hidden";
		}

		if (window.scrollY > 0) {
			header.classList.add("sticky");
			box.style.marginTop = "57px";
		} else {
			header.classList.remove("sticky");
			box.style.marginTop = "0px";

			if (selected != null) {
				//selected.classList.remove("select");
				selected = null;
			}
		}
	};

	window.onscroll();

	// header

	let menu = document.getElementById("collapse-menu");

	for (const a of menu.children) {
		a.onclick = () => {
			if (selected != null)
				selected.classList.remove("select");

			selected = a;
			a.classList.add("select");
		};
	}

	document.getElementById("collapse-icon").onclick = () => {
		let menu = document.getElementById("collapse-menu");

		menu.classList.toggle("collapse-hide");
	};

	// top prompt

	// pong game

	box.onmousemove = () => {
		e = window.event;

		rect = box.getBoundingClientRect();

		mx = (e.clientX - rect.left) / box.clientWidth * 100;
		my = (e.clientY - rect.top) / box.clientHeight * 100;
	};

	ball = document.getElementById("ball");
	ball.style.left = "75%";
	ball.style.top = "25%";

	userPaddle = document.getElementById("paddle-a");
	userPaddle.style.left = "0%";
	userPaddle.style.top = "50%";

	paddle = document.getElementById("paddle-b");
	paddle.style.right = "0%";
	paddle.style.top = "50%";

	window.requestAnimationFrame(animate);
};
