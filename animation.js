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

