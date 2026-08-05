const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const userWords = document.getElementById("userWords");
const winText = document.getElementById("winText");

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
      if (data.win == true) {
        winText.textContent = "Вы отгадали слово!";
      }

      userWord = document.createElement("li");
      userWord.textContent =
        "Слово: " + word + " | Косинусное сходство: " + data.cos_sim;

      userWords.appendChild(userWord);

      userInput.value = "";
      userInput.focus();
    })
    .catch((error) => {
      console.error("Ошибка:", error);
    });
}
