"use strict";
(() => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message");
  const sendButton = document.getElementById("send");
  const messages = document.getElementById("messages");
  const status = document.getElementById("status");
  // Fresh ID per page load; the same ID is reused across messages on this page.
  const conversationId = (globalThis.crypto && typeof crypto.randomUUID === "function")
    ? crypto.randomUUID() : "demo-" + Date.now().toString(36);
  let pending = false;

  function addMessage(text, role) {
    const bubble = document.createElement("div");
    bubble.className = "bubble " + role;
    bubble.textContent = text; // Never interpret server/user content as HTML.
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || pending) return;
    pending = true;
    input.disabled = true;
    sendButton.disabled = true;
    status.textContent = "Nova está respondiendo…";
    addMessage(message, "user");
    input.value = "";
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({conversation_id: conversationId, message})
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      if (typeof data.reply !== "string") throw new Error("Respuesta inesperada");
      addMessage(data.reply, "assistant");
      status.textContent = "";
    } catch (error) {
      status.textContent = "No pudimos contactar a Nova. Puedes volver a enviar tu mensaje.";
      input.value = message;
      console.error("Nova chat request failed:", error);
    } finally {
      pending = false;
      input.disabled = false;
      sendButton.disabled = false;
      input.focus();
    }
  });
})();
