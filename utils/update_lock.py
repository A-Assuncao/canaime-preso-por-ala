"""
Lock de atualização em andamento (evita downloads/instâncias duplicados).
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

LOCK_PATH = Path(tempfile.gettempdir()) / "canaime-update.lock"


@dataclass
class UpdateLockInfo:
    pid: int
    version: str
    started_at: str


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if psutil is not None:
        return psutil.pid_exists(pid)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def read_lock() -> UpdateLockInfo | None:
    if not LOCK_PATH.is_file():
        return None
    try:
        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        return UpdateLockInfo(
            pid=int(data["pid"]),
            version=str(data["version"]),
            started_at=str(data.get("started_at", "")),
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def acquire_lock(version: str) -> bool:
    """Cria o lock para o PID atual. Retorna False se outra atualização estiver ativa."""
    existing = read_lock()
    if existing is not None and _pid_alive(existing.pid):
        return False
    release_lock()
    info = UpdateLockInfo(
        pid=os.getpid(),
        version=version,
        started_at=datetime.now(timezone.utc).isoformat(),
    )
    LOCK_PATH.write_text(json.dumps(asdict(info), ensure_ascii=False), encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def is_update_in_progress() -> UpdateLockInfo | None:
    """Retorna dados do lock se uma atualização válida estiver em andamento."""
    info = read_lock()
    if info is None:
        return None
    if _pid_alive(info.pid):
        return info
    release_lock()
    return None
