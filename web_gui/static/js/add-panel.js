/**
 * add-panel.js – Add atom panel with periodic table element picker.
 */

import { S } from "./state.js";
import { $, $$, showError, clearError } from "./utils.js";
import { elemColor } from "./viewer.js";
import { addAtom, snapshotStructureState, LAYERS_CHANGED_EVENT } from "./structure.js";
import { setMode } from "./editor.js";
import { closeAllPanels } from "./panel-core.js";
import { PERIODIC_TABLE_ROWS } from "./elements.js";

/* ── Periodic table helpers ──────────────────────────────────────────────── */

function buildPeriodicRow(entries) {
  const row = Array(18).fill(null);
  for (const [columnIndex, elementSymbol] of entries) {
    row[columnIndex - 1] = elementSymbol;
  }
  return row;
}

function setSelectedAddElement(elementSymbol) {
  S.addElement = elementSymbol;
  $$(".pt-elem-btn").forEach((button) => {
    button.classList.toggle("selected", button.dataset.element === elementSymbol);
  });
}

function createElementButton(elementSymbol) {
  const button = document.createElement("button");
  button.className = `pt-elem-btn${elementSymbol === S.addElement ? " selected" : ""}`;
  button.type = "button";
  button.textContent = elementSymbol;
  button.title = elementSymbol;
  button.dataset.element = elementSymbol;
  button.style.color = elemColor(elementSymbol);
  button.addEventListener("click", () => setSelectedAddElement(elementSymbol));
  return button;
}

function buildAddPalette() {
  const table = $("#add-periodic-table");
  table.innerHTML = "";

  for (let rowIndex = 0; rowIndex < PERIODIC_TABLE_ROWS.length; rowIndex += 1) {
    const rowEntries = PERIODIC_TABLE_ROWS[rowIndex];
    const rowElement = document.createElement("div");
    rowElement.className = "pt-row";

    if (rowIndex >= 7) {
      rowElement.classList.add("pt-row-series");
      if (rowIndex === 7) rowElement.classList.add("pt-row-series-start");

      const seriesElements = [...rowEntries]
        .sort((left, right) => left[0] - right[0])
        .map((entry) => entry[1]);

      for (const elementSymbol of seriesElements) {
        rowElement.appendChild(createElementButton(elementSymbol));
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
      rowElement.appendChild(createElementButton(elementSymbol));
    }

    table.appendChild(rowElement);
  }
}

/* ── Default position ────────────────────────────────────────────────────── */

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

  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

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

/* ── Open / toggle / add ─────────────────────────────────────────────────── */

function openAddPanel() {
  closeAllPanels();
  buildAddPalette();
  clearError("#add-error");
  const pos = computeAddDefaultPosition();
  $("#add-x").value = pos.x.toFixed(3);
  $("#add-y").value = pos.y.toFixed(3);
  $("#add-z").value = pos.z.toFixed(3);
  $("#add-panel").classList.add("show");
  $("#tb-add").classList.add("active");
}

export function toggleAddPanel() {
  if ($("#add-panel").classList.contains("show")) {
    closeAllPanels();
  } else {
    openAddPanel();
  }
}

function addAtomFromPanel() {
  const x = Number.parseFloat($("#add-x").value);
  const y = Number.parseFloat($("#add-y").value);
  const z = Number.parseFloat($("#add-z").value);
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(z)) {
    showError("#add-error", "Coordinates must be valid numbers.");
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
  document.dispatchEvent(new CustomEvent(LAYERS_CHANGED_EVENT));
  clearError("#add-error");
  setMode("translate");
}

/* ── Wiring ──────────────────────────────────────────────────────────────── */

export function wireAddPanel() {
  $("#tb-add").addEventListener("click", toggleAddPanel);
  $("#add-cancel").addEventListener("click", () => closeAllPanels());
  $("#add-build").addEventListener("click", addAtomFromPanel);
}
