let userInput = document.getElementById("userInput");
let sendButton = document.getElementById("sendButton");

userInput.addEventListener("keydown", function (event) {
  if (event.key == "Enter") {
    send();
  }
});
sendButton.addEventListener("click", send);

function send() {
  const word = userInput.value;

  fetch("/guess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word: word }),
  })
    .then((response) => response.json())
    .then((data) => {
      userInput.value = "";
      userInput.focus();
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
}
