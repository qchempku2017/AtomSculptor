/**
 * supercell-panel.js – Supercell builder tool panel.
 */

import { S } from "./state.js";
import { $, showError, clearError } from "./utils.js";
import { buildSupercell } from "./structure.js";
import { togglePanel } from "./panel-core.js";

async function handleSupercellBuild() {
  clearError("#sc-error");

  if (!S.structPath) {
    showError("#sc-error", "Load a structure first.");
    return;
  }

  const ids = [
    ["sc-m00", "sc-m01", "sc-m02"],
    ["sc-m10", "sc-m11", "sc-m12"],
    ["sc-m20", "sc-m21", "sc-m22"],
  ];
  const matrix = ids.map((row) => row.map((id) => parseInt($(`#${id}`).value, 10)));

  if (matrix.flat().some((v) => isNaN(v))) {
    showError("#sc-error", "All matrix entries must be integers.");
    return;
  }

  const btn = $("#sc-build");
  btn.disabled = true;
  btn.textContent = "Building...";
  try {
    const result = await buildSupercell(matrix);
    if (result.error) {
      showError("#sc-error", result.error);
    } else {
      $("#supercell-panel").classList.remove("show");
    }
  } catch (e) {
    showError("#sc-error", String(e));
  } finally {
    btn.disabled = false;
    btn.textContent = "Build";
  }
}

export function wireSupercellPanel() {
  $("#tb-supercell").addEventListener("click", () => {
    togglePanel("#supercell-panel", () => clearError("#sc-error"));
  });
  $("#sc-cancel").addEventListener("click", () => $("#supercell-panel").classList.remove("show"));
  $("#sc-build").addEventListener("click", handleSupercellBuild);
}
