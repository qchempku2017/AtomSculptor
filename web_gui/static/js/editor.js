/**
 * editor.js – Edit-mode interactions: select, box-select, translate/rotate/scale
 *             (via TransformControls gizmo), add, delete.
 */

import { S } from "./state.js";
import { $, $$ } from "./utils.js";
import {
  raycastAtoms, atomIdFromMesh, setOrbitEnabled,
  updateAtomVisuals,
  elemColor, resetCamera, setViewDirection,
} from "./viewer.js";
import {
  addAtom,
  applyLattice,
  buildSurface,
  buildSupercell,
  deleteAtomById,
  deleteSelected,
  redoStructureEdit,
  saveStructure,
  snapshotStructureState,
  undoStructureEdit,
  updateStatusBar,
} from "./structure.js";
import { updateGizmo, nudgeTransform, isGizmoActive } from "./gizmo.js";

const TRANSFORM_MODES = new Set(["translate", "rotate", "scale"]);
const PERIODIC_TABLE_ROWS = [
  [[1, "H"], [18, "He"]],
  [[1, "Li"], [2, "Be"], [13, "B"], [14, "C"], [15, "N"], [16, "O"], [17, "F"], [18, "Ne"]],
  [[1, "Na"], [2, "Mg"], [13, "Al"], [14, "Si"], [15, "P"], [16, "S"], [17, "Cl"], [18, "Ar"]],
  [[1, "K"], [2, "Ca"], [3, "Sc"], [4, "Ti"], [5, "V"], [6, "Cr"], [7, "Mn"], [8, "Fe"], [9, "Co"], [10, "Ni"], [11, "Cu"], [12, "Zn"], [13, "Ga"], [14, "Ge"], [15, "As"], [16, "Se"], [17, "Br"], [18, "Kr"]],
  [[1, "Rb"], [2, "Sr"], [3, "Y"], [4, "Zr"], [5, "Nb"], [6, "Mo"], [7, "Tc"], [8, "Ru"], [9, "Rh"], [10, "Pd"], [11, "Ag"], [12, "Cd"], [13, "In"], [14, "Sn"], [15, "Sb"], [16, "Te"], [17, "I"], [18, "Xe"]],
  [[1, "Cs"], [2, "Ba"], [4, "Hf"], [5, "Ta"], [6, "W"], [7, "Re"], [8, "Os"], [9, "Ir"], [10, "Pt"], [11, "Au"], [12, "Hg"], [13, "Tl"], [14, "Pb"], [15, "Bi"], [16, "Po"], [17, "At"], [18, "Rn"]],
  [[1, "Fr"], [2, "Ra"], [4, "Rf"], [5, "Db"], [6, "Sg"], [7, "Bh"], [8, "Hs"], [9, "Mt"], [10, "Ds"], [11, "Rg"], [12, "Cn"], [13, "Nh"], [14, "Fl"], [15, "Mc"], [16, "Lv"], [17, "Ts"], [18, "Og"]],
  [[4, "La"], [5, "Ce"], [6, "Pr"], [7, "Nd"], [8, "Pm"], [9, "Sm"], [10, "Eu"], [11, "Gd"], [12, "Tb"], [13, "Dy"], [14, "Ho"], [15, "Er"], [16, "Tm"], [17, "Yb"], [18, "Lu"]],
  [[4, "Ac"], [5, "Th"], [6, "Pa"], [7, "U"], [8, "Np"], [9, "Pu"], [10, "Am"], [11, "Cm"], [12, "Bk"], [13, "Cf"], [14, "Es"], [15, "Fm"], [16, "Md"], [17, "No"], [18, "Lr"]],
];

function buildPeriodicRow(entries) {
  const row = Array(18).fill(null);
  for (const [columnIndex, elementSymbol] of entries) {
    row[columnIndex - 1] = elementSymbol;
  }
  return row;
}

function computeAddDefaultPosition() {
  if (Array.isArray(S.cell) && S.cell.length === 3) {
    const [a, b, c] = S.cell;
    return {
      x: (a[0] + b[0] + c[0]) / 2,
      y: (a[1] + b[1] + c[1]) / 2,
      z: (a[2] + b[2] + c[2]) / 2,
    };
  }

  if (!S.atoms.length) return { x: 0, y: 0, z: 0 };

  let minX = Infinity;
  let minY = Infinity;
  let minZ = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let maxZ = -Infinity;

  for (const atom of S.atoms) {
    minX = Math.min(minX, atom.x);
    minY = Math.min(minY, atom.y);
    minZ = Math.min(minZ, atom.z);
    maxX = Math.max(maxX, atom.x);
    maxY = Math.max(maxY, atom.y);
    maxZ = Math.max(maxZ, atom.z);
  }

  return {
    x: (minX + maxX) / 2,
    y: (minY + maxY) / 2,
    z: (minZ + maxZ) / 2,
  };
}

function setAddCoordinateInputs(position) {
  $("#add-x").value = position.x.toFixed(3);
  $("#add-y").value = position.y.toFixed(3);
  $("#add-z").value = position.z.toFixed(3);
}

function clearAddError() {
  const errEl = $("#add-error");
  errEl.classList.remove("show");
  errEl.textContent = "";
}

function showAddError(message) {
  const errEl = $("#add-error");
  errEl.textContent = message;
  errEl.classList.add("show");
}

function setSelectedAddElement(elementSymbol) {
  S.addElement = elementSymbol;
  $$(".pt-elem-btn").forEach((button) => {
    button.classList.toggle("selected", button.dataset.element === elementSymbol);
  });
}

// ── Select ──────────────────────────────────────────────────────────────────

function onSelectClick(e) {
  const hit = raycastAtoms(e);
  if (!hit) {
    if (!e.shiftKey) {
      S.selected.clear();
      updateAtomVisuals();
      updateGizmo();
      updateStatusBar();
    }
    return;
  }

  const id = atomIdFromMesh(hit.object);
  if (e.shiftKey) {
    S.selected.add(id);
  } else {
    S.selected.clear();
    S.selected.add(id);
  }

  updateAtomVisuals();
  updateGizmo();
  updateStatusBar();
}

// ── Delete ──────────────────────────────────────────────────────────────────

function onDeleteClick(e) {
  const hit = raycastAtoms(e);
  if (!hit) return;
  deleteAtomById(atomIdFromMesh(hit.object));
  updateGizmo();
}

// ── Add Atom ────────────────────────────────────────────────────────────────

export function buildAddPalette() {
  const table = $("#add-periodic-table");
  table.innerHTML = "";

  for (let rowIndex = 0; rowIndex < PERIODIC_TABLE_ROWS.length; rowIndex += 1) {
    const rowEntries = PERIODIC_TABLE_ROWS[rowIndex];
    const rowElement = document.createElement("div");
    rowElement.className = "pt-row";

    const isSeriesRow = rowIndex >= 7;
    if (isSeriesRow) {
      rowElement.classList.add("pt-row-series");
      if (rowIndex === 7) rowElement.classList.add("pt-row-series-start");

      const seriesElements = [...rowEntries]
        .sort((left, right) => left[0] - right[0])
        .map((entry) => entry[1]);

      for (const elementSymbol of seriesElements) {
        const button = document.createElement("button");
        button.className = `pt-elem-btn${elementSymbol === S.addElement ? " selected" : ""}`;
        button.type = "button";
        button.textContent = elementSymbol;
        button.title = elementSymbol;
        button.dataset.element = elementSymbol;
        button.style.color = elemColor(elementSymbol);
        button.addEventListener("click", () => setSelectedAddElement(elementSymbol));
        rowElement.appendChild(button);
      }
      table.appendChild(rowElement);
      continue;
    }

    const row = buildPeriodicRow(rowEntries);
    for (const elementSymbol of row) {
      if (!elementSymbol) {
        const spacer = document.createElement("div");
        spacer.className = "pt-spacer";
        rowElement.appendChild(spacer);
        continue;
      }

      const button = document.createElement("button");
      button.className = `pt-elem-btn${elementSymbol === S.addElement ? " selected" : ""}`;
      button.type = "button";
      button.textContent = elementSymbol;
      button.title = elementSymbol;
      button.dataset.element = elementSymbol;
      button.style.color = elemColor(elementSymbol);
      button.addEventListener("click", () => setSelectedAddElement(elementSymbol));
      rowElement.appendChild(button);
    }

    table.appendChild(rowElement);
  }
}

function addAtomFromPanel() {
  const x = Number.parseFloat($("#add-x").value);
  const y = Number.parseFloat($("#add-y").value);
  const z = Number.parseFloat($("#add-z").value);
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z)) {
    showAddError("Coordinates must be valid numbers.");
    return;
  }

  const newId = S.atoms.length ? Math.max(...S.atoms.map((a) => a.id)) + 1 : 0;
  const beforeState = snapshotStructureState();
  addAtom({
    id: newId,
    symbol: S.addElement,
    x,
    y,
    z,
  }, beforeState);

  S.selected = new Set([newId]);
  S.hovered = null;
  clearAddError();
  setMode("translate");
}

// ── Box Select ──────────────────────────────────────────────────────────────

function onBoxStart(e) {
  setOrbitEnabled(false);
  const wrap = $("#viewer-wrap");
  const rect = wrap.getBoundingClientRect();
  S.boxStart = { x: e.clientX - rect.left, y: e.clientY - rect.top };

  const overlay = $("#box-select-overlay");
  overlay.style.left = `${S.boxStart.x}px`;
  overlay.style.top = `${S.boxStart.y}px`;
  overlay.style.width = "0px";
  overlay.style.height = "0px";
  overlay.style.display = "block";
}

function onBoxMove(e) {
  if (!S.boxStart) return;
  const wrap = $("#viewer-wrap");
  const rect = wrap.getBoundingClientRect();

  const cx = e.clientX - rect.left;
  const cy = e.clientY - rect.top;
  const x = Math.min(S.boxStart.x, cx);
  const y = Math.min(S.boxStart.y, cy);
  const w = Math.abs(cx - S.boxStart.x);
  const h = Math.abs(cy - S.boxStart.y);

  const o = $("#box-select-overlay");
  o.style.left = `${x}px`;
  o.style.top = `${y}px`;
  o.style.width = `${w}px`;
  o.style.height = `${h}px`;
}

function onBoxEnd(e) {
  if (!S.boxStart) return false;

  const wrap = $("#viewer-wrap");
  const rect = wrap.getBoundingClientRect();
  const ex = e.clientX - rect.left;
  const ey = e.clientY - rect.top;

  const dx = ex - S.boxStart.x;
  const dy = ey - S.boxStart.y;
  const clickThreshold = 4;
  const isClick = Math.abs(dx) < clickThreshold && Math.abs(dy) < clickThreshold;

  if (isClick) {
    S.boxStart = null;
    $("#box-select-overlay").style.display = "none";
    setOrbitEnabled(true);
    return false;
  }

  const x0 = ((Math.min(S.boxStart.x, ex) / rect.width) * 2) - 1;
  const y0 = -((Math.min(S.boxStart.y, ey) / rect.height) * 2) + 1;
  const x1 = ((Math.max(S.boxStart.x, ex) / rect.width) * 2) - 1;
  const y1 = -((Math.max(S.boxStart.y, ey) / rect.height) * 2) + 1;

  if (!e.shiftKey && !e.ctrlKey) S.selected.clear();

  const proj = new THREE.Vector3();
  for (const mesh of S.atomMeshes) {
    proj.copy(mesh.position).project(S.camera);
    if (proj.x >= x0 && proj.x <= x1 && proj.y <= y0 && proj.y >= y1) {
      S.selected.add(mesh.userData.atomId);
    }
  }

  S.boxStart = null;
  $("#box-select-overlay").style.display = "none";
  setOrbitEnabled(true);
  updateAtomVisuals();
  updateGizmo();
  updateStatusBar();
  return true;
}

// ── Canvas event wiring ─────────────────────────────────────────────────────

export function setupCanvasEvents() {
  const canvas = $("#struct-canvas");
  const hoverModes = new Set(["orbit", "delete", "translate", "rotate", "scale"]);
  let pendingHover = null;
  let hoverTickScheduled = false;
  let transientBoxSelectActive = false;
  let suppressNextSelectClick = false;
  let leftDownPos = null;
  let leftDragMoved = false;

  // In orbit / transform modes, Shift+left drag starts box selection.
  // Capture phase runs before OrbitControls' own listeners.
  canvas.addEventListener("mousedown", (e) => {
    if (e.button !== 0 || !e.shiftKey) return;
    if (S.mode !== "orbit" && !TRANSFORM_MODES.has(S.mode)) return;
    if (isGizmoActive()) return;       // don't hijack gizmo interaction
    setOrbitEnabled(false);
  }, true);

  const runHoverHitTest = () => {
    hoverTickScheduled = false;
    if (!pendingHover) return;

    const hoverEvt = pendingHover;
    pendingHover = null;

    const hit = raycastAtoms(hoverEvt);
    const newHover = hit ? atomIdFromMesh(hit.object) : null;
    if (newHover !== S.hovered) {
      S.hovered = newHover;
      updateAtomVisuals();
    }

    const pointerMode = hoverModes.has(S.mode);
    canvas.style.cursor = newHover !== null && pointerMode ? "pointer" : "default";
  };

  canvas.addEventListener("mousemove", (e) => {
    if ((e.buttons & 1) !== 0 && leftDownPos) {
      const dx = e.clientX - leftDownPos.x;
      const dy = e.clientY - leftDownPos.y;
      if ((dx * dx) + (dy * dy) > 9) leftDragMoved = true;
    }

    if (S.mode === "box" || transientBoxSelectActive) {
      onBoxMove(e);
      return;
    }

    if (!hoverModes.has(S.mode)) {
      if (S.hovered !== null) {
        S.hovered = null;
        updateAtomVisuals();
      }
      return;
    }

    // While dragging (button pressed), skip hover raycasts.
    if (e.buttons !== 0) return;

    pendingHover = { clientX: e.clientX, clientY: e.clientY };
    if (!hoverTickScheduled) {
      hoverTickScheduled = true;
      requestAnimationFrame(runHoverHitTest);
    }
  });

  canvas.addEventListener("mouseleave", () => {
    if (S.hovered !== null) {
      S.hovered = null;
      updateAtomVisuals();
    }
  });

  canvas.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    leftDownPos = { x: e.clientX, y: e.clientY };
    leftDragMoved = false;

    // Don't start box-select when interacting with the gizmo
    if (isGizmoActive()) return;

    if ((S.mode === "orbit" || TRANSFORM_MODES.has(S.mode)) && e.shiftKey) {
      transientBoxSelectActive = true;
      suppressNextSelectClick = false;
      onBoxStart(e);
      return;
    }

    if (S.mode === "box") onBoxStart(e);
  });

  canvas.addEventListener("mouseup", (e) => {
    if (e.button !== 0) return;

    if (transientBoxSelectActive) {
      const didBoxSelect = onBoxEnd(e);
      transientBoxSelectActive = false;
      suppressNextSelectClick = didBoxSelect;
      return;
    }

    if (S.mode === "box") onBoxEnd(e);
  });

  canvas.addEventListener("click", (e) => {
    // After a gizmo drag, suppress the click so we don't accidentally deselect.
    if (S.gizmoJustDragged) {
      S.gizmoJustDragged = false;
      leftDownPos = null;
      leftDragMoved = false;
      return;
    }

    // Orbit and transform modes share the same click-to-select behaviour.
    if (S.mode === "orbit" || TRANSFORM_MODES.has(S.mode)) {
      if (suppressNextSelectClick) {
        suppressNextSelectClick = false;
        leftDownPos = null;
        leftDragMoved = false;
        return;
      }
      if (leftDragMoved) {
        leftDownPos = null;
        leftDragMoved = false;
        return;
      }
      onSelectClick(e);
      leftDownPos = null;
      leftDragMoved = false;
      return;
    }

    if (S.mode === "delete") onDeleteClick(e);

    leftDownPos = null;
    leftDragMoved = false;
  });
}

// ── Mode switching & toolbar ────────────────────────────────────────────────

function openAddPanel() {
  buildAddPalette();
  clearAddError();
  setAddCoordinateInputs(computeAddDefaultPosition());
  $("#surface-panel").classList.remove("show");
  $("#supercell-panel").classList.remove("show");
  $("#add-panel").classList.add("show");
  $("#tb-add").classList.add("active");
}

function closeAddPanel() {
  $("#add-panel").classList.remove("show");
  $("#tb-add").classList.remove("active");
}

function toggleAddPanel() {
  if ($("#add-panel").classList.contains("show")) {
    closeAddPanel();
  } else {
    openAddPanel();
  }
}

function setMatrixInputs(prefix, matrix) {
  for (let i = 0; i < 3; i += 1) {
    for (let j = 0; j < 3; j += 1) {
      $("#" + prefix + i + j).value = Number(matrix[i][j]).toFixed(3);
    }
  }
}

function readMatrixInputs(prefix) {
  const m = [];
  for (let i = 0; i < 3; i += 1) {
    m[i] = [];
    for (let j = 0; j < 3; j += 1) {
      const v = parseFloat($("#" + prefix + i + j).value);
      if (Number.isNaN(v)) throw new Error("Matrix contains invalid numbers.");
      m[i][j] = v;
    }
  }
  return m;
}

function multiplyMatrices(a, b) {
  const out = [];
  for (let i = 0; i < 3; i += 1) {
    out[i] = [];
    for (let j = 0; j < 3; j += 1) {
      out[i][j] = 0;
      for (let k = 0; k < 3; k += 1) {
        out[i][j] += a[i][k] * b[k][j];
      }
    }
  }
  return out;
}

function setLatticeFromReal(realMatrix, scaleAtoms) {
  applyLattice(realMatrix, scaleAtoms);
}

function initializeLatticePanel() {
  setMatrixInputs("la-sm", [[1,0,0],[0,1,0],[0,0,1]]);
  if (Array.isArray(S.cell) && S.cell.length === 3) {
    setMatrixInputs("la-rm", S.cell);
  } else {
    setMatrixInputs("la-rm", [[1,0,0],[0,1,0],[0,0,1]]);
  }
  $("#la-scale-atoms").checked = true;
  $("#la-error").classList.remove("show");
}

export function setMode(mode) {
  S.mode = mode;
  $$(".tb-btn[data-mode]").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === mode && mode !== "");
  });

  // Orbit stays enabled in transform modes; gizmo disables it during drag.
  const orbitActive = mode === "orbit" || TRANSFORM_MODES.has(mode);
  setOrbitEnabled(orbitActive);
  updateAtomVisuals();
  updateGizmo();
  updateStatusBar();
  closeAddPanel();

  // Hide tool panels when switching modes
  $("#surface-panel").classList.remove("show");
  $("#supercell-panel").classList.remove("show");
  $("#lattice-panel").classList.remove("show");
}

export function wireToolbar() {
  document.querySelectorAll(".tb-btn[data-mode]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      if (mode) setMode(mode);
    });
  });

  $("#tb-add").addEventListener("click", () => {
    toggleAddPanel();
  });

  $("#tb-reset").addEventListener("click", () => {
    closeAddPanel();
    resetCamera();
  });
  $("#tb-save").addEventListener("click", () => {
    closeAddPanel();
    saveStructure();
  });
  $("#tb-delete").addEventListener("click", () => {
    if (S.mode === "delete") { deleteSelected(); updateGizmo(); }
    else setMode("delete");
  });

  // ── Surface builder panel ──
  $("#tb-surface").addEventListener("click", () => {
    const panel = $("#surface-panel");
    $("#supercell-panel").classList.remove("show");
    closeAddPanel();
    panel.classList.toggle("show");
    $("#sf-error").classList.remove("show");
  });

  $("#sf-cancel").addEventListener("click", () => {
    $("#surface-panel").classList.remove("show");
  });

  $("#sf-build").addEventListener("click", async () => {
    const errEl = $("#sf-error");
    errEl.classList.remove("show");

    if (!S.structPath) {
      errEl.textContent = "Load a structure first.";
      errEl.classList.add("show");
      return;
    }

    const h = parseInt($("#sf-h").value, 10);
    const k = parseInt($("#sf-k").value, 10);
    const l = parseInt($("#sf-l").value, 10);
    const layers = parseInt($("#sf-layers").value, 10);
    const vacuum = parseFloat($("#sf-vacuum").value);

    if ([h, k, l].some(v => isNaN(v))) {
      errEl.textContent = "Miller indices must be integers.";
      errEl.classList.add("show");
      return;
    }
    if (h === 0 && k === 0 && l === 0) {
      errEl.textContent = "Miller indices cannot all be zero.";
      errEl.classList.add("show");
      return;
    }

    const btn = $("#sf-build");
    btn.disabled = true;
    btn.textContent = "Building...";
    try {
      const result = await buildSurface([h, k, l], layers, vacuum);
      if (result.error) {
        errEl.textContent = result.error;
        errEl.classList.add("show");
      } else {
        $("#surface-panel").classList.remove("show");
      }
    } catch (e) {
      errEl.textContent = String(e);
      errEl.classList.add("show");
    } finally {
      btn.disabled = false;
      btn.textContent = "Build";
    }
  });

  // ── Supercell builder panel ──
  $("#tb-supercell").addEventListener("click", () => {
    const panel = $("#supercell-panel");
    $("#surface-panel").classList.remove("show");
    $("#lattice-panel").classList.remove("show");
    closeAddPanel();
    panel.classList.toggle("show");
    $("#sc-error").classList.remove("show");
  });

  $("#sc-cancel").addEventListener("click", () => {
    $("#supercell-panel").classList.remove("show");
  });

  // ── Lattice operations panel ──
  $("#tb-lattice").addEventListener("click", () => {
    const panel = $("#lattice-panel");
    $("#surface-panel").classList.remove("show");
    $("#supercell-panel").classList.remove("show");
    closeAddPanel();
    panel.classList.toggle("show");
    initializeLatticePanel();
  });

  $("#la-cancel").addEventListener("click", () => {
    $("#lattice-panel").classList.remove("show");
  });

  $("#la-update-real").addEventListener("click", () => {
    try {
      const scaleMat = readMatrixInputs("la-sm");
      const currentCell = Array.isArray(S.cell) && S.cell.length === 3 ? S.cell : [[1,0,0],[0,1,0],[0,0,1]];
      const newReal = multiplyMatrices(currentCell, scaleMat);
      setMatrixInputs("la-rm", newReal);
      $("#la-error").classList.remove("show");
    } catch (e) {
      const err = $("#la-error");
      err.textContent = String(e);
      err.classList.add("show");
    }
  });

  $("#la-apply").addEventListener("click", () => {
    try {
      const realMat = readMatrixInputs("la-rm");
      const scaleAtoms = $("#la-scale-atoms").checked;
      setLatticeFromReal(realMat, scaleAtoms);
      $("#lattice-panel").classList.remove("show");
    } catch (e) {
      const err = $("#la-error");
      err.textContent = String(e);
      err.classList.add("show");
    }
  });

  $("#sc-build").addEventListener("click", async () => {
    const errEl = $("#sc-error");
    errEl.classList.remove("show");

    if (!S.structPath) {
      errEl.textContent = "Load a structure first.";
      errEl.classList.add("show");
      return;
    }

    const ids = [
      ["sc-m00", "sc-m01", "sc-m02"],
      ["sc-m10", "sc-m11", "sc-m12"],
      ["sc-m20", "sc-m21", "sc-m22"],
    ];
    const matrix = ids.map((row) => row.map((id) => parseInt($("#" + id).value, 10)));

    if (matrix.flat().some((v) => isNaN(v))) {
      errEl.textContent = "All matrix entries must be integers.";
      errEl.classList.add("show");
      return;
    }

    const btn = $("#sc-build");
    btn.disabled = true;
    btn.textContent = "Building...";
    try {
      const result = await buildSupercell(matrix);
      if (result.error) {
        errEl.textContent = result.error;
        errEl.classList.add("show");
      } else {
        $("#supercell-panel").classList.remove("show");
      }
    } catch (e) {
      errEl.textContent = String(e);
      errEl.classList.add("show");
    } finally {
      btn.disabled = false;
      btn.textContent = "Build";
    }
  });

  // ── Add atom panel ──
  $("#add-cancel").addEventListener("click", () => {
    closeAddPanel();
  });

  $("#add-build").addEventListener("click", () => {
    addAtomFromPanel();
  });
}

// ── Keyboard shortcuts ──────────────────────────────────────────────────────

export function wireKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") return;

    if (e.ctrlKey || e.metaKey) {
      const key = e.key.toLowerCase();

      if (key === "z" && !e.shiftKey) {
        e.preventDefault();
        if (undoStructureEdit()) updateGizmo();
        return;
      }

      if (key === "y" || (key === "z" && e.shiftKey)) {
        e.preventDefault();
        if (redoStructureEdit()) updateGizmo();
        return;
      }
    }

    // ── Fine adjustment (WASD + arrows) when in a transform mode with selection ──
    if (TRANSFORM_MODES.has(S.mode) && S.selected.size > 0) {
      let dir = null;
      if (e.key === "ArrowUp" || e.key.toLowerCase() === "w")                              dir = "up";
      else if (e.key === "ArrowDown" || e.key.toLowerCase() === "s")                        dir = "down";
      else if (e.key === "ArrowLeft" || (e.key.toLowerCase() === "a" && !e.ctrlKey && !e.metaKey)) dir = "left";
      else if (e.key === "ArrowRight" || e.key.toLowerCase() === "d")                       dir = "right";

      if (dir) { e.preventDefault(); nudgeTransform(dir); return; }
    }

    // ── Mode switches ──
    if (e.key === "1") { setMode("orbit"); return; }
    if (e.key === "2") { setMode("box"); return; }
    if (e.key === "5") { toggleAddPanel(); return; }
    if (e.key === "6") { setMode("delete"); return; }

    if (!e.ctrlKey && !e.metaKey) {
      if (e.key.toLowerCase() === "t") { setMode("translate"); return; }
      if (e.key.toLowerCase() === "r") { setMode("rotate"); return; }
    }
      if (e.key.toLowerCase() === "e") { setMode("scale"); return; }

    // ── View direction ──
    if (e.key.toLowerCase() === "x") { setViewDirection("x"); return; }
    if (e.key.toLowerCase() === "y") { setViewDirection("y"); return; }
    if (e.key.toLowerCase() === "z") { setViewDirection("z"); return; }

    // ── Delete / Escape / Save / Select-all ──
    if (e.key === "Delete" || e.key === "Backspace") {
      deleteSelected();
      updateGizmo();
      return;
    }
    if (e.key === "Escape") {
      S.selected.clear();
      updateAtomVisuals();
      updateGizmo();
      updateStatusBar();
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
      e.preventDefault();
      saveStructure();
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "a") {
      e.preventDefault();
      S.selected = new Set(S.atoms.map((a) => a.id));
      updateAtomVisuals();
      updateGizmo();
      updateStatusBar();
    }
  });
}
