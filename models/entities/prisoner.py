"""
Entidade Prisoner (Prisioneiro).

Representa um prisioneiro no sistema Canaimé.
"""


class Prisoner:
    """
    Classe que representa um prisioneiro no sistema.
    
    Attributes
    ----------
    code : str
        Código único do prisioneiro
    name : str
        Nome do prisioneiro
    cell : str
        Cela onde o prisioneiro está alocado
    wing : str
        Ala onde o prisioneiro está alocado
    unit : str
        Unidade onde o prisioneiro está alocado
    situation : str, optional
        Situação atual do prisioneiro
    status : str, optional
        Status atual do prisioneiro
    """
    
    def __init__(self, code, name, cell, wing, unit, situation=None, status=None):
        """
        Inicializa um objeto Prisoner.
        
        Parameters
        ----------
        code : str
            Código único do prisioneiro
        name : str
            Nome do prisioneiro
        cell : str
            Cela onde o prisioneiro está alocado
        wing : str
            Ala onde o prisioneiro está alocado
        unit : str
            Unidade onde o prisioneiro está alocado
        situation : str, optional
            Situação atual do prisioneiro
        status : str, optional
            Status atual do prisioneiro
        """
        self.code = code
        self.name = name
        self.cell = cell
        self.wing = wing
        self.unit = unit
        self.situation = situation
        self.status = status
    
    def __str__(self):
        """Representação em string do prisioneiro."""
        return f"Prisoner({self.code}: {self.name}, {self.unit}/{self.wing}/{self.cell})"
    
    def to_dict(self):
        """
        Converte o objeto em um dicionário.
        
        Returns
        -------
        dict
            Representação do prisioneiro como dicionário
        """
        return {
            'code': self.code,
            'name': self.name,
            'cell': self.cell,
            'wing': self.wing,
            'unit': self.unit,
            'situation': self.situation,
            'status': self.status
        } 