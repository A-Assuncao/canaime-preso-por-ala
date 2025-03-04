"""
Repositório de Unidades.

Gerencia o acesso e manipulação dos dados de unidades.
"""
import json
from models.entities.unit import Unit
from utils.logger import Logger
from utils.resource_manager import resource_path

logger = Logger.get_logger()


class UnitRepository:
    """
    Classe responsável por gerenciar os dados de unidades.
    
    Attributes
    ----------
    units : dict
        Dicionário de unidades indexadas por código
    config_path : str
        Caminho para o arquivo de configuração das unidades
    """
    
    def __init__(self, config_path=None):
        """
        Inicializa o repositório de unidades.
        
        Parameters
        ----------
        config_path : str, optional
            Caminho para o arquivo de configuração das unidades
        """
        self.units = {}
        self.config_path = config_path or resource_path('config/units_config.json')
        self.load_from_config()
    
    def load_from_config(self):
        """
        Carrega as unidades a partir do arquivo de configuração.
        
        Returns
        -------
        bool
            True se as unidades foram carregadas com sucesso, False caso contrário
        """
        try:
            logger.info(f"Carregando a configuração das unidades de {self.config_path}")
            with open(self.config_path, 'r', encoding='utf-8') as file:
                units_config = json.load(file)
                
            for unit_code, unit_data in units_config.items():
                unit = Unit(
                    code=unit_code,
                    name=unit_data.get('name', ''),
                    wings=unit_data.get('wings', [])
                )
                self.add(unit)
                
            logger.info(f"Configuração das unidades carregada com sucesso. {len(self.units)} unidades carregadas.")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar a configuração das unidades: {str(e)}")
            return False
    
    def add(self, unit):
        """
        Adiciona uma unidade ao repositório.
        
        Parameters
        ----------
        unit : Unit
            Unidade a ser adicionada
        """
        self.units[unit.code] = unit
        logger.debug(f"Unidade adicionada: {unit.code}")
    
    def get_by_code(self, code):
        """
        Obtém uma unidade pelo código.
        
        Parameters
        ----------
        code : str
            Código da unidade
            
        Returns
        -------
        Unit or None
            Unidade com o código especificado ou None se não encontrada
        """
        return self.units.get(code)
    
    def get_all(self):
        """
        Obtém todas as unidades do repositório.
        
        Returns
        -------
        dict
            Dicionário de todas as unidades indexadas por código
        """
        return self.units
    
    def get_unit_names(self):
        """
        Obtém os nomes de todas as unidades.
        
        Returns
        -------
        list
            Lista com os nomes das unidades
        """
        return [unit.name for unit in self.units.values()]
    
    def get_unit_codes(self):
        """
        Obtém os códigos de todas as unidades.
        
        Returns
        -------
        list
            Lista com os códigos das unidades
        """
        return list(self.units.keys())
    
    def clear(self):
        """Limpa o repositório de unidades."""
        self.units = {}
        logger.debug("Repositório de unidades limpo.") 