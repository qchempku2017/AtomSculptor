/**
 * state.js – Global application state and constants.
 */

export const S = {
  ws: null,
  cy: null,
  connected: false,
  processing: false,
  aggregatorStatus: null,
  todoData: { tasks: [], finished: true },

    currentSessionId: null,
    sessions: [],

  renderer: null,
  scene: null,
  camera: null,
  cameraMode: "perspective",
  controls: null,
  rafId: null,

  structPath: null,
  atoms: [],
  layers: [],
  selectedLayerIds: new Set(),
  layerSeq: 0,
  cell: null,
  pbc: [false, false, false],
  undoStack: [],
  redoStack: [],

  atomMeshes: [],
  bondMeshes: [],
  cellLines: null,

  mode: "orbit",
  selected: new Set(),
  hovered: null,
  addElement: "H",

  gizmoJustDragged: false,

  boxStart: null,
  // Controls visibility of the temporary selection overlay layer
  selectionLayerHidden: false,
};

export const STRUCTURE_EXTS = new Set([
  "cif", "xyz", "vasp", "poscar", "extxyz", "pdb", "sdf", "mol2", "lxyz",
]);
export const STRUCTURE_PREFIXES = ["poscar", "contcar"];

export const MAX_UNDO_ENTRIES = 100;

export const STATUS_COLOR = {
  pending: "#858585",
  ready: "#4fc3f7",
  in_progress: "#ffb74d",
  done: "#81c784",
  blocked: "#e57373",
  deprecated: "#616161",
};

export const ELEM_COLOR = {
  H: "#ffffff", He: "#d9ffff", Li: "#cc80ff", Be: "#bfe1a3", B: "#ffb5b5",
  C: "#404040", N: "#3050f8", O: "#ff0d0d", F: "#90e050", Ne: "#b3e3f5",
  Na: "#ab5cf2", Mg: "#8aff00", Al: "#bfa6a6", Si: "#f0c8a0", P: "#ff8000",
  S: "#ffff30", Cl: "#1ff01f", Ar: "#80d1e3", K: "#8f40d4", Ca: "#3dff00",
  Sc: "#6699ff", Ti: "#bfc2c7", V: "#a6a6ff", Cr: "#8a99c7", Mn: "#9c7ac7",
  Fe: "#e06633", Co: "#f090a0", Ni: "#50d050", Cu: "#c88033", Zn: "#7d80b0",
  Ga: "#c28f8f", Ge: "#668f8f", As: "#9e4fb5", Se: "#ffa100", Br: "#a62929",
  Kr: "#5cb8d1", Rb: "#702eb0", Sr: "#00e676", Y: "#94ffff", Zr: "#94e0e0",
  Nb: "#73c2c9", Mo: "#54b5b5", Ru: "#2f6f6f", Rh: "#c3c3c3", Pd: "#006985",
  Ag: "#c0c0c0", Cd: "#ffd700", In: "#a67573", Sn: "#668080", Sb: "#9e63b5",
  Te: "#d47a00", I: "#940094", Xe: "#429eb0", Cs: "#57178f", Ba: "#00c900",
  La: "#70d4ff", Ce: "#ffffc7", Nd: "#c2ffbd", Sm: "#ffd2a6", Eu: "#ffc0cb",
  Gd: "#aaffc3", Tb: "#d3cfff", Dy: "#ffdfba", Ho: "#ffd4b6", Er: "#b0e0e6",
  Tm: "#c6d7ff", Yb: "#ffd1dc", Lu: "#d0d0ff", Hf: "#4dc2ff", Ta: "#4da6ff",
  W: "#3399ff", Re: "#267f99", Os: "#266f7a", Ir: "#175487", Pt: "#d0d0e0",
  Au: "#ffd123", Hg: "#b8b8d0", Tl: "#a6544d", Pb: "#575961", Bi: "#9c5cb3",
  default: "#ff1493",
};

// van der Waals radii (Å) used for bond detection
export const ELEM_VDW = {
  H: 1.20, He: 1.40, Li: 1.82, Be: 1.53, B: 1.92,
  C: 1.70, N: 1.55, O: 1.52, F: 1.47, Ne: 1.54,
  Na: 2.27, Mg: 1.73, Al: 1.84, Si: 2.10, P: 1.80,
  S: 1.80, Cl: 1.75, Ar: 1.88, K: 2.75, Ca: 2.31,
  Sc: 2.11, Ti: 2.00, V: 2.00, Cr: 2.00, Mn: 2.00,
  Fe: 2.00, Co: 2.00, Ni: 1.63, Cu: 1.40, Zn: 1.39,
  Ga: 1.87, Ge: 2.11, As: 1.85, Se: 1.90, Br: 1.85,
  Kr: 2.02, Rb: 3.03, Sr: 2.49, Y: 2.00, Zr: 2.16,
  Nb: 2.07, Mo: 2.10, Ru: 2.05, Rh: 2.00, Pd: 2.05,
  Ag: 1.72, Cd: 1.58, In: 1.93, Sn: 2.17, Sb: 2.06,
  Te: 2.06, I: 1.98, Xe: 2.16, Cs: 3.43, Ba: 2.68,
  La: 2.07, Ce: 2.04, Nd: 2.01, Sm: 2.06, Eu: 2.00,
  Gd: 1.95, Tb: 1.90, Dy: 1.88, Ho: 1.87, Er: 1.88,
  Tm: 1.90, Yb: 1.94, Lu: 1.87, Hf: 2.16, Ta: 2.15,
  W: 2.10, Re: 2.05, Os: 2.00, Ir: 2.00, Pt: 2.05,
  Au: 1.66, Hg: 1.55, Tl: 1.96, Pb: 2.02, Bi: 2.07,
  default: 1.80,
};

export const ELEM_RADIUS = {
  H: 0.31, C: 0.77, N: 0.75, O: 0.73, F: 0.71,
  P: 1.06, S: 1.02, Cl: 0.99, Br: 1.14, I: 1.33,
  Li: 1.28, Na: 1.66, K: 2.03, Ca: 1.74, Mg: 1.41,
  Al: 1.21, Si: 1.17, Fe: 1.25, Cu: 1.28, Zn: 1.22,
  Ag: 1.44, Au: 1.44, Pt: 1.39, Pd: 1.31, Ti: 1.47,
  Co: 1.25, Ni: 1.24, Mn: 1.29, Cr: 1.29,
  He: 0.28, Ne: 0.58, Ar: 1.06, Xe: 1.31, Kr: 1.16,
  default: 1.2,
};

// Bond tolerance: bond drawn when dist < (rCov_A + rCov_B) * BOND_TOLERANCE
export const BOND_TOLERANCE = 1.2;

// Use 60% of the sum of van der Waals radii to detect bonds (VMD/VMD convention)
export const VDW_BOND_FACTOR = 0.6;

export const MODE_HINT = {
  orbit: "Drag to rotate · Scroll to zoom · Right-drag to pan · Click atom to select",
  box: "Drag box to select · Shift/Ctrl to add to selection",
  translate: "Select atoms then drag gizmo axes · Arrows/WASD to nudge 0.1 Å",
  rotate: "Select atoms then drag gizmo rings · Arrows/WASD to nudge 1°",
  scale: "Select atoms then drag gizmo handles · Arrows/WASD to nudge",
  add: "Pick element and coordinates in the Add Atom panel",
  delete: "Click atom to delete",
};
