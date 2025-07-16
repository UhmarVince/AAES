const textElement = document.getElementById("head4");
const originalText = textElement.textContent;

function shuffleText(element, text, duration = 2000) {
  const characters = '01sd3@^$ada@32001';
  const textArray = text.split("");
  const iterations = text.length * 50; // How many shuffles per character
  let counter = 0;

  const interval = setInterval(() => {
    const newText = textArray.map((char, i) => {
      if (counter > i * iterations / textArray.length) return char;
      return characters.charAt(Math.floor(Math.random() * characters.length));
    }).join("");

    element.textContent = newText;

    counter += textArray.length;
    if (counter > iterations) {
      clearInterval(interval);
      element.textContent = text; // Reset to the original text
    }
  }, 50);
}

shuffleText(textElement, originalText);

const textElement5 = document.getElementById("head5");
const originalText5 = textElement5.textContent;

function shuffleText5(element, text, duration = 2000) {
  const characters = 'tuabo!@#$%^&*()';
  const textArray = text.split("");
  const iterations = text.length * 10; // How many shuffles per character
  let counter = 0;

  const interval = setInterval(() => {
    const newText = textArray.map((char, i) => {
      if (counter > i * iterations / textArray.length) return char;
      return characters.charAt(Math.floor(Math.random() * characters.length));
    }).join("");

    element.textContent = newText;

    counter += textArray.length;
    if (counter > iterations) {
      clearInterval(interval);
      element.textContent = text; // Reset to the original text
    }
  }, 50);
}

shuffleText(textElement5, originalText5);

const textElement6 = document.getElementById("head6");
const originalText6 = textElement6.textContent;

function shuffleText6(element, text, duration = 2000) {
  const characters = '!@#$%^&*()';
  const textArray = text.split("");
  const iterations = text.length * 3; // How many shuffles per character
  let counter = 0;

  const interval = setInterval(() => {
    const newText = textArray.map((char, i) => {
      if (counter > i * iterations / textArray.length) return char;
      return characters.charAt(Math.floor(Math.random() * characters.length));
    }).join("");

    element.textContent = newText;

    counter += textArray.length;
    if (counter > iterations) {
      clearInterval(interval);
      element.textContent = text; // Reset to the original text
    }
  }, 50);
}

shuffleText(textElement6, originalText6);

const textElement7 = document.getElementById("head7");
const originalText7 = textElement7.textContent;

function shuffleText7(element7, text, duration = 2000) {
  const characters7 = '!@#$%';
  const textArray7 = text7.split("");
  const iterations7 = text7.length * 1; // How many shuffles per character
  let counter = 0;

  const interval7 = setInterval(() => {
    const newText7 = textArray7.map((char, i) => {
      if (counter > i * iterations7 / textArray7.length) return char;
      return characters7.charAt(Math.floor(Math.random() * characters7.length));
    }).join("");

    element7.textContent = newText7;

    counter += textArray7.length;
    if (counter > iterations7) {
      clearInterval(interval7);
      element7.textContent = text; // Reset to the original text
    }
  }, 50);
}

shuffleText(textElement7, originalText7);

window.addEventListener('scroll', function() {
  var element = document.getElementById('slideUpDiv');
  var position = element.getBoundingClientRect();

  // Check if the element is in view (in the viewport)
  if (position.top <= window.innerHeight && position.bottom >= 0) {
    element.classList.add('show');
  }
});



const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

hamburger.addEventListener('click', () => {
  navMenu.classList.toggle('show');
});
