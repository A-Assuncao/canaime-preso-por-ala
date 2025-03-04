"""
Entidade Unit (Unidade).

Representa uma unidade prisional no sistema Canaimé.
"""


class Unit:
    """
    Classe que representa uma unidade prisional no sistema.
    
    Attributes
    ----------
    code : str
        Código único da unidade
    name : str
        Nome da unidade
    wings : list
        Lista de alas da unidade
    """
    
    def __init__(self, code, name, wings=None):
        """
        Inicializa um objeto Unit.
        
        Parameters
        ----------
        code : str
            Código único da unidade
        name : str
            Nome da unidade
        wings : list, optional
            Lista de alas da unidade
        """
        self.code = code
        self.name = name
        self.wings = wings or []
    
    def __str__(self):
        """Representação em string da unidade."""
        return f"Unit({self.code}: {self.name})"
    
    def to_dict(self):
        """
        Converte o objeto em um dicionário.
        
        Returns
        -------
        dict
            Representação da unidade como dicionário
        """
        return {
            'code': self.code,
            'name': self.name,
            'wings': self.wings
        } 