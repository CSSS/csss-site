window.onload = () => {
	let cd_days = document.getElementById("days");
	let cd_hours = document.getElementById("hours");
	let cd_mins = document.getElementById("mins");
	let cd_secs = document.getElementById("secs");

	// target date is September 11th, 2023, 1:00PM; the start of the Ice-Cream Social.
	let target = new Date("Sep 11, 2023 13:00:00").getTime();
	let func = () => {
		let now = new Date().getTime();
		let distance = target - now;

		let days = Math.floor(distance / (1000 * 60 * 60 * 24));
		let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
		let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
		let seconds = Math.floor((distance % (1000 * 60)) / 1000);

		cd_days.innerHTML = `${days}`;
		cd_hours.innerHTML = `${hours}`;
		cd_mins.innerHTML = `${minutes}`;
		cd_secs.innerHTML = `${seconds}`;
	};
	func();

	// create the interval
	let i = setInterval(func, 1000);
}
