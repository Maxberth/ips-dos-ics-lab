"""Estilo común de las figuras del paper (LNCS: ancho de texto 12,2 cm = 4,8 in).

Se diseña a tamaño final (4,8 in de ancho, fuentes de 6,5–8 pt) para que al insertar la figura con
\\includegraphics[width=\\textwidth] la letra no se reduzca. Paleta apta para daltonismo (Okabe-Ito); además de color,
cada escenario usa un marcador distinto para que se distinga en blanco y negro.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

W = 4.8  # in, ancho de texto de llncs
COL = {"E0": "#555555", "E1": "#0072B2", "E2": "#E69F00", "E3": "#D55E00"}
MARK = {"E0": "s", "E1": "o", "E2": "^", "E3": "D"}

def aplicar():
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300, "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
        "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": .6,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25, "grid.linewidth": .4,
        "lines.linewidth": 1.0, "font.family": "DejaVu Sans", "pdf.fonttype": 42, "svg.fonttype": "none"})

def guardar(fig, dest, nombre):
    os.makedirs(dest, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(f"{dest}/{nombre}.{ext}")
    plt.close(fig)
