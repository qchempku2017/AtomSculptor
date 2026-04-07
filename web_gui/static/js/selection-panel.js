/**
 * selection-panel.js – Selection operations tool panel.
 */

import { $, showError, clearError } from "./utils.js";
import { selectAtomsByTypes, expandSelectionByRadius, invertSelection, extractSelectedToNewLayer } from "./structure.js";
import { closeAllPanels } from "./panel-core.js";

function openSelectionPanel() {
  closeAllPanels();
  clearError("#sel-error");
  $("#sel-types-input").value = "";
  $("#sel-expand-radius").value = "1.5";
  $("#selection-panel").classList.add("show");
  $("#tb-box").classList.add("active");

  $("#sel-types-btn").onclick = async () => {
    clearError("#sel-error");
    try {
      const raw = $("#sel-types-input").value || "";
      const symbols = raw.split(/[,\s]+/).map(s => s.trim()).filter(Boolean).map(s => s.replace(/[^A-Za-z]/g, ""));
      if (!symbols.length) { showError("#sel-error", "Enter at least one element symbol."); return; }
      await selectAtomsByTypes(symbols);
      $("#selection-panel").classList.remove("show");
      $("#tb-box").classList.remove("active");
    } catch (e) { showError("#sel-error", String(e)); }
  };

  $("#sel-expand-btn").onclick = async () => {
    clearError("#sel-error");
    try {
      const r = parseFloat($("#sel-expand-radius").value);
      if (!Number.isFinite(r) || r <= 0) { showError("#sel-error", "Enter a positive radius."); return; }
      await expandSelectionByRadius(r);
    } catch (e) { showError("#sel-error", String(e)); }
  };

  $("#sel-invert-btn").onclick = async () => {
    clearError("#sel-error");
    try {
      await invertSelection();
    } catch (e) { showError("#sel-error", String(e)); }
  };

  $("#sel-extract-btn").onclick = () => {
    clearError("#sel-error");
    try {
      const res = extractSelectedToNewLayer();
      if (!res.ok) showError("#sel-error", res.error || "Failed to extract.");
      else { $("#selection-panel").classList.remove("show"); $("#tb-box").classList.remove("active"); }
    } catch (e) { showError("#sel-error", String(e)); }
  };

  $("#sel-cancel").onclick = () => { closeAllPanels(); };
}

export function toggleSelectionPanel() {
  const panel = $("#selection-panel");
  if (panel.classList.contains("show")) {
    closeAllPanels();
  } else {
    openSelectionPanel();
  }
}
