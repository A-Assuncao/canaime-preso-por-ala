"""
Módulo para gerenciar a pasta centralizada C:/Planilha PAMC
"""

import os
import shutil
from pathlib import Path

# Definir o caminho base da pasta PAMC
PAMC_FOLDER = Path("C:/Planilha PAMC")

def ensure_pamc_folder():
    """
    Verifica se a pasta C:/Planilha PAMC existe e a cria se necessário.
    
    Returns:
        Path: Caminho da pasta PAMC
    """
    try:
        # Criar a pasta se não existir
        PAMC_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Verificar se a pasta foi criada com sucesso
        if PAMC_FOLDER.exists() and PAMC_FOLDER.is_dir():
            return PAMC_FOLDER
        else:
            raise Exception(f"Não foi possível criar ou acessar a pasta {PAMC_FOLDER}")
            
    except Exception as e:
        raise Exception(f"Erro ao criar pasta PAMC: {str(e)}")

def get_pamc_log_path():
    """
    Retorna o caminho completo para o arquivo de log na pasta PAMC.
    
    Returns:
        Path: Caminho para app_log.log na pasta PAMC
    """
    pamc_folder = ensure_pamc_folder()
    return pamc_folder / "app_log.log"

def get_pamc_excel_path(filename):
    """
    Retorna o caminho completo para um arquivo Excel na pasta PAMC.
    
    Args:
        filename (str): Nome do arquivo Excel
        
    Returns:
        Path: Caminho completo para o arquivo na pasta PAMC
    """
    pamc_folder = ensure_pamc_folder()
    return pamc_folder / filename

def copy_file_to_pamc(source_path, target_filename=None):
    """
    Copia um arquivo para a pasta PAMC.
    
    Args:
        source_path (str): Caminho do arquivo origem
        target_filename (str, optional): Nome do arquivo destino. Se None, usa o nome original.
        
    Returns:
        Path: Caminho do arquivo copiado na pasta PAMC
    """
    try:
        pamc_folder = ensure_pamc_folder()
        
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Arquivo origem não encontrado: {source_path}")
        
        # Usar nome original se não especificado
        if target_filename is None:
            target_filename = source.name
            
        target_path = pamc_folder / target_filename
        
        # Copiar o arquivo
        shutil.copy2(source, target_path)
        
        return target_path
        
    except Exception as e:
        raise Exception(f"Erro ao copiar arquivo para pasta PAMC: {str(e)}")

def list_pamc_files(extension=None):
    """
    Lista arquivos na pasta PAMC, opcionalmente filtrados por extensão.
    
    Args:
        extension (str, optional): Extensão para filtrar (ex: '.xlsx', '.log')
        
    Returns:
        list: Lista de arquivos na pasta PAMC
    """
    try:
        pamc_folder = ensure_pamc_folder()
        
        if extension:
            # Filtrar por extensão
            files = [f for f in pamc_folder.iterdir() if f.is_file() and f.suffix.lower() == extension.lower()]
        else:
            # Listar todos os arquivos
            files = [f for f in pamc_folder.iterdir() if f.is_file()]
            
        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        
    except Exception as e:
        raise Exception(f"Erro ao listar arquivos da pasta PAMC: {str(e)}")

def get_pamc_folder_info():
    """
    Retorna informações sobre a pasta PAMC.
    
    Returns:
        dict: Informações da pasta (existe, tamanho, número de arquivos, etc.)
    """
    try:
        pamc_folder = ensure_pamc_folder()
        
        files = list(pamc_folder.iterdir())
        total_files = len([f for f in files if f.is_file()])
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "path": str(pamc_folder),
            "exists": pamc_folder.exists(),
            "is_directory": pamc_folder.is_dir(),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        return {
            "path": str(PAMC_FOLDER),
            "exists": False,
            "error": str(e)
        } 