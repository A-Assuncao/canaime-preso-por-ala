"""
Diálogo para escolher alas da chamada (Bloco A e Bloco B apenas), antes do login.
"""

import tkinter as tk
from tkinter import messagebox

from config.units_config import UNITS_CONFIG

UNIT_KEY = "PAMC"
# Chamada: somente estes blocos (ordem fixa)
CHAMADA_BLOCK_KEYS = ("A", "B")
# Colunas de checkboxes por bloco para caber sem rolagem
ALA_GRID_COLUMNS = 3

FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_HINT = ("Segoe UI", 11)
FONT_BLOCK = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN_MAIN = ("Segoe UI", 11, "bold")
FONT_BTN_SEC = ("Segoe UI", 11)


def _fit_toplevel_to_content(window, margin_x=36, margin_y=36, min_w=520, min_h=380):
    """Ajusta geometria ao conteúdo; limita à área útil do monitor."""
    window.update_idletasks()
    req_w = window.winfo_reqwidth()
    req_h = window.winfo_reqheight()
    w = max(min_w, req_w + margin_x)
    h = max(min_h, req_h + margin_y)
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    w = min(w, sw - 48)
    h = min(h, sh - 48)
    window.geometry(f"{int(w)}x{int(h)}")


def _sort_ala_keys(keys):
    """Ordena chaves de alas de forma estável (numérico quando possível)."""

    def key_fn(k):
        try:
            return (0, int(k))
        except ValueError:
            return (1, k)

    return sorted(keys, key=key_fn)


def prompt_chamada_alas(parent):
    """
    Exibe seleção de alas por bloco (apenas A e B). Todas as alas iniciam marcadas.

    Returns:
        Lista de tuplas (bloco_id, ala_id), ex.: [("A", "12"), ("B", "01")].
        None se o usuário cancelar.
    """
    pamc = UNITS_CONFIG.get(UNIT_KEY, {})
    blocks = pamc.get("blocks") or {}

    blocks_to_show = []
    for bk in CHAMADA_BLOCK_KEYS:
        if bk in blocks:
            blocks_to_show.append((bk, blocks[bk]))

    if not blocks_to_show:
        messagebox.showerror(
            "Configuração",
            "Blocos A e B não encontrados na configuração da unidade.",
            parent=parent,
        )
        return None

    result = {"value": None}

    top = tk.Toplevel(parent)
    top.title("Chamada — Selecionar alas")
    top.configure(bg="#1E2C44")
    top.resizable(True, True)
    top.transient(parent)

    title = tk.Label(
        top,
        text="Escolha as alas para imprimir a chamada (Bloco A e Bloco B)",
        font=FONT_TITLE,
        fg="#FFFFFF",
        bg="#1E2C44",
    )
    title.pack(pady=(12, 6), padx=16)

    hint = tk.Label(
        top,
        text="Use os botões de cada bloco para marcar todas ou limpar.",
        font=FONT_HINT,
        fg="#CCCCCC",
        bg="#1E2C44",
    )
    hint.pack(pady=(0, 10), padx=16)

    columns_master = tk.Frame(top, bg="#1E2C44")
    columns_master.pack(fill="both", expand=True, padx=14, pady=(0, 8))

    checkbox_vars = {}

    for col_idx, (block_key, block_data) in enumerate(blocks_to_show):
        block_title = block_data.get("name") or block_key
        alas_map = block_data.get("alas") or {}

        block_frame = tk.LabelFrame(
            columns_master,
            text=f" {block_title} ",
            font=FONT_BLOCK,
            fg="#FFFFFF",
            bg="#1E2C44",
            highlightbackground="#2B3C57",
            highlightthickness=1,
            bd=0,
        )
        block_frame.grid(row=0, column=col_idx, sticky="nsew", padx=(0 if col_idx == 0 else 8, 0))
        columns_master.columnconfigure(col_idx, weight=1, uniform="blk")

        btn_row = tk.Frame(block_frame, bg="#1E2C44")
        btn_row.pack(fill="x", padx=8, pady=(8, 6))

        def make_select_all(bk=block_key):
            def _fn():
                for (b, _a), var in checkbox_vars.items():
                    if b == bk:
                        var.set(True)

            return _fn

        def make_clear(bk=block_key):
            def _fn():
                for (b, _a), var in checkbox_vars.items():
                    if b == bk:
                        var.set(False)

            return _fn

        tk.Button(
            btn_row,
            text="Selecionar todas",
            font=FONT_BODY,
            bg="#2B3C57",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=make_select_all(),
            activebackground="#3d5270",
            activeforeground="#FFFFFF",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row,
            text="Limpar seleção",
            font=FONT_BODY,
            bg="#2B3C57",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=make_clear(),
            activebackground="#3d5270",
            activeforeground="#FFFFFF",
        ).pack(side="left")

        alas_inner = tk.Frame(block_frame, bg="#1E2C44")
        alas_inner.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        ala_keys = _sort_ala_keys(list(alas_map.keys()))
        for i, ala_key in enumerate(ala_keys):
            ala_info = alas_map[ala_key]
            text = ala_info.get("name") or ala_key

            var = tk.BooleanVar(value=True)
            checkbox_vars[(block_key, ala_key)] = var

            r, c = divmod(i, ALA_GRID_COLUMNS)
            cb = tk.Checkbutton(
                alas_inner,
                text=text,
                variable=var,
                font=FONT_BODY,
                bg="#1E2C44",
                fg="#FFFFFF",
                selectcolor="#2B3C57",
                activebackground="#1E2C44",
                activeforeground="#FFFFFF",
                anchor="w",
            )
            cb.grid(row=r, column=c, sticky="w", padx=2, pady=3)

    btn_footer = tk.Frame(top, bg="#1E2C44")
    btn_footer.pack(fill="x", pady=(6, 14), padx=16)

    def on_ok():
        selected = [
            (bk, ak)
            for (bk, ak), var in sorted(checkbox_vars.items())
            if var.get()
        ]
        if not selected:
            messagebox.showwarning(
                "Seleção",
                "Selecione pelo menos uma ala.",
                parent=top,
            )
            return
        result["value"] = selected
        top.destroy()

    def on_cancel():
        result["value"] = None
        top.destroy()

    ok_btn = tk.Button(
        btn_footer,
        text="Continuar",
        font=FONT_BTN_MAIN,
        bg="#1A73E8",
        fg="white",
        relief="flat",
        cursor="hand2",
        command=on_ok,
        activebackground="#155CBF",
        padx=16,
        pady=6,
    )
    ok_btn.pack(side="right", padx=(8, 0))

    cancel_btn = tk.Button(
        btn_footer,
        text="Cancelar",
        font=FONT_BTN_SEC,
        bg="#2B3C57",
        fg="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=on_cancel,
        activebackground="#3d5270",
        padx=16,
        pady=6,
    )
    cancel_btn.pack(side="right")

    top.protocol("WM_DELETE_WINDOW", on_cancel)
    top.bind("<Return>", lambda e: on_ok())
    top.bind("<Escape>", lambda e: on_cancel())

    _fit_toplevel_to_content(top)
    top.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (top.winfo_width() // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (top.winfo_height() // 2)
    top.geometry(f"{top.winfo_width()}x{top.winfo_height()}+{max(0, x)}+{max(0, y)}")

    top.grab_set()
    top.wait_window()

    return result["value"]
