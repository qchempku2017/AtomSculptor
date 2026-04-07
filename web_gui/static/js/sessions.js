/**
 * sessions.js – Session history panel.
 *
 * Renders the list of sessions in #panel-sessions, supports click-to-switch,
 * and a right-click context menu for rename / delete.
 */

import { S } from "./state.js";
import { wsSend } from "./websocket.js";
import {
  appendUser, appendAgent, appendToolCall, appendToolResult, appendError,
} from "./chat.js";

// ── Context menu ──────────────────────────────────────────────────────────────

let _ctxMenu = null;
let _ctxSessionId = null;

function _removeCtxMenu() {
  if (_ctxMenu) { _ctxMenu.remove(); _ctxMenu = null; }
}

function _showCtxMenu(e, sessionId) {
  _removeCtxMenu();
  _ctxSessionId = sessionId;

  const menu = document.createElement("div");
  menu.className = "session-ctx-menu";
  menu.style.left = `${e.clientX}px`;
  menu.style.top  = `${e.clientY}px`;

  const rename = document.createElement("div");
  rename.className = "session-ctx-item";
  rename.textContent = "Rename";
  rename.onclick = () => { _removeCtxMenu(); _renameSession(sessionId); };

  const del = document.createElement("div");
  del.className = "session-ctx-item danger";
  del.textContent = "Delete";
  del.onclick = () => { _removeCtxMenu(); _deleteSession(sessionId); };

  menu.appendChild(rename);
  menu.appendChild(del);
  document.body.appendChild(menu);
  _ctxMenu = menu;
}

document.addEventListener("click",  _removeCtxMenu);
document.addEventListener("scroll", _removeCtxMenu, true);

// ── Rename / Delete via REST ──────────────────────────────────────────────────

async function _renameSession(sessionId) {
  const current = S.sessions.find(s => s.id === sessionId);
  const newName = prompt("Rename session:", current ? current.name : "");
  if (!newName || !newName.trim()) return;

  try {
    const res = await fetch("/api/sessions/rename", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, name: newName.trim() }),
    });
    const data = await res.json();
    if (data.ok) {
      // Update local state and re-render
      const entry = S.sessions.find(s => s.id === sessionId);
      if (entry) entry.name = newName.trim();
      renderSessions(S.sessions, S.currentSessionId);
    }
  } catch (_) {}
}

async function _deleteSession(sessionId) {
  const current = S.sessions.find(s => s.id === sessionId);
  if (!confirm(`Delete session "${current ? current.name : sessionId}"?`)) return;

  try {
    const res = await fetch("/api/sessions/delete", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    const data = await res.json();
    if (data.ok) {
      // Remove from local state
      S.sessions = S.sessions.filter(s => s.id !== sessionId);

      // If the deleted session was active, switch to the last remaining one
      if (sessionId === S.currentSessionId && S.sessions.length > 0) {
        const target = S.sessions[S.sessions.length - 1];
        wsSend({ type: "switch_session", session_id: target.id });
      } else if (sessionId === S.currentSessionId) {
        S.currentSessionId = null;
        renderSessions(S.sessions, S.currentSessionId);
        wsSend({ type: "new_session" });
      } else {
        renderSessions(S.sessions, S.currentSessionId);
      }
    }
  } catch (_) {}
}

// ── Render ────────────────────────────────────────────────────────────────────

export function renderSessions(sessions, activeId) {
  const list = document.getElementById("sessions-list");
  if (!list) return;
  list.innerHTML = "";

  // Show newest sessions at the top
  const reversed = [...sessions].reverse();
  for (const s of reversed) {
    const item = document.createElement("div");
    item.className = "session-item" + (s.id === activeId ? " active" : "");
    item.dataset.sid = s.id;

    const name = document.createElement("span");
    name.className = "session-item-name";
    name.textContent = s.name;

    item.appendChild(name);

    item.addEventListener("click", () => {
      if (s.id !== S.currentSessionId) {
        wsSend({ type: "switch_session", session_id: s.id });
      }
    });
    item.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      _showCtxMenu(e, s.id);
    });

    list.appendChild(item);
  }
}

// ── Replay messages after session switch ──────────────────────────────────────

export function replayMessages(messages) {
  const chatEl = document.getElementById("chat-messages");
  if (!chatEl) return;
  chatEl.innerHTML = "";

  for (const m of messages) {
    switch (m.type) {
      case "user_message":  appendUser(m.text); break;
      case "agent_message": appendAgent(m.author, m.text); break;
      case "tool_call":     appendToolCall(m.author, m.tool, m.args); break;
      case "tool_result":   appendToolResult(m.author, m.tool, m.result); break;
      case "error":         appendError(m.text, m.traceback); break;
    }
  }
  // Scroll to bottom
  const scrollEl = document.getElementById("chat-scroll");
  if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
}

// ── Init ──────────────────────────────────────────────────────────────────────

export function initSessions() {
  const btn = document.getElementById("btn-new-session");
  if (btn) {
    btn.addEventListener("click", () => wsSend({ type: "new_session" }));
  }
}
