let rollDown = document.getElementById('head2');

rollDown.addEventListener('click', rollingThunder);

function rollingThunder() {
  window.location.href = "https://aa-engineers.net/services.html";
}


let rollDown1 = document.getElementById('head3');

rollDown1.addEventListener('click', rollingThunder1);

function rollingThunder1() {
  document.getElementById("fourthPart").scrollIntoView({ behavior: "smooth" });
}

let rollDown2 = document.getElementById('head4');

rollDown2.addEventListener('click', rollingThunder2);

function rollingThunder2() {
  document.getElementById("fifthPart").scrollIntoView({ behavior: "smooth" });
}

let rollDown3 = document.getElementById('head5');

rollDown3.addEventListener('click', rollingThunder3);

function rollingThunder3() {
  document.getElementById("sixthPart").scrollIntoView({ behavior: "smooth" });
}

let rollDown4 = document.getElementById('herobutton');

rollDown4.addEventListener('click', rollingThunder4);

function rollingThunder4() {
  document.getElementById("thirdPart").scrollIntoView({ behavior: "smooth" });
}
