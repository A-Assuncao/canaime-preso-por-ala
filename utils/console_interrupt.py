"""
Permite encerrar o app com Ctrl+C no terminal mesmo com Tkinter (Windows).
"""

from __future__ import annotations

import os
import signal
import tkinter as tk


def enable_ctrl_c_exit(root: tk.Misc) -> None:
    """
    Registra SIGINT e mantém o event loop do Tk ativo para o sinal ser processado.

    Cancela o timer ao destruir a janela (evita ``invalid command name ..._pulse``).
    """
    state: dict = {"after_id": None}

    def _cancel_pulse() -> None:
        after_id = state.get("after_id")
        if after_id is not None:
            try:
                root.after_cancel(after_id)
            except tk.TclError:
                pass
            state["after_id"] = None

    def _shutdown() -> None:
        print("\nEncerrando (Ctrl+C)...", flush=True)
        _cancel_pulse()
        try:
            from utils.logger import Logger

            Logger.end_session()
        except Exception:
            pass
        try:
            root.quit()
        except tk.TclError:
            pass
        os._exit(130)

    def _on_sigint(_signum, _frame) -> None:
        try:
            root.after(0, _shutdown)
        except tk.TclError:
            os._exit(130)

    def _pulse() -> None:
        try:
            if not root.winfo_exists():
                return
            state["after_id"] = root.after(400, _pulse)
        except tk.TclError:
            _cancel_pulse()

    def _on_destroy(event) -> None:
        if event.widget is root:
            _cancel_pulse()

    signal.signal(signal.SIGINT, _on_sigint)
    root.bind("<Destroy>", _on_destroy, add="+")

    try:
        state["after_id"] = root.after(400, _pulse)
    except tk.TclError:
        pass
