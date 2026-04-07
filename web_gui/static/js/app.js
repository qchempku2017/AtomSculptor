/**
 * app.js – Main entry point.  Wires up every subsystem on DOMContentLoaded.
 *
 * Module map:
 *   state.js      – global state object & constants
 *   utils.js      – pure formatting / DOM helpers
 *   websocket.js  – WebSocket connection, message routing & dispatch
 *   chat.js       – chat panel rendering & message sending
 *   todo.js       – task-flow DAG (Cytoscape) & aggregator hint
 *   filesystem.js – workspace file-tree rendering
 *   viewer.js     – Three.js scene, camera, rendering loop
 *   structure.js  – structure data (load / save / undo-redo / detect)
 *   editor.js     – canvas interaction (select, box, mode switching, keyboard)
 *   panels.js     – tool panels (add atom, surface, supercell, lattice)
 *   gizmo.js      – TransformControls gizmo for translate/rotate/scale
 */

import { S } from "./state.js";
import { $ } from "./utils.js";
import { connect, wsSend } from "./websocket.js";
import { wireChat } from "./chat.js";
import { initSessions } from "./sessions.js";
import { initGraph, updateTodo } from "./todo.js";
import { initViewer } from "./viewer.js";
import { initLayersPanel } from "./layers.js";
import { setupCanvasEvents, setMode, wireToolbar, wireKeyboardShortcuts } from "./editor.js";
import { wirePanels } from "./panels.js";
import { initGizmo } from "./gizmo.js";

function reportStartupError(label, err) {
  console.error(`${label} startup error`, err);

  const text = err instanceof Error ? err.message : String(err);
  const status = $("#ws-label");
  if (status && !S.connected) {
    status.textContent = `${label} error`;
  }

  const messages = $("#chat-messages");
  if (messages) {
    const d = document.createElement("div");
    d.className = "msg-error";
    d.textContent = `${label} failed: ${text}`;
    messages.appendChild(d);
  }
}

function safeInit(label, fn) {
  try {
    fn();
    return true;
  } catch (err) {
    reportStartupError(label, err);
    return false;
  }
}

function initResizablePanels() {
  const app = document.getElementById("app");
  const panelIds = ["panel-left", "panel-chat", "panel-struct", "panel-right"];
  const minWidth = 140;

  document.querySelectorAll(".col-divider").forEach((divider, i) => {
    divider.addEventListener("mousedown", (e) => {
      e.preventDefault();
      const startX = e.clientX;
      const startWidths = panelIds.map(id =>
        document.getElementById(id).getBoundingClientRect().width
      );

      divider.classList.add("dragging");
      document.body.classList.add("col-dragging");

      function onMove(me) {
        const dx = me.clientX - startX;
        const maxDx = startWidths[i + 1] - minWidth;
        const minDx = -(startWidths[i] - minWidth);
        const d = Math.max(minDx, Math.min(maxDx, dx));
        const w = [...startWidths];
        w[i] += d;
        w[i + 1] -= d;
        app.style.gridTemplateColumns =
          `${w[0]}px 4px ${w[1]}px 4px ${w[2]}px 4px ${w[3]}px`;
      }

      function onUp() {
        divider.classList.remove("dragging");
        document.body.classList.remove("col-dragging");
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
      }

      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  safeInit("Chat", wireChat);
  safeInit("Sessions", initSessions);
  safeInit("Toolbar", wireToolbar);
  safeInit("Panels", wirePanels);
  safeInit("Layers", initLayersPanel);
  safeInit("Keyboard", wireKeyboardShortcuts);
  safeInit("Task graph", initGraph);
  safeInit("Resizable panels", initResizablePanels);

  // Wire non-chat header/panel buttons
  $("#btn-refresh-todo").addEventListener("click", () => wsSend({ type: "refresh_todo" }));
  $("#btn-refresh-files").addEventListener("click", () => wsSend({ type: "refresh_files" }));

  // Reset sessions and todo flow
  const resetBtn = $("#btn-reset-session");
  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      if (!confirm("Reset all sessions and the todo flow?")) return;
      try {
        const res = await fetch("/api/reset", { method: "POST" });
        const data = await res.json();
        if (data && data.ok) {
          // Clear chat UI and reconnect websocket to get a fresh server session
          const chat = document.getElementById("chat-messages");
          if (chat) chat.innerHTML = "";
          try {
            if (window.S && window.S.ws) {
              try { window.S.ws.close(); } catch (e) {}
              window.S.ws = null;
            }
          } catch (e) {}
          // reconnect
          try { connect(); } catch (e) {}

          // Also fetch fresh todo-flow directly and update UI immediately
          try {
            const tf = await fetch('/api/todo-flow');
            if (tf && tf.ok) {
              const j = await tf.json();
              try { updateTodo(j); } catch (e) {}
            }
          } catch (e) {}

          alert("Reset complete.");
        } else {
          alert("Reset failed: " + (data && data.error ? data.error : res.status));
        }
      } catch (err) {
        alert("Reset request failed: " + err);
      }
    });
  }

  connect();

  const viewerReady = safeInit("Viewer", initViewer);
  if (viewerReady) {
    safeInit("Gizmo", initGizmo);
    safeInit("Canvas controls", setupCanvasEvents);
    setMode("orbit");
  } else {
    $("#viewer-empty").textContent = "Viewer failed to initialize. Chat and workspace remain available.";
  }
});
