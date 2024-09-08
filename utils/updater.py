import os
import requests
import logging
from packaging import version
from urllib.parse import urljoin
import tkinter as tk
from tkinter import messagebox

from utils.resource_manager import get_executable_dir

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Update these URLs as necessary
UPDATE_URL = 'https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/'
VERSION_FILE = 'latest_version.txt'


def get_latest_version():
    """
    Gets the latest version of the application from the update server.

    Returns
    -------
    str
        The latest version of the application as a string, or None in case of failure.
    """
    try:
        version_url = urljoin(UPDATE_URL, VERSION_FILE)
        response = requests.get(version_url, timeout=10)  # Adicionar timeout para requests
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        logging.error(f"Falha ao obter a versão mais recente: {e}")
        return None


def download_update(version, target_path):
    """
    Downloads the update file from the server.

    Parameters
    ----------
    version : str
        The version of the application to download.
    target_path : str
        The path where the update file will be saved.

    Returns
    -------
    bool
        True if the download is successful, False otherwise.
    """
    try:
        executable_name = f"canaime-preso-por-ala-{version}.exe"
        download_url = urljoin(UPDATE_URL, executable_name)  # Usar urljoin para URLs
        response = requests.get(download_url, stream=True, timeout=20)  # Adicionar timeout para downloads
        response.raise_for_status()
        with open(target_path, 'wb') as out_file:
            out_file.write(response.content)
        return True
    except requests.RequestException as e:
        logging.error(f"Falha ao baixar a atualização: {e}")
        return False


def prompt_user_for_update():
    """
    Pergunta ao usuário se deseja realizar a atualização.

    Returns
    -------
    bool
        True se o usuário aceitar a atualização, False se recusar.
    """
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    result = messagebox.askyesno("Atualização disponível", "Há uma nova versão disponível. Deseja atualizar agora?")
    root.destroy()
    return result


def update_application(current_version):
    """
    Checks if an update is available and, if so, downloads and applies the update,
    restarting the application.

    Parameters
    ----------
    current_version : str
        The current version of the application.

    Returns
    -------
    bool
        False if there is no update or if the update fails.
    """
    latest_version = get_latest_version()
    if not latest_version:
        logging.info("Não foi possível verificar atualizações.")
        return False

    # Usar a biblioteca 'packaging' para comparar versões
    if version.parse(latest_version) > version.parse(current_version):
        logging.info(f"Atualização para a versão {latest_version} disponível.")

        # Pergunta ao usuário se deseja atualizar
        if prompt_user_for_update():
            logging.info("Usuário aceitou a atualização. Baixando...")
            # Usar o diretório onde o executável está rodando
            exec_dir = get_executable_dir()
            update_exe_path = os.path.join(exec_dir, f'canaime-preso-por-ala-{latest_version}.exe')

            if download_update(latest_version, update_exe_path):
                logging.info(f"Atualização baixada com sucesso e salva em: {update_exe_path}")

                # Verifique se o arquivo existe
                if os.path.exists(update_exe_path):
                    logging.info("Executando o instalador...")
                    os.execl(update_exe_path, update_exe_path)
                else:
                    logging.error("Arquivo de atualização não encontrado após o download.")

        else:
            logging.info("Usuário recusou a atualização.")
    else:
        logging.info("Nenhuma atualização disponível.")

    return False
