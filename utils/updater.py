import os
import requests
from packaging import version
from urllib.parse import urljoin
import tkinter as tk
from tkinter import messagebox
from .logger import Logger

# Configurações
UPDATE_URL = 'https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/'
VERSION_FILE = 'latest_version.txt'


def get_latest_version():
    """Obtém a versão mais recente disponível no servidor."""
    try:
        response = requests.get(urljoin(UPDATE_URL, VERSION_FILE), timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        Logger.capture_error(e)
        return None


def download_update(latest_version, target_path):
    """Baixa o arquivo de atualização."""
    try:
        download_url = urljoin(UPDATE_URL, f"canaime-preso-por-ala-{latest_version}.exe")
        response = requests.get(download_url, stream=True, timeout=20)
        response.raise_for_status()
        with open(target_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        return True
    except requests.RequestException as e:
        Logger.capture_error(e)
        return False


def prompt_user_for_update(latest_version):
    """Pergunta ao usuário se deseja atualizar."""
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    result = messagebox.askyesno(
        "Atualização disponível",
        f"Uma nova versão ({latest_version}) está disponível. Deseja atualizar?"
    )
    root.destroy()
    return result


def check_and_update(current_version):
    """
    Verifica por atualizações e, se disponível, permite que o usuário escolha se deseja atualizar.
    """
    latest_version = get_latest_version()
    if not latest_version:
        print("Não foi possível verificar atualizações.")
        Logger.get_logger().warning("Falha ao verificar atualizações.")
        return False

    if version.parse(latest_version) <= version.parse(current_version):
        print("Nenhuma atualização disponível.")
        return False

    print(f"Nova versão disponível: {latest_version}.")
    user_wants_update = prompt_user_for_update(latest_version)

    if not user_wants_update:
        print("Atualização recusada pelo usuário.")
        return False

    update_path = os.path.join(os.getcwd(), f'canaime-preso-por-ala-{latest_version}.exe')
    if download_update(latest_version, update_path):
        print(f"Atualização baixada em: {update_path}.")
        Logger.get_logger().info(f"Atualização baixada: {update_path}")

        # Reiniciar o aplicativo com a nova versão
        import subprocess
        import sys
        try:
            subprocess.Popen(update_path, shell=True)
            sys.exit(0)
        except Exception as e:
            Logger.capture_error(e)
            print("Erro ao tentar iniciar a nova versão.")
            return False
    else:
        print("Falha ao baixar a atualização.")
        Logger.get_logger().error("Falha no download da atualização.")
        return False

    return True
