/**
 * surface-panel.js – Surface builder tool panel.
 */

import { S } from "./state.js";
import { $, showError, clearError } from "./utils.js";
import { buildSurface } from "./structure.js";
import { togglePanel } from "./panel-core.js";

async function handleSurfaceBuild() {
  clearError("#sf-error");

  if (!S.structPath) {
    showError("#sf-error", "Load a structure first.");
    return;
  }

  const h = parseInt($("#sf-h").value, 10);
  const k = parseInt($("#sf-k").value, 10);
  const l = parseInt($("#sf-l").value, 10);
  const layers = parseInt($("#sf-layers").value, 10);
  const vacuum = parseFloat($("#sf-vacuum").value);

  if ([h, k, l].some(v => isNaN(v))) {
    showError("#sf-error", "Miller indices must be integers.");
    return;
  }
  if (h === 0 && k === 0 && l === 0) {
    showError("#sf-error", "Miller indices cannot all be zero.");
    return;
  }

  const btn = $("#sf-build");
  btn.disabled = true;
  btn.textContent = "Building...";
  try {
    const result = await buildSurface([h, k, l], layers, vacuum);
    if (result.error) {
      showError("#sf-error", result.error);
    } else {
      $("#surface-panel").classList.remove("show");
    }
  } catch (e) {
    showError("#sf-error", String(e));
  } finally {
    btn.disabled = false;
    btn.textContent = "Build";
  }
}

export function wireSurfacePanel() {
  $("#tb-surface").addEventListener("click", () => {
    togglePanel("#surface-panel", () => clearError("#sf-error"));
  });
  $("#sf-cancel").addEventListener("click", () => $("#surface-panel").classList.remove("show"));
  $("#sf-build").addEventListener("click", handleSurfaceBuild);
}
