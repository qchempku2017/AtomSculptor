/**
 * export-panel.js – Structure export dialog and File System Access API flow.
 */

import { S } from "./state.js";
import { $ } from "./utils.js";
import { exportStructure, exportStructureWithPicker } from "./structure.js";
import { closeAllPanels } from "./panel-core.js";

/**
 * Click handler for the Export toolbar button.
 * On browsers that support the File System Access API (Chrome/Edge) the OS
 * native "Save As" dialog opens with a format-type selector built in.
 * On other browsers (Firefox) a compact <dialog> modal lets the user pick
 * a format before the browser auto-downloads the file.
 */
async function triggerExport() {
  closeAllPanels();

  if ("showSaveFilePicker" in window) {
    if (!S.structPath) {
      openExportDialog("No structure loaded.");
      return;
    }
    const name = S.structPath.split("/").pop().replace(/\.[^.]+$/, "") || "structure";
    const result = await exportStructureWithPicker(name);
    if (!result.ok && result.error) openExportDialog(result.error);
    return;
  }

  openExportDialog("");
}

function openExportDialog(errorMsg) {
  const dialog = document.getElementById("export-dialog");
  document.getElementById("ex-error").textContent = errorMsg || "";
  document.getElementById("ex-format").value = "cif";
  dialog.showModal();
}

async function handleDialogExport() {
  const errorEl = document.getElementById("ex-error");
  const btn = document.getElementById("ex-save");
  const format = document.getElementById("ex-format").value;

  errorEl.textContent = "";
  btn.disabled = true;
  btn.textContent = "Downloading...";

  try {
    const result = await exportStructure(format);
    if (!result.ok) {
      errorEl.textContent = result.error || "Export failed.";
      return;
    }
    document.getElementById("export-dialog").close();
  } finally {
    btn.disabled = false;
    btn.textContent = "Download";
  }
}

export function wireExportPanel() {
  $("#tb-export").addEventListener("click", triggerExport);

  const exportDialog = document.getElementById("export-dialog");
  document.getElementById("ex-cancel").addEventListener("click", () => exportDialog.close());
  document.getElementById("ex-save").addEventListener("click", handleDialogExport);
  exportDialog.addEventListener("click", (e) => {
    if (e.target === exportDialog) exportDialog.close();
  });
}
