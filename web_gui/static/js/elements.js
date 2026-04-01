/**
 * elements.js – Periodic table layout data.
 *
 * Each row is an array of [column, symbol] pairs where column is the
 * 1-based position in the standard 18-column periodic table grid.
 */

export const PERIODIC_TABLE_ROWS = [
  [[1, "H"], [18, "He"]],
  [[1, "Li"], [2, "Be"], [13, "B"], [14, "C"], [15, "N"], [16, "O"], [17, "F"], [18, "Ne"]],
  [[1, "Na"], [2, "Mg"], [13, "Al"], [14, "Si"], [15, "P"], [16, "S"], [17, "Cl"], [18, "Ar"]],
  [[1, "K"], [2, "Ca"], [3, "Sc"], [4, "Ti"], [5, "V"], [6, "Cr"], [7, "Mn"], [8, "Fe"], [9, "Co"], [10, "Ni"], [11, "Cu"], [12, "Zn"], [13, "Ga"], [14, "Ge"], [15, "As"], [16, "Se"], [17, "Br"], [18, "Kr"]],
  [[1, "Rb"], [2, "Sr"], [3, "Y"], [4, "Zr"], [5, "Nb"], [6, "Mo"], [7, "Tc"], [8, "Ru"], [9, "Rh"], [10, "Pd"], [11, "Ag"], [12, "Cd"], [13, "In"], [14, "Sn"], [15, "Sb"], [16, "Te"], [17, "I"], [18, "Xe"]],
  [[1, "Cs"], [2, "Ba"], [4, "Hf"], [5, "Ta"], [6, "W"], [7, "Re"], [8, "Os"], [9, "Ir"], [10, "Pt"], [11, "Au"], [12, "Hg"], [13, "Tl"], [14, "Pb"], [15, "Bi"], [16, "Po"], [17, "At"], [18, "Rn"]],
  [[1, "Fr"], [2, "Ra"], [4, "Rf"], [5, "Db"], [6, "Sg"], [7, "Bh"], [8, "Hs"], [9, "Mt"], [10, "Ds"], [11, "Rg"], [12, "Cn"], [13, "Nh"], [14, "Fl"], [15, "Mc"], [16, "Lv"], [17, "Ts"], [18, "Og"]],
  [[3, "La"], [4, "Ce"], [5, "Pr"], [6, "Nd"], [7, "Pm"], [8, "Sm"], [9, "Eu"], [10, "Gd"], [11, "Tb"], [12, "Dy"], [13, "Ho"], [14, "Er"], [15, "Tm"], [16, "Yb"], [17, "Lu"]],
  [[3, "Ac"], [4, "Th"], [5, "Pa"], [6, "U"], [7, "Np"], [8, "Pu"], [9, "Am"], [10, "Cm"], [11, "Bk"], [12, "Cf"], [13, "Es"], [14, "Fm"], [15, "Md"], [16, "No"], [17, "Lr"]],
];

export function buildPeriodicRow(entries) {
  const row = Array(18).fill(null);
  for (const [columnIndex, elementSymbol] of entries) {
    row[columnIndex - 1] = elementSymbol;
  }
  return row;
}

