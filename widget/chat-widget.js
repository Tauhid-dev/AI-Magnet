(function () {
  "use strict";

  var currentScript = document.currentScript;
  var config = {
    apiBaseUrl: currentScript && currentScript.dataset.apiBaseUrl
      ? currentScript.dataset.apiBaseUrl.replace(/\/$/, "")
      : "http://127.0.0.1:8000",
    widgetKey: currentScript ? currentScript.dataset.widgetKey : "",
    title: currentScript && currentScript.dataset.title
      ? currentScript.dataset.title
      : "Chat with us",
  };

  if (!config.widgetKey) {
    return;
  }

  var state = {
    conversationId: null,
    isOpen: false,
  };

  var launcher = document.createElement("button");
  launcher.type = "button";
  launcher.setAttribute("aria-label", config.title);
  launcher.textContent = "Chat";
  launcher.style.cssText = [
    "position:fixed",
    "right:20px",
    "bottom:20px",
    "z-index:2147483000",
    "border:0",
    "border-radius:8px",
    "background:#1f6feb",
    "color:#fff",
    "font:600 15px system-ui,-apple-system,BlinkMacSystemFont,sans-serif",
    "padding:12px 16px",
    "box-shadow:0 8px 24px rgba(15,23,42,.22)",
    "cursor:pointer",
  ].join(";");

  var panel = document.createElement("section");
  panel.setAttribute("aria-label", config.title);
  panel.style.cssText = [
    "position:fixed",
    "right:20px",
    "bottom:76px",
    "z-index:2147483000",
    "width:min(360px,calc(100vw - 32px))",
    "height:480px",
    "display:none",
    "grid-template-rows:auto 1fr auto",
    "background:#fff",
    "border:1px solid #d7dde8",
    "border-radius:8px",
    "box-shadow:0 18px 48px rgba(15,23,42,.24)",
    "overflow:hidden",
    "font:14px system-ui,-apple-system,BlinkMacSystemFont,sans-serif",
  ].join(";");

  panel.innerHTML = [
    "<header style=\"background:#172033;color:#fff;padding:14px 16px;font-weight:700;\">",
    escapeHtml(config.title),
    "</header>",
    "<div data-wm-messages style=\"padding:14px;overflow:auto;background:#f7f9fc;\"></div>",
    "<form data-wm-form style=\"display:flex;gap:8px;padding:12px;border-top:1px solid #d7dde8;background:#fff;\">",
    "<input data-wm-input aria-label=\"Message\" autocomplete=\"off\" placeholder=\"Type your message\" style=\"min-width:0;flex:1;border:1px solid #cbd5e1;border-radius:6px;padding:10px;font:14px system-ui;\" />",
    "<button type=\"submit\" style=\"border:0;border-radius:6px;background:#1f6feb;color:#fff;font-weight:700;padding:0 14px;cursor:pointer;\">Send</button>",
    "</form>",
  ].join("");

  document.body.appendChild(panel);
  document.body.appendChild(launcher);

  var messages = panel.querySelector("[data-wm-messages]");
  var form = panel.querySelector("[data-wm-form]");
  var input = panel.querySelector("[data-wm-input]");

  launcher.addEventListener("click", function () {
    state.isOpen = !state.isOpen;
    panel.style.display = state.isOpen ? "grid" : "none";
    if (state.isOpen && !state.conversationId) {
      startConversation();
    }
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var text = input.value.trim();
    if (!text || !state.conversationId) {
      return;
    }
    input.value = "";
    appendMessage("You", text);
    postMessage(text);
  });

  function startConversation() {
    appendMessage("Assistant", "Hi, I am the AI receptionist. How can I help?");
    request("/chat/conversations", {
      widget_key: config.widgetKey,
      origin: window.location.origin,
    }).then(function (payload) {
      state.conversationId = payload.conversation_id;
    }).catch(function () {
      appendMessage("Assistant", "Sorry, this chat is not available right now.");
    });
  }

  function postMessage(text) {
    request("/chat/conversations/" + encodeURIComponent(state.conversationId) + "/messages", {
      widget_key: config.widgetKey,
      message: text,
      origin: window.location.origin,
    }).then(function (payload) {
      appendMessage("Assistant", payload.assistant_message);
      if (payload.lead_capture && payload.lead_capture.next_prompt) {
        appendMessage("Assistant", payload.lead_capture.next_prompt);
      }
    }).catch(function () {
      appendMessage("Assistant", "Sorry, I could not send that message.");
    });
  }

  function request(path, body) {
    return fetch(config.apiBaseUrl + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("Request failed");
      }
      return response.json();
    });
  }

  function appendMessage(author, text) {
    var item = document.createElement("div");
    item.style.cssText = "margin:0 0 10px;padding:10px;border-radius:8px;background:#fff;border:1px solid #e2e8f0;";
    item.innerHTML = "<strong>" + escapeHtml(author) + ":</strong> " + escapeHtml(text);
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#039;",
      }[character];
    });
  }
})();
