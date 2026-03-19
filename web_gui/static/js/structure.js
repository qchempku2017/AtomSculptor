/**
 * structure.js – Structure data operations: load, save, format detection.
 */

import {
  S,
  STRUCTURE_EXTS,
  STRUCTURE_PREFIXES,
  MODE_HINT,
  MAX_UNDO_ENTRIES,
} from "./state.js";
import { $ } from "./utils.js";
import { rebuildScene, resetCamera } from "./viewer.js";

function cloneAtoms(atoms) {
  return atoms.map((atom) => ({ ...atom }));
}

function cloneCell(cell) {
  return Array.isArray(cell) ? cell.map((vec) => [...vec]) : null;
}

function clonePbc(pbc) {
  return Array.isArray(pbc) ? [...pbc] : [false, false, false];
}

function atomListsEqual(left, right) {
  if (left.length !== right.length) return false;
  for (let i = 0; i < left.length; i += 1) {
    const a = left[i];
    const b = right[i];
    if (
      a.id !== b.id
      || a.symbol !== b.symbol
      || a.x !== b.x
      || a.y !== b.y
      || a.z !== b.z
    ) {
      return false;
    }
  }
  return true;
}

function matrixListsEqual(left, right) {
  if (left === right) return true;
  if (!Array.isArray(left) || !Array.isArray(right)) return false;
  if (left.length !== right.length) return false;
  for (let i = 0; i < left.length; i += 1) {
    const lv = left[i];
    const rv = right[i];
    if (!Array.isArray(lv) || !Array.isArray(rv) || lv.length !== rv.length) return false;
    for (let j = 0; j < lv.length; j += 1) {
      if (lv[j] !== rv[j]) return false;
    }
  }
  return true;
}

function arraysEqual(left, right) {
  if (left === right) return true;
  if (!Array.isArray(left) || !Array.isArray(right)) return false;
  if (left.length !== right.length) return false;
  for (let i = 0; i < left.length; i += 1) {
    if (left[i] !== right[i]) return false;
  }
  return true;
}

function structureStatesEqual(left, right) {
  return (
    atomListsEqual(left.atoms, right.atoms)
    && matrixListsEqual(left.cell, right.cell)
    && arraysEqual(left.pbc, right.pbc)
    && arraysEqual(left.selected, right.selected)
  );
}

function normalizeSelection(selected) {
  const atomIds = new Set(S.atoms.map((atom) => atom.id));
  return new Set(selected.filter((id) => atomIds.has(id)));
}

function applyStructureState(state) {
  S.atoms = cloneAtoms(state.atoms);
  S.cell = cloneCell(state.cell);
  S.pbc = clonePbc(state.pbc);
  S.selected = normalizeSelection(state.selected);
  S.hovered = null;
  rebuildScene();
  updateStatusBar();
}

function pushUndoState(state) {
  S.undoStack.push(state);
  if (S.undoStack.length > MAX_UNDO_ENTRIES) S.undoStack.shift();
}

export function snapshotStructureState() {
  return {
    atoms: cloneAtoms(S.atoms),
    cell: cloneCell(S.cell),
    pbc: clonePbc(S.pbc),
    selected: [...S.selected].sort((left, right) => left - right),
  };
}

export function resetStructureHistory() {
  S.undoStack = [];
  S.redoStack = [];
}

export function recordStructureEdit(beforeState) {
  if (!beforeState) return false;
  const afterState = snapshotStructureState();
  if (structureStatesEqual(beforeState, afterState)) return false;
  pushUndoState(beforeState);
  S.redoStack = [];
  return true;
}

export function undoStructureEdit() {
  const previous = S.undoStack.pop();
  if (!previous) return false;
  S.redoStack.push(snapshotStructureState());
  applyStructureState(previous);
  return true;
}

export function redoStructureEdit() {
  const next = S.redoStack.pop();
  if (!next) return false;
  pushUndoState(snapshotStructureState());
  applyStructureState(next);
  return true;
}

function deleteAtomsByIds(ids, beforeState = null) {
  const toDelete = new Set(ids);
  if (!toDelete.size) return false;

  const existingIds = new Set(S.atoms.map((atom) => atom.id));
  const deletableIds = [...toDelete].filter((id) => existingIds.has(id));
  if (!deletableIds.length) return false;

  const snapshot = beforeState || snapshotStructureState();
  const deletedIdSet = new Set(deletableIds);
  S.atoms = S.atoms.filter((atom) => !deletedIdSet.has(atom.id));
  S.selected = new Set([...S.selected].filter((id) => !deletedIdSet.has(id)));
  if (S.hovered !== null && deletedIdSet.has(S.hovered)) S.hovered = null;
  rebuildScene();
  updateStatusBar();
  recordStructureEdit(snapshot);
  return true;
}

export function isStructureFilename(name) {
  const base = String(name).split("/").pop().toLowerCase();
  const ext = base.includes(".") ? base.split(".").pop() : "";
  if (STRUCTURE_EXTS.has(ext)) return true;
  return STRUCTURE_PREFIXES.some((prefix) => (
    base === prefix
    || base.startsWith(`${prefix}_`)
    || base.startsWith(`${prefix}-`)
    || base.startsWith(`${prefix}.`)
  ));
}

export function updateStatusBar() {
  $("#sb-mode").textContent = `Mode: ${S.mode.charAt(0).toUpperCase()}${S.mode.slice(1)}`;
  $("#sb-natoms").textContent = `${S.atoms.length} atoms`;
  $("#sb-sel").textContent = S.selected.size ? `${S.selected.size} selected` : "";
  $("#sb-hint").textContent = MODE_HINT[S.mode] || "";
}

export async function loadStructure(path) {
  try {
    const resp = await fetch(`/api/structure?path=${encodeURIComponent(path)}`);
    const data = await resp.json();
    if (data.error) {
      console.error(data.error);
      return;
    }

    S.structPath = path;
    S.atoms = data.atoms;
    S.cell = data.cell;
    S.pbc = data.pbc;
    S.selected = new Set();
    S.hovered = null;
    resetStructureHistory();
    rebuildScene();
    $("#struct-file-label").textContent = data.path;
    $("#viewer-empty").style.display = "none";
    resetCamera();
    updateStatusBar();
  } catch (e) {
    console.error("loadStructure", e);
  }
}

export async function saveStructure() {
  if (!S.structPath) {
    alert("No structure loaded.");
    return;
  }

  try {
    const resp = await fetch("/api/structure/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: S.structPath, atoms: S.atoms, cell: S.cell, pbc: S.pbc }),
    });
    const data = await resp.json();

    if (data.ok) {
      const sb = $("#struct-statusbar");
      const orig = sb.style.borderTop;
      sb.style.borderTop = "1px solid var(--s-done)";
      setTimeout(() => {
        sb.style.borderTop = orig;
      }, 1500);
    } else {
      alert(`Save failed: ${data.error || "unknown"}`);
    }
  } catch (e) {
    alert(`Save error: ${e}`);
  }
}

export function deleteAtomById(id) {
  deleteAtomsByIds([id]);
}

export function deleteSelected() {
  deleteAtomsByIds([...S.selected]);
}

export function addAtom(atom, beforeState = null) {
  const snapshot = beforeState || snapshotStructureState();
  S.atoms.push({ ...atom });
  rebuildScene();
  updateStatusBar();
  recordStructureEdit(snapshot);
}

// ── Structure building tools ────────────────────────────────────────────────

function applyBuiltStructure(data) {
  S.structPath = data.path;
  S.atoms = data.atoms;
  S.cell = data.cell;
  S.pbc = data.pbc;
  S.selected = new Set();
  S.hovered = null;
  resetStructureHistory();
  rebuildScene();
  $("#struct-file-label").textContent = data.path;
  $("#viewer-empty").style.display = "none";
  resetCamera();
  updateStatusBar();
}

async function parseJsonResponseSafe(resp) {
  const text = await resp.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (data && typeof data === "object") {
    return data;
  }

  if (!resp.ok) {
    return { error: `HTTP ${resp.status}: ${text || resp.statusText}` };
  }

  return { error: "Server returned an unexpected response." };
}

export async function buildSurface(millerIndices, layers, vacuum) {
  if (!S.structPath) return { error: "No structure loaded." };

  const resp = await fetch("/api/structure/build-surface", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path: S.structPath,
      miller_indices: millerIndices,
      layers,
      vacuum,
    }),
  });
  const data = await parseJsonResponseSafe(resp);
  if (data.error) return data;
  applyBuiltStructure(data);
  return data;
}

export async function buildSupercell(matrix) {
  if (!S.structPath) return { error: "No structure loaded." };

  const resp = await fetch("/api/structure/build-supercell", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path: S.structPath,
      matrix,
    }),
  });
  const data = await parseJsonResponseSafe(resp);
  if (data.error) return data;
  applyBuiltStructure(data);
  return data;
}
