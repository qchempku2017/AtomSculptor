/**
 * lattice-panel.js – Lattice operations tool panel.
 */

import { S } from "./state.js";
import { $, showError, clearError, setMatrixInputs, readMatrixInputs, multiplyMatrices } from "./utils.js";
import { applyLattice } from "./structure.js";
import { togglePanel } from "./panel-core.js";

function initializeLatticePanel() {
  setMatrixInputs("la-sm", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]);
  if (Array.isArray(S.cell) && S.cell.length === 3) {
    setMatrixInputs("la-rm", S.cell);
  } else {
    setMatrixInputs("la-rm", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]);
  }
  $("#la-scale-atoms").checked = true;
  clearError("#la-error");
}

function handleScaleUpdate() {
  try {
    const scaleMat = readMatrixInputs("la-sm");
    const currentCell = Array.isArray(S.cell) && S.cell.length === 3
      ? S.cell : [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const newReal = multiplyMatrices(currentCell, scaleMat);
    setMatrixInputs("la-rm", newReal);
    clearError("#la-error");
  } catch (e) {
    showError("#la-error", String(e));
  }
}

function handleLatticeApply() {
  try {
    const realMat = readMatrixInputs("la-rm");
    const scaleAtoms = $("#la-scale-atoms").checked;
    applyLattice(realMat, scaleAtoms);
    $("#lattice-panel").classList.remove("show");
  } catch (e) {
    showError("#la-error", String(e));
  }
}

export function wireLatticePanel() {
  $("#tb-lattice").addEventListener("click", () => {
    togglePanel("#lattice-panel", initializeLatticePanel);
  });
  $("#la-cancel").addEventListener("click", () => $("#lattice-panel").classList.remove("show"));
  $("#la-update-real").addEventListener("click", handleScaleUpdate);
  $("#la-apply").addEventListener("click", handleLatticeApply);
}
