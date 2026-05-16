"""
Janela de progresso e conclusão do download da atualização.
"""

from __future__ import annotations

import threading
import tkinter as tk
from enum import Enum
from pathlib import Path
from tkinter import messagebox, ttk

from config.config import APP_DISPLAY_NAME
from utils.updater import DownloadProgress, download_update_with_progress

_WINDOW_W = 480
_WINDOW_H_DOWNLOAD = 300
_WINDOW_H_DONE = 340


class UpdateDialogResult(Enum):
    """Resultado após fechar a janela de atualização."""

    FAILED = "failed"
    SKIP = "skip"
    LAUNCH = "launch"


class UpdateProgressDialog:
    """Download com progresso; ao concluir, pergunta se abre a nova versão."""

    def __init__(
        self,
        parent: tk.Misc | None,
        *,
        latest_version: str,
        target_path: str,
        download_url: str,
    ) -> None:
        _ = parent
        self._target_path = target_path
        self._download_url = download_url
        self._latest_version = latest_version
        self._cancel_event = threading.Event()
        self._success = False
        self._error_message: str | None = None
        self._pending_progress: DownloadProgress | None = None
        self._indeterminate = False
        self._ui_finished = False
        self._result = UpdateDialogResult.FAILED

        self._root = tk.Tk()
        self.window = self._root
        self.window.title(f"{APP_DISPLAY_NAME} — baixando atualização")
        self.window.configure(bg="#1E2C44")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.window.attributes("-topmost", True)

        self._content = tk.Frame(self.window, bg="#1E2C44", padx=24, pady=20)
        self._content.pack(fill="both", expand=True)

        tk.Label(
            self._content,
            text=f"Atualizando para a versão {latest_version}",
            font=("Segoe UI", 11, "bold"),
            fg="#E8EEF7",
            bg="#1E2C44",
        ).pack(anchor="w")

        tk.Label(
            self._content,
            text="Não feche esta janela durante o download.",
            font=("Segoe UI", 9),
            fg="#9FB0C8",
            bg="#1E2C44",
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(6, 14))

        self._progress = ttk.Progressbar(self._content, mode="determinate", length=420, maximum=100)
        self._progress.pack(fill="x", pady=(0, 10))

        self._status_var = tk.StringVar(value="Preparando download…")
        tk.Label(
            self._content,
            textvariable=self._status_var,
            font=("Consolas", 9),
            fg="#C5D4E8",
            bg="#1E2C44",
            anchor="w",
            justify="left",
            wraplength=420,
        ).pack(fill="x")

        self._detail_var = tk.StringVar(value="Aguardando resposta do servidor…")
        tk.Label(
            self._content,
            textvariable=self._detail_var,
            font=("Consolas", 9),
            fg="#8FA3BC",
            bg="#1E2C44",
            anchor="w",
            justify="left",
            wraplength=420,
        ).pack(fill="x", pady=(4, 12))

        self._cancel_btn = tk.Button(
            self._content,
            text="Cancelar download",
            command=self._on_cancel,
            font=("Segoe UI", 9),
            bg="#3A4D6B",
            fg="#E8EEF7",
            activebackground="#4A5F82",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self._cancel_btn.pack(anchor="e")

        self._center_on_screen(_WINDOW_H_DOWNLOAD)
        self._worker = threading.Thread(target=self._run_download, daemon=True)
        self._worker.start()
        self.window.after(80, self._poll_progress)

    @property
    def success(self) -> bool:
        return self._success

    def wait(self) -> UpdateDialogResult:
        """Executa o loop de eventos até o usuário decidir ou falhar."""
        try:
            self._root.mainloop()
        except tk.TclError:
            pass
        return self._result

    def _center_on_screen(self, height: int) -> None:
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        x = max(0, (sw - _WINDOW_W) // 2)
        y = max(0, (sh - height) // 2)
        self.window.geometry(f"{_WINDOW_W}x{height}+{x}+{y}")
        self.window.lift()
        self.window.focus_force()

    def _on_cancel(self) -> None:
        if self._ui_finished and self._success:
            self._choose_skip()
            return
        if self._cancel_event.is_set():
            return
        if messagebox.askyesno(
            "Cancelar atualização",
            "Deseja cancelar o download?",
            parent=self.window,
        ):
            self._cancel_event.set()
            self._cancel_btn.configure(state="disabled")
            self._status_var.set("Cancelando…")

    def _run_download(self) -> None:
        try:
            ok, err = download_update_with_progress(
                self._download_url,
                self._target_path,
                on_progress=self._schedule_progress,
                cancel_event=self._cancel_event,
            )
            self._success = ok
            if not ok:
                self._error_message = err or "Falha no download."
            if self._cancel_event.is_set():
                self._success = False
                self._error_message = "Download cancelado pelo usuário."
        except Exception as exc:  # noqa: BLE001
            self._success = False
            self._error_message = str(exc)

    def _schedule_progress(self, progress: DownloadProgress) -> None:
        self._pending_progress = progress

    def _window_alive(self) -> bool:
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def _poll_progress(self) -> None:
        if self._ui_finished or not self._window_alive():
            return

        if self._pending_progress is not None:
            self._apply_progress(self._pending_progress)

        if not self._worker.is_alive():
            self._finish()
            return

        try:
            self.window.after(80, self._poll_progress)
        except tk.TclError:
            pass

    def _apply_progress(self, progress: DownloadProgress) -> None:
        if progress is None:
            return
        if progress.total_bytes and progress.total_bytes > 0:
            if self._indeterminate:
                self._progress.stop()
                self._indeterminate = False
            pct = min(100.0, 100.0 * progress.downloaded_bytes / progress.total_bytes)
            self._progress.configure(mode="determinate", maximum=100, value=pct)
        elif not self._indeterminate:
            self._progress.configure(mode="indeterminate")
            self._progress.start(12)
            self._indeterminate = True

        self._status_var.set(progress.status_line)
        self._detail_var.set(progress.detail_line)

    def _finish(self) -> None:
        if self._ui_finished:
            return
        self._ui_finished = True

        if not self._window_alive():
            return

        try:
            self._progress.stop()
        except tk.TclError:
            pass

        if self._success:
            if not Path(self._target_path).is_file():
                self._success = False
                self._error_message = (
                    f"O download terminou, mas o arquivo não foi encontrado:\n"
                    f"{self._target_path}"
                )
                msg = self._error_message
                messagebox.showerror("Erro na atualização", msg, parent=self.window)
                self._result = UpdateDialogResult.FAILED
                self._close_window()
                return
            self._show_completion_screen()
            return

        msg = self._error_message or "Falha no download."
        detail = (
            f"{msg}\n\n"
            "O programa continuará com a versão já instalada.\n\n"
            "Para sair: feche a janela principal ou pressione Ctrl+C no terminal."
        )
        messagebox.showerror("Erro na atualização", detail, parent=self.window)
        self._result = UpdateDialogResult.FAILED
        self._close_window()

    def _show_completion_screen(self) -> None:
        self.window.title(f"{APP_DISPLAY_NAME} — atualização concluída")
        self.window.protocol("WM_DELETE_WINDOW", self._choose_skip)

        for child in self._content.winfo_children():
            child.destroy()

        tk.Label(
            self._content,
            text="Download concluído",
            font=("Segoe UI", 14, "bold"),
            fg="#6EEB83",
            bg="#1E2C44",
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            self._content,
            text=(
                f"A versão {self._latest_version} foi salva em:\n"
                f"{self._target_path}\n\n"
                "Deseja abrir a nova versão agora?\n"
                "O programa atual será fechado e a nova versão será iniciada.\n"
                "(A primeira abertura do .exe pode levar alguns segundos — é normal.)"
            ),
            font=("Segoe UI", 9),
            fg="#C5D4E8",
            bg="#1E2C44",
            justify="left",
            wraplength=420,
        ).pack(anchor="w", pady=(0, 20))

        btn_row = tk.Frame(self._content, bg="#1E2C44")
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="Abrir nova versão",
            command=self._choose_launch,
            font=("Segoe UI", 10, "bold"),
            bg="#2E7D4F",
            fg="#FFFFFF",
            activebackground="#3A9960",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_row,
            text="Continuar com a versão atual",
            command=self._choose_skip,
            font=("Segoe UI", 9),
            bg="#3A4D6B",
            fg="#E8EEF7",
            activebackground="#4A5F82",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left")

        self._center_on_screen(_WINDOW_H_DONE)

    def _choose_launch(self) -> None:
        """Registra a escolha; a abertura ocorre logo após fechar esta janela."""
        path = Path(self._target_path)
        if not path.is_file():
            messagebox.showerror(
                "Erro na atualização",
                f"Arquivo não encontrado:\n{path}",
                parent=self.window,
            )
            return
        self.window.title("Abrindo nova versão…")
        for child in self._content.winfo_children():
            child.destroy()
        tk.Label(
            self._content,
            text="Abrindo a nova versão…",
            font=("Segoe UI", 11, "bold"),
            fg="#E8EEF7",
            bg="#1E2C44",
        ).pack(anchor="w", pady=(8, 6))
        tk.Label(
            self._content,
            text="Aguarde. A janela do programa novo pode demorar alguns segundos na primeira execução.",
            font=("Segoe UI", 9),
            fg="#9FB0C8",
            bg="#1E2C44",
            wraplength=420,
            justify="left",
        ).pack(anchor="w")
        self.window.update_idletasks()
        self._result = UpdateDialogResult.LAUNCH
        self._close_window()

    def _choose_skip(self) -> None:
        self._result = UpdateDialogResult.SKIP
        self._close_window()

    def _close_window(self) -> None:
        try:
            self._root.quit()
        except tk.TclError:
            pass
        try:
            self._root.destroy()
        except tk.TclError:
            pass
