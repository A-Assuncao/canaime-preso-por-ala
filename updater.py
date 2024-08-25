import os
import requests
import logging

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
        response = requests.get(os.path.join(UPDATE_URL, VERSION_FILE))
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
        download_url = os.path.join(UPDATE_URL, executable_name)
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(target_path, 'wb') as out_file:
            out_file.write(response.content)
        return True
    except requests.RequestException as e:
        logging.error(f"Falha ao baixar a atualização: {e}")
        return False


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
        return False

    if latest_version != current_version:
        logging.info(f"Atualização para a versão {latest_version} disponível. Baixando...")
        # Usar o diretório de trabalho atual para salvar o arquivo de atualização
        update_exe_path = os.path.join(os.getcwd(), f'canaime-preso-por-ala-{latest_version}.exe')
        if download_update(latest_version, update_exe_path):
            logging.info(f"Atualização baixada com sucesso e salva em: {update_exe_path}")
            print(f"Arquivo de atualização salvo em: {update_exe_path}")
            logging.info("Executando o instalador...")
            os.execl(update_exe_path, update_exe_path)
        else:
            logging.error("Falha ao baixar a atualização.")
    else:
        logging.info("Nenhuma atualização disponível.")
    return False
