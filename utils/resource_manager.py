import sys
import os


def resource_path(relative_path):
    """
    Obtém o caminho absoluto para um recurso, funciona para dev e para PyInstaller.

    Parameters
    ----------
    relative_path : str
        Caminho relativo para o recurso (arquivo, imagem, etc.)

    Returns
    -------
    str
        Caminho absoluto para o recurso.
    """
    # Verifica se o código está rodando dentro de um pacote PyInstaller (onde _MEIPASS é definido)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")  # Em desenvolvimento, usa o diretório atual
    return os.path.join(base_path, relative_path)


def get_executable_dir():
    """
    Obtém o caminho absoluto do diretório onde o executável está localizado.
    Funciona tanto no modo de desenvolvimento quanto em executáveis criados com PyInstaller.

    Returns
    -------
    str
        Caminho absoluto do diretório do executável.
    """
    if getattr(sys, 'frozen', False):  # Se o código estiver congelado (usando PyInstaller)
        return os.path.dirname(sys.executable)  # Diretório onde o executável está
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Diretório do script Python
