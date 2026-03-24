/**
 * layers.js – Layer panel UI for lattice + atom layers.
 */

import { S } from "./state.js";
import { $, esc } from "./utils.js";
import {
  LAYERS_CHANGED_EVENT,
  addAtomsLayer,
  appendStructureToLayer,
  deleteSelectedAtomLayers,
  mergeSelectedAtomLayers,
  setSelectedAtomLayers,
  toggleLayerVisibility,
  toggleSelectionLayerVisibility,
  extractSelectedToNewLayer,
  useLatticeFromLayer,
} from "./structure.js";

function layerLabel(layer) {
  if (layer.type === "lattice") return "Lattice";
  const count = S.atoms.filter((atom) => atom.layerId === layer.id).length;
  return `${layer.name} (${count})`;
}

function updateActionState() {
  const selectedCount = [...S.selectedLayerIds].length;
  $("#btn-merge-layer").disabled = selectedCount < 2;
  $("#btn-del-layer").disabled = selectedCount < 1;
}

function renderLayerList() {
  const list = $("#layer-list");
  const empty = $("#layer-empty");
  list.innerHTML = "";

  // Render temporary selection overlay row when atoms are selected
  if (S.selected && S.selected.size > 0) {
    const selCount = S.selected.size;
    const row = document.createElement("div");
    row.className = `layer-item selection`;
    if (S.selectionLayerHidden) row.classList.add("layer-hidden");
    const icon = "◉";
    const meta = "selection";
    const eyeVisible = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    const eyeHidden = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
    const visBtn = `<button type='button' class='li-vis' title='${S.selectionLayerHidden ? "Show selection" : "Hide selection"}'>${S.selectionLayerHidden ? eyeHidden : eyeVisible}</button>`;
    // Use the same visual style as the 'Use lattice' action button
    const actionHtml = `<span class='li-actions'><button type='button' class='li-use-lattice li-extract' title='Extract selection to new layer'>Extract</button></span>`;
    row.innerHTML = `<span class='li-icon'>${icon}</span>${visBtn}<span class='li-name'>Selection (${selCount})</span><span class='li-meta'>${esc(meta)}</span>${actionHtml}`;

    row.querySelector(".li-vis")?.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleSelectionLayerVisibility();
    });

    row.querySelector(".li-extract")?.addEventListener("click", (event) => {
      event.stopPropagation();
      const result = extractSelectedToNewLayer();
      if (!result.ok) alert(result.error || "Extract failed");
    });

    list.appendChild(row);
  }

  if (!Array.isArray(S.layers) || !S.layers.length) {
    empty.style.display = "block";
    updateActionState();
    return;
  }
  empty.style.display = "none";

  for (const layer of S.layers) {
    const row = document.createElement("div");
    row.className = `layer-item ${layer.type === "lattice" ? "lattice" : "atoms"}`;
    if (layer.type === "atoms" && S.selectedLayerIds.has(layer.id)) {
      row.classList.add("selected");
    }
    if (layer.type === "atoms" && layer.hidden) {
      row.classList.add("layer-hidden");
    }

    const icon = layer.type === "lattice" ? "▦" : "●";
    const meta = layer.type === "lattice" ? "base" : layer.id;
    const eyeVisible = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    const eyeHidden = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
    const visBtn = layer.type === "atoms"
      ? `<button type='button' class='li-vis' title='${layer.hidden ? "Show layer" : "Hide layer"}'>${layer.hidden ? eyeHidden : eyeVisible}</button>`
      : "";
    const actionHtml = layer.type === "atoms"
      ? `<span class='li-actions'><button type='button' class='li-use-lattice' title='Apply this layer lattice metadata to base lattice'>Use lattice</button></span>`
      : "";
    row.innerHTML = `<span class='li-icon'>${icon}</span>${visBtn}<span class='li-name'>${esc(layerLabel(layer))}</span><span class='li-meta'>${esc(meta)}</span>${actionHtml}`;

    if (layer.type === "atoms") {
      row.querySelector(".li-vis")?.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleLayerVisibility(layer.id);
      });

      row.querySelector(".li-use-lattice")?.addEventListener("click", (event) => {
        event.stopPropagation();
        const result = useLatticeFromLayer(layer.id);
        if (!result.ok) {
          alert(result.error);
        }
      });

      row.addEventListener("click", (event) => {
        if (event.shiftKey) {
          const next = new Set(S.selectedLayerIds);
          if (next.has(layer.id)) next.delete(layer.id);
          else next.add(layer.id);
          setSelectedAtomLayers([...next]);
          return;
        }
        setSelectedAtomLayers([layer.id]);
      });

      row.addEventListener("dragover", (event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = "copy";
        row.classList.add("drop-target");
      });

      row.addEventListener("dragleave", () => {
        row.classList.remove("drop-target");
      });

      row.addEventListener("drop", async (event) => {
        event.preventDefault();
        row.classList.remove("drop-target");
        const path = event.dataTransfer.getData("application/x-atomsculptor-structure-path")
          || event.dataTransfer.getData("text/plain");
        if (!path) return;

        const result = await appendStructureToLayer(path, layer.id);
        if (!result.ok) {
          alert(`Layer import failed: ${result.error || "unknown"}`);
        }
      });
    }

    list.appendChild(row);
  }

  updateActionState();
}

export function initLayersPanel() {
  document.addEventListener(LAYERS_CHANGED_EVENT, renderLayerList);

  const dropHost = $("#layers-body");
  dropHost.addEventListener("dragover", (event) => {
    const hasStructure = event.dataTransfer.types.includes("application/x-atomsculptor-structure-path")
      || event.dataTransfer.types.includes("text/plain");
    if (!hasStructure) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
  });

  dropHost.addEventListener("drop", async (event) => {
    // Row-level handlers own in-row drops; this is for empty panel space.
    if (event.target.closest(".layer-item.atoms")) return;
    const path = event.dataTransfer.getData("application/x-atomsculptor-structure-path")
      || event.dataTransfer.getData("text/plain");
    if (!path) return;

    event.preventDefault();
    const layerId = addAtomsLayer();
    const result = await appendStructureToLayer(path, layerId);
    if (!result.ok) {
      alert(`Layer import failed: ${result.error || "unknown"}`);
    }
  });

  $("#btn-add-layer").addEventListener("click", () => {
    addAtomsLayer();
  });

  $("#btn-del-layer").addEventListener("click", () => {
    const result = deleteSelectedAtomLayers();
    if (!result.ok) {
      alert(result.error);
    }
  });

  $("#btn-merge-layer").addEventListener("click", () => {
    const result = mergeSelectedAtomLayers();
    if (!result.ok) {
      alert(result.error);
    }
  });

  renderLayerList();
}
