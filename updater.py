import os
import requests
import zipfile
import sys
import shutil
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Update these URLs as necessary
UPDATE_URL = 'https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/'
VERSION_FILE = 'latest_version.txt'
UPDATE_ARCHIVE = 'latest.zip'


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


def download_update(target_path):
    """
    Downloads the update file from the server.

    Parameters
    ----------
    target_path : str
        The path where the update file will be saved.

    Returns
    -------
    bool
        True if the download is successful, False otherwise.
    """
    try:
        response = requests.get(os.path.join(UPDATE_URL, UPDATE_ARCHIVE), stream=True)
        response.raise_for_status()
        with open(target_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return True
    except requests.RequestException as e:
        logging.error(f"Falha ao baixar a atualização: {e}")
        return False


def extract_update(zip_path, extract_to):
    """
    Extracts the downloaded update file.

    Parameters
    ----------
    zip_path : str
        The path to the update ZIP file.
    extract_to : str
        The path where the contents of the ZIP file will be extracted.

    Returns
    -------
    bool
        True if the extraction is successful, False otherwise.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except zipfile.BadZipFile as e:
        logging.error(f"Falha ao extrair a atualização: {e}")
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
        logging.info("Atualização disponível. Baixando...")
        with tempfile.TemporaryDirectory() as temp_dir:
            update_zip_path = os.path.join(temp_dir, 'update.zip')
            if download_update(update_zip_path):
                logging.info("Extraindo atualização...")
                if extract_update(update_zip_path, '.'):
                    logging.info("Atualização aplicada com sucesso. Reiniciando aplicativo...")
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    logging.error("Falha ao extrair a atualização.")
            else:
                logging.error("Falha ao baixar a atualização.")
    else:
        logging.info("Nenhuma atualização disponível.")
    return False
