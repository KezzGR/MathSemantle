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

  if (!word.trim()) {
    alert("Введите слово");
    return;
  }

  fetch("/guess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word: word }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error(data.error);
        alert(data.error);
        return;
      }

      if (data.win == true) {
        winText.textContent = "Вы отгадали слово!";
      }

      const userWord = document.createElement("li");
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
