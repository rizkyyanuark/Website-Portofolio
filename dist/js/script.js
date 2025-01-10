// filepath: /C:/Users/rizky/OneDrive/Dokumen/GitHub/Website-Portofolio/dist/js/script.js
class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector(".chatbox__button"),
      chatBox: document.querySelector(".chatbox__support"),
      sendButton: document.querySelector(".send__button"),
    };

    this.state = false;
    this.messages = [];
  }

  display() {
    const { openButton, chatBox, sendButton } = this.args;

    openButton.addEventListener("click", () => this.toggleState(chatBox));

    sendButton.addEventListener("click", () => this.onSendButton(chatBox));

    const node = chatBox.querySelector("input");
    node.addEventListener("keyup", ({ key }) => {
      if (key === "Enter") {
        this.onSendButton(chatBox);
      }
    });
  }

  toggleState(chatbox) {
    this.state = !this.state;

    // show or hides the box
    if (this.state) {
      chatbox.classList.add("chatbox--active");
      this.sendWelcomeMessage(chatbox);
    } else {
      chatbox.classList.remove("chatbox--active");
    }
  }

  sendWelcomeMessage(chatbox) {
    if (this.messages.length === 0) {
      let msg = { name: "airi", message: "Hi. My name is airi. How can I help you?" };
      this.messages.push(msg);
      this.updateChatText(chatbox);
    }
  }

  onSendButton(chatbox) {
    var textField = chatbox.querySelector("input");
    let text1 = textField.value;
    if (text1 === "") {
      return;
    }

    // Clear the input field immediately
    textField.value = "";

    let msg1 = { name: "User", message: text1 };
    this.messages.push(msg1);
    this.updateChatText(chatbox);

    // Add a "thinking" message
    let thinkingMsg = { name: "airi", message: "Thinking..." };
    this.messages.push(thinkingMsg);
    this.updateChatText(chatbox);

    fetch("https://nv-bite-api-279551392308.asia-southeast1.run.app/chatbot", {
      method: "POST",
      body: JSON.stringify({ message: text1 }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // Remove the "thinking" message
        this.messages.pop();

        let msg2 = { name: "airi", message: data.answer };
        this.messages.push(msg2);
        this.updateChatText(chatbox);
      })
      .catch((error) => {
        console.error("Error:", error);
        this.updateChatText(chatbox);
      });
  }

  updateChatText(chatbox) {
    var html = "";
    this.messages
      .slice()
      .reverse()
      .forEach(function (item, index) {
        if (item.name === "airi") {
          html += '<div class="messages__item messages__item--visitor">' + item.message + "</div>";
        } else {
          html += '<div class="messages__item messages__item--operator">' + item.message + "</div>";
        }
      });

    const chatmessage = chatbox.querySelector(".chatbox__messages");
    chatmessage.innerHTML = html;
  }
}

const chatbox = new Chatbox();
chatbox.display();

window.onscroll = function () {
  const header = document.querySelector("header");
  const fixedNav = header.offsetTop;

  if (window.pageYOffset > fixedNav) {
    header.classList.add("navbar-fixed");
  } else {
    header.classList.remove("navbar-fixed");
  }
};

// Hamburger
const hamburger = document.querySelector("#hamburger");
const navMenu = document.querySelector("#nav-menu");

hamburger.addEventListener("click", function () {
  hamburger.classList.toggle("hamburger-active");
  navMenu.classList.toggle("hidden");
});
