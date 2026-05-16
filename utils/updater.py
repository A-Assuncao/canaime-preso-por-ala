"""
Verificação e aplicação de atualizações (download com progresso e abertura da nova versão).
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin

import requests
import tkinter as tk
from packaging import version
from tkinter import messagebox

from utils.logger import Logger
from utils.update_helper import HELPER_LOG, shutdown_current_app
from utils.update_lock import acquire_lock, is_update_in_progress, release_lock

logger = Logger.get_logger()

UPDATE_URL = os.getenv(
    "UPDATE_URL",
    "https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/",
)
VERSION_FILE = "latest_version.txt"
CHUNK_SIZE = 256 * 1024
SPEED_WINDOW_SEC = 1.5


@dataclass
class DownloadProgress:
    downloaded_bytes: int
    total_bytes: int | None
    speed_bps: float
    eta_seconds: float | None

    @property
    def status_line(self) -> str:
        if self.total_bytes and self.total_bytes > 0:
            pct = 100.0 * self.downloaded_bytes / self.total_bytes
            return f"{pct:5.1f}%  —  {_format_bytes(self.downloaded_bytes)} / {_format_bytes(self.total_bytes)}"
        return f"Baixado: {_format_bytes(self.downloaded_bytes)}"

    @property
    def detail_line(self) -> str:
        speed = _format_speed(self.speed_bps)
        if self.eta_seconds is not None and self.eta_seconds >= 0:
            return f"Velocidade: {speed}  |  Tempo restante: {_format_eta(self.eta_seconds)}"
        return f"Velocidade: {speed}"


def _normalize_version(ver: str) -> str:
    return ver.strip().lstrip("vV")


def _format_bytes(num: int) -> str:
    if num < 1024:
        return f"{num} B"
    if num < 1024 * 1024:
        return f"{num / 1024:.1f} KB"
    return f"{num / (1024 * 1024):.2f} MB"


def _format_speed(bps: float) -> str:
    if bps <= 0:
        return "—"
    return f"{_format_bytes(int(bps))}/s"


def _format_eta(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min {secs} s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes} min"


def _install_directory() -> Path:
    """
    Pasta onde o instalador .exe é salvo.

    - Empacotado (PyInstaller): mesma pasta do .exe em execução.
    - Desenvolvimento: raiz do repositório (não usa cwd nem %TEMP%).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_latest_version() -> str | None:
    """Obtém a versão mais recente disponível no servidor."""
    try:
        response = requests.get(urljoin(UPDATE_URL, VERSION_FILE), timeout=15)
        response.raise_for_status()
        return _normalize_version(response.text)
    except requests.RequestException as e:
        logger.warning("Falha ao obter versão remota: %s", e)
        return None


def _release_asset_filenames(latest_version: str) -> list[str]:
    """Nomes de artefato no GitHub Releases (com e sem ``v`` no nome do arquivo)."""
    ver = _normalize_version(latest_version)
    return [
        f"canaime-preso-por-ala-v{ver}.exe",
        f"canaime-preso-por-ala-{ver}.exe",
    ]


def resolve_update_asset(latest_version: str) -> tuple[str, str] | None:
    """
    Localiza URL e nome do .exe publicado no release.

    Returns:
        ``(url, filename)`` ou ``None`` se nenhum candidato existir (HTTP 200).
    """
    for filename in _release_asset_filenames(latest_version):
        url = urljoin(UPDATE_URL, filename)
        try:
            response = requests.head(url, timeout=8, allow_redirects=True)
            if response.status_code == 200:
                return url, filename
        except requests.RequestException as exc:
            logger.warning("HEAD falhou para %s: %s", url, exc)
    return None


def build_download_url(latest_version: str) -> str:
    resolved = resolve_update_asset(latest_version)
    if resolved is None:
        ver = _normalize_version(latest_version)
        return urljoin(UPDATE_URL, f"canaime-preso-por-ala-v{ver}.exe")
    return resolved[0]


def build_target_exe_path(latest_version: str, asset_filename: str | None = None) -> Path:
    if asset_filename:
        return _install_directory() / asset_filename
    ver = _normalize_version(latest_version)
    return _install_directory() / f"canaime-preso-por-ala-v{ver}.exe"


def download_update_with_progress(
    download_url: str,
    target_path: str | Path,
    *,
    on_progress: Callable[[DownloadProgress], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> tuple[bool, str | None]:
    """
    Baixa o executável com relatório de progresso.

    Grava primeiro em ``.part`` e renomeia ao concluir.

    Returns:
        ``(sucesso, mensagem_de_erro)``
    """
    target = Path(target_path)
    partial = target.with_suffix(target.suffix + ".part")
    partial.parent.mkdir(parents=True, exist_ok=True)

    if partial.exists():
        partial.unlink()

    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        total = response.headers.get("Content-Length")
        total_bytes = int(total) if total else None

        if on_progress:
            on_progress(
                DownloadProgress(
                    downloaded_bytes=0,
                    total_bytes=total_bytes,
                    speed_bps=0.0,
                    eta_seconds=None,
                )
            )

        downloaded = 0
        window_start = time.monotonic()
        window_bytes = 0
        speed_bps = 0.0

        with partial.open("wb") as out_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if cancel_event and cancel_event.is_set():
                    if partial.exists():
                        partial.unlink(missing_ok=True)
                    return False, "Download cancelado."
                if not chunk:
                    continue
                out_file.write(chunk)
                downloaded += len(chunk)
                window_bytes += len(chunk)

                now = time.monotonic()
                elapsed = now - window_start
                if elapsed >= SPEED_WINDOW_SEC:
                    speed_bps = window_bytes / elapsed if elapsed > 0 else 0.0
                    window_start = now
                    window_bytes = 0

                eta = None
                if total_bytes and speed_bps > 0:
                    remaining = max(0, total_bytes - downloaded)
                    eta = remaining / speed_bps

                if on_progress:
                    on_progress(
                        DownloadProgress(
                            downloaded_bytes=downloaded,
                            total_bytes=total_bytes,
                            speed_bps=speed_bps,
                            eta_seconds=eta,
                        )
                    )

        partial.replace(target)
        return True, None
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        msg = f"Arquivo não encontrado no servidor (HTTP {status}).\nURL: {download_url}"
        logger.error("Falha no download da atualização: %s", msg)
        if partial.exists():
            partial.unlink(missing_ok=True)
        return False, msg
    except requests.RequestException as e:
        msg = f"Erro de rede ao baixar: {e}"
        logger.error("Falha no download da atualização: %s", msg)
        if partial.exists():
            partial.unlink(missing_ok=True)
        return False, msg


def _show_update_error_message(message: str) -> None:
    """Exibe erro de atualização (cria root temporário se necessário)."""
    root = tk.Tk()
    root.withdraw()
    try:
        messagebox.showerror("Erro na atualização", message, parent=root)
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


def prompt_user_for_update(parent: tk.Misc, latest_version: str, current_version: str) -> bool:
    return messagebox.askyesno(
        "Atualização disponível",
        (
            f"Há uma nova versão disponível.\n\n"
            f"Instalada: {current_version}\n"
            f"Nova: {latest_version}\n\n"
            "Deseja baixar a atualização agora?\n"
            "Ao concluir, você poderá escolher se abre a nova versão."
        ),
        parent=parent,
    )


def check_and_update(current_version: str, *, parent: tk.Misc | None = None) -> bool:
    """
    Verifica atualização; se o usuário aceitar, baixa com UI e reinicia via helper.

    Returns:
        True se a atualização foi aplicada e o processo atual deve encerrar.
        False se não há atualização, usuário recusou ou houve falha recuperável.
    """
    own_root: tk.Tk | None = None
    if parent is None:
        own_root = tk.Tk()
        own_root.withdraw()
        parent = own_root

    try:
        in_progress = is_update_in_progress()
        if in_progress is not None:
            messagebox.showinfo(
                "Atualização em andamento",
                (
                    "Outra janela deste programa já está atualizando.\n"
                    "Aguarde a conclusão ou feche a outra instância."
                ),
                parent=parent,
            )
            return False

        latest_version = get_latest_version()
        if not latest_version:
            logger.warning("Falha ao verificar atualizações.")
            return False

        current_norm = _normalize_version(current_version)
        if version.parse(latest_version) <= version.parse(current_norm):
            return False

        if not prompt_user_for_update(parent, latest_version, current_version):
            logger.info("Atualização recusada pelo usuário.")
            return False

        if not acquire_lock(latest_version):
            messagebox.showinfo(
                "Atualização em andamento",
                "Não foi possível iniciar: outra atualização já está em execução.",
                parent=parent,
            )
            return False

        resolved = resolve_update_asset(latest_version)
        if resolved is None:
            ver = _normalize_version(latest_version)
            names = ", ".join(_release_asset_filenames(latest_version))
            messagebox.showerror(
                "Erro na atualização",
                (
                    f"Não foi encontrado o instalador da versão {ver} no servidor.\n\n"
                    f"Arquivos esperados:\n{names}\n\n"
                    "Verifique o release no GitHub."
                ),
                parent=parent,
            )
            release_lock()
            return False

        download_url, asset_filename = resolved
        target_path = build_target_exe_path(latest_version, asset_filename)

        # Fecha o root oculto dos diálogos antes do progresso (evita dois tk.Tk() ao mesmo tempo).
        if own_root is not None:
            try:
                own_root.destroy()
            except tk.TclError:
                pass
            own_root = None
            parent = None

        try:
            from gui.update.update_progress_dialog import (
                UpdateDialogResult,
                UpdateProgressDialog,
            )
            from utils.update_helper import launch_downloaded_and_exit

            dialog = UpdateProgressDialog(
                None,
                latest_version=latest_version,
                target_path=str(target_path),
                download_url=download_url,
            )
            result = dialog.wait()

            if result == UpdateDialogResult.FAILED:
                logger.error("Falha ou cancelamento no download da atualização.")
                release_lock()
                print(
                    "\n[Atualização] Download falhou ou foi cancelado.\n"
                    "O programa continuará com a versão instalada.\n"
                    "Para sair: feche a janela do programa ou pressione Ctrl+C.\n",
                    flush=True,
                )
                return False

            if result == UpdateDialogResult.SKIP:
                release_lock()
                print(
                    f"\n[Atualização] Nova versão salva em:\n  {target_path}\n"
                    "Continuando com a versão instalada.\n",
                    flush=True,
                )
                return False

            if result != UpdateDialogResult.LAUNCH:
                release_lock()
                return False

            if not target_path.is_file() or target_path.stat().st_size < 1024:
                _show_update_error_message(
                    f"O arquivo baixado parece inválido:\n{target_path}",
                )
                release_lock()
                return False

            logger.info("Abrindo nova versão: %s", target_path)
            release_lock()
            try:
                launch_downloaded_and_exit(target_path)
            except (OSError, FileNotFoundError, RuntimeError) as exc:
                acquire_lock(latest_version)
                _show_update_error_message(
                    f"Não foi possível abrir a nova versão:\n{exc}\n\n"
                    f"Tente executar manualmente:\n{target_path}\n\n"
                    f"Log: {HELPER_LOG}"
                )
                return False
        except Exception as exc:
            release_lock()
            logger.exception("Erro inesperado na atualização")
            _show_update_error_message(f"Erro inesperado na atualização:\n{exc}")
            return False

        return True  # inalcançável (shutdown_current_app)
    finally:
        if own_root is not None:
            try:
                own_root.destroy()
            except Exception:
                pass
