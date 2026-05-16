"""
Inicia a nova versão baixada e encerra o processo atual (Windows).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_CREATE_NEW_PROCESS_GROUP = 0x00000200
_DETACHED_PROCESS = 0x00000008

HELPER_LOG = Path(tempfile.gettempdir()) / "canaime-update-helper.log"


def _log(message: str) -> None:
    try:
        with HELPER_LOG.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")
    except OSError:
        pass


def launch_downloaded_and_exit(new_exe_path: Path) -> None:
    """
    Inicia o .exe novo em processo separado e encerra o app atual.

    Não usa PowerShell (falhava em silêncio). Mesma ideia do updater original:
    ``Popen`` do novo executável e ``os._exit``.
    """
    resolved = new_exe_path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Instalador não encontrado:\n{resolved}")

    size = resolved.stat().st_size
    if size < 1024:
        raise RuntimeError(f"Arquivo inválido ({size} bytes): {resolved}")

    work_dir = str(resolved.parent)
    current_pid = os.getpid()
    _log(f"Iniciando nova versão pid_pai={current_pid} exe={resolved} ({size} bytes)")

    try:
        from utils.logger import Logger

        Logger.end_session()
    except Exception:
        pass

    try:
        if os.name == "nt":
            proc = subprocess.Popen(
                [str(resolved)],
                cwd=work_dir,
                creationflags=_DETACHED_PROCESS | _CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _log(f"subprocess.Popen OK, filho PID={proc.pid}")
        else:
            subprocess.Popen(
                [str(resolved)],
                cwd=work_dir,
                start_new_session=True,
                close_fds=True,
            )
            _log("subprocess.Popen OK (não-Windows)")
    except OSError as exc:
        _log(f"ERRO ao iniciar processo: {exc}")
        if os.name == "nt":
            try:
                os.startfile(str(resolved))  # noqa: SIM115
                _log("Fallback os.startfile OK")
            except OSError as exc2:
                _log(f"ERRO os.startfile: {exc2}")
                raise RuntimeError(
                    f"Não foi possível abrir o programa:\n{exc}\n\n"
                    f"Abra manualmente:\n{resolved}"
                ) from exc2
        else:
            raise

    time.sleep(0.15)
    _log(f"Encerrando processo atual PID={current_pid}")
    shutdown_current_app()


def _destroy_tk(root) -> None:
    if root is None:
        return
    try:
        root.quit()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass


def shutdown_current_app(tk_root=None) -> None:
    """Encerra o processo atual imediatamente."""
    import logging

    _destroy_tk(tk_root)
    try:
        import tkinter as tk

        default = tk._default_root
        if default is not None and default is not tk_root:
            _destroy_tk(default)
    except Exception:
        pass

    logging.shutdown()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
