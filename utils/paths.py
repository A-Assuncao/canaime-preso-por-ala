import os
import sys

# Define o diretório base do projeto (diretório pai de utils)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios específicos do projeto
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
UTILS_DIR = os.path.join(PROJECT_ROOT, 'utils')
GUI_DIR = os.path.join(PROJECT_ROOT, 'gui')
SERVICES_DIR = os.path.join(PROJECT_ROOT, 'services')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def setup_project_paths():
    """
    Adiciona todos os diretórios do projeto ao sys.path para facilitar as importações.
    """
    paths_to_add = [
        PROJECT_ROOT,
        CONFIG_DIR,
        UTILS_DIR,
        os.path.join(GUI_DIR, 'login'),
        SERVICES_DIR,
        DATA_DIR
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.append(path) 