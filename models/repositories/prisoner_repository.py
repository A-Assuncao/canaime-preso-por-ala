"""
Repositório de Prisioneiros.

Gerencia o acesso e manipulação dos dados de prisioneiros.
"""
from models.entities.prisoner import Prisoner
from utils.logger import Logger

logger = Logger.get_logger()


class PrisonerRepository:
    """
    Classe responsável por gerenciar os dados de prisioneiros.
    
    Attributes
    ----------
    prisoners : dict
        Dicionário de prisioneiros indexados por código
    """
    
    def __init__(self):
        """Inicializa o repositório de prisioneiros."""
        self.prisoners = {}
    
    def add(self, prisoner):
        """
        Adiciona um prisioneiro ao repositório.
        
        Parameters
        ----------
        prisoner : Prisoner
            Prisioneiro a ser adicionado
        """
        self.prisoners[prisoner.code] = prisoner
        logger.debug(f"Prisioneiro adicionado: {prisoner.code}")
    
    def get_by_code(self, code):
        """
        Obtém um prisioneiro pelo código.
        
        Parameters
        ----------
        code : str
            Código do prisioneiro
            
        Returns
        -------
        Prisoner or None
            Prisioneiro com o código especificado ou None se não encontrado
        """
        return self.prisoners.get(code)
    
    def get_by_unit(self, unit):
        """
        Obtém todos os prisioneiros de uma unidade.
        
        Parameters
        ----------
        unit : str
            Código da unidade
            
        Returns
        -------
        dict
            Dicionário de prisioneiros da unidade indexados por código
        """
        return {code: prisoner for code, prisoner in self.prisoners.items() 
                if prisoner.unit == unit}
    
    def get_by_unit_and_wing(self, unit, wing):
        """
        Obtém todos os prisioneiros de uma unidade e ala.
        
        Parameters
        ----------
        unit : str
            Código da unidade
        wing : str
            Código da ala
            
        Returns
        -------
        dict
            Dicionário de prisioneiros da unidade e ala indexados por código
        """
        return {code: prisoner for code, prisoner in self.prisoners.items() 
                if prisoner.unit == unit and prisoner.wing == wing}
    
    def get_all(self):
        """
        Obtém todos os prisioneiros do repositório.
        
        Returns
        -------
        dict
            Dicionário de todos os prisioneiros indexados por código
        """
        return self.prisoners
    
    def clear(self):
        """Limpa o repositório de prisioneiros."""
        self.prisoners = {}
        logger.debug("Repositório de prisioneiros limpo.") 