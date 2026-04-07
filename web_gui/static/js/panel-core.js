/**
 * panel-core.js – Shared panel infrastructure (open / close / toggle).
 *
 * Kept separate from individual panel modules so each panel can import
 * `closeAllPanels` without creating circular dependencies.
 */

import { $, $$ } from "./utils.js";

/** Close every tool panel and deactivate associated toolbar buttons. */
export function closeAllPanels() {
  for (const el of $$(".tool-panel")) el.classList.remove("show");
  for (const id of ["#tb-add", "#tb-box"]) $(id)?.classList.remove("active");
}

/**
 * Toggle a single panel: close all others first, then show the target
 * if it was not already open.  Runs `onOpen` when the panel is opening.
 */
export function togglePanel(panelSelector, onOpen) {
  const panel = $(panelSelector);
  const wasOpen = panel.classList.contains("show");
  closeAllPanels();
  if (!wasOpen) {
    if (onOpen) onOpen();
    panel.classList.add("show");
  }
}
