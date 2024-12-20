import os
import sys
import logging
import urllib.request
from urllib.parse import urljoin
from packaging import version
import tkinter as tk
from tkinter import messagebox

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPDATE_URL = 'https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/'
VERSION_FILE = 'latest_version.txt'

class UpdateCheckError(Exception):
    pass

class UpdateDownloadError(Exception):
    pass


def get_latest_version():
    """
    Obtém a versão mais recente do servidor de atualização.

    Returns
    -------
    str
        A versão mais recente em forma de string.

    Raises
    ------
    UpdateCheckError
        Se ocorrer um problema ao buscar a versão.
    """
    try:
        version_url = urljoin(UPDATE_URL, VERSION_FILE)
        with urllib.request.urlopen(version_url, timeout=10) as response:
            data = response.read().decode('utf-8').strip()
        if not data:
            raise UpdateCheckError("Nenhuma versão encontrada no servidor.")
        return data
    except Exception as e:
        raise UpdateCheckError(f"Falha ao obter a versão mais recente: {e}")


def is_update_available(current_version):
    """
    Verifica se há uma versão mais recente disponível.

    Parameters
    ----------
    current_version : str
        A versão atual da aplicação.

    Returns
    -------
    (bool, str or None)
        Retorna uma tupla (update_disponivel, latest_version)
        update_disponivel: True se houver uma atualização, False caso contrário.
        latest_version: A string da última versão, ou None se não houver atualização.
    """
    try:
        latest_version = get_latest_version()
    except UpdateCheckError as e:
        logging.error(e)
        return False, None

    if version.parse(latest_version) > version.parse(current_version):
        return True, latest_version
    return False, None


def download_update(latest_version, target_path):
    """
    Baixa a atualização.

    Parameters
    ----------
    latest_version : str
        Versão a ser baixada.
    target_path : str
        Caminho completo onde salvar o arquivo baixado.

    Raises
    ------
    UpdateDownloadError
        Se ocorrer falha no download.
    """
    executable_name = f"canaime-preso-por-ala-{latest_version}.exe"
    download_url = urljoin(UPDATE_URL, executable_name)
    try:
        with urllib.request.urlopen(download_url, timeout=20) as response:
            data = response.read()
        with open(target_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        raise UpdateDownloadError(f"Falha ao baixar a atualização: {e}")


def prompt_user_for_update(latest_version):
    """
    Pergunta ao usuário se deseja atualizar para a nova versão.
    """
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno("Atualização disponível",
                                 f"Há uma nova versão ({latest_version}) disponível. Deseja atualizar agora?")
    root.destroy()
    return result


def apply_update(new_exe_path):
    """
    Aplica a atualização substituindo o processo atual pelo novo executável.

    Parameters
    ----------
    new_exe_path : str
        Caminho do novo executável.

    Raises
    ------
    FileNotFoundError
        Se o arquivo baixado não for encontrado.
    """
    if not os.path.exists(new_exe_path):
        raise FileNotFoundError(f"Arquivo de atualização não encontrado: {new_exe_path}")

    logging.info("Executando o instalador...")
    os.execl(new_exe_path, new_exe_path)


def update_application(current_version, executable_dir):
    """
    Verifica, pergunta ao usuário e, se aprovado, faz o download e aplica a atualização.

    Parameters
    ----------
    current_version : str
        Versão atual da aplicação.
    executable_dir : str
        Diretório onde o executável atual está localizado.

    Returns
    -------
    bool
        True se a atualização foi iniciada (o que significa que a aplicação será substituída),
        False caso não haja atualização ou o usuário recuse.
    """
    update_available, latest_version = is_update_available(current_version)
    if not update_available or latest_version is None:
        logging.info("Nenhuma atualização disponível.")
        return False

    logging.info(f"Atualização para a versão {latest_version} disponível.")
    if prompt_user_for_update(latest_version):
        logging.info("Usuário aceitou a atualização. Baixando...")
        update_exe_path = os.path.join(executable_dir, f'canaime-preso-por-ala-{latest_version}.exe')

        try:
            download_update(latest_version, update_exe_path)
            logging.info(f"Atualização baixada com sucesso em: {update_exe_path}")
            apply_update(update_exe_path)
            # Se tudo der certo, o processo atual será substituído pelo novo executável aqui.
        except Exception as e:
            logging.error(f"Falha na atualização: {e}")
            return False
    else:
        logging.info("Usuário recusou a atualização.")
        return False

    # Se chegar aqui é porque a atualização não foi aplicada (os.execl substitui o processo antes),
    # mas por segurança, retornamos False.
    return False
