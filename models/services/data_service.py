"""
Serviço de Dados.

Responsável pelo processamento e manipulação de dados relacionados aos prisioneiros.
"""
from models.entities.prisoner import Prisoner
from models.repositories.prisoner_repository import PrisonerRepository
from models.repositories.unit_repository import UnitRepository
from infrastructure.browser.playwright_adapter import PlaywrightAdapter
from utils.logger import Logger

logger = Logger.get_logger()


class DataService:
    """
    Serviço responsável pelo processamento de dados de prisioneiros.
    
    Attributes
    ----------
    unit_repository : UnitRepository
        Repositório de unidades
    prisoner_repository : PrisonerRepository
        Repositório de prisioneiros
    """
    
    def __init__(self, unit_repository=None, prisoner_repository=None):
        """
        Inicializa o serviço de dados.
        
        Parameters
        ----------
        unit_repository : UnitRepository, optional
            Repositório de unidades
        prisoner_repository : PrisonerRepository, optional
            Repositório de prisioneiros
        """
        self.unit_repository = unit_repository or UnitRepository()
        self.prisoner_repository = prisoner_repository or PrisonerRepository()
    
    def normalize_text(self, text):
        """
        Normaliza textos que começam com 'REMI' e terminam com '01' ou '02' para
        'REMIÇÃO01' e 'REMIÇÃO02', independentemente dos caracteres intermediários.

        Parameters
        ----------
        text : str
            Texto a ser normalizado.

        Returns
        -------
        str
            Texto normalizado.
        """
        if text.startswith("REMI") and text.endswith("01"):
            logger.debug(f"Texto normalizado: {text} -> REMIÇÃO01")
            return "REMIÇÃO01"
        elif text.startswith("REMI") and text.endswith("02"):
            logger.debug(f"Texto normalizado: {text} -> REMIÇÃO02")
            return "REMIÇÃO02"
        else:
            return text
    
    def map_prisoner_data(self, unit_code, wing, cell, code, name):
        """
        Mapeia os dados do preso para a estrutura da unidade conforme definida no JSON de configuração.

        Parameters
        ----------
        unit_code : str
            Código da unidade.
        wing : str
            Ala do preso.
        cell : str
            Cela do preso.
        code : str
            Código do preso.
        name : str
            Nome do preso.

        Returns
        -------
        Prisoner or None
            Objeto Prisoner com os dados do preso, ou None se a ala ou cela não estiver definida.
        """
        unit = self.unit_repository.get_by_code(unit_code)
        if not unit:
            logger.warning(f"Unidade {unit_code} não encontrada.")
            return None
        
        # Criar o objeto Prisoner
        prisoner = Prisoner(
            code=code,
            name=name,
            cell=cell,
            wing=wing,
            unit=unit_code
        )
        
        return prisoner
    
    def process_unit_data(self, playwright_adapter, unit_code):
        """
        Processa os dados de uma unidade prisional.
        
        Parameters
        ----------
        playwright_adapter : PlaywrightAdapter
            Adaptador do Playwright para interação com o navegador
        unit_code : str
            Código da unidade prisional
            
        Returns
        -------
        list
            Lista de prisioneiros processados
        """
        logger.info(f"Processando a unidade {unit_code}.")
        processed_prisoners = []
        
        try:
            # Carregar a página e coletar os elementos necessários
            url = f'https://canaime.com.br/sgp2rr/areas/impressoes/UND_ChamadaFOTOS_todos2.php?id_und_prisional={unit_code}'
            playwright_adapter.navigate(url)
            page = playwright_adapter.page
            
            all_entries = page.locator('.titulobkSingCAPS')
            names = page.locator('.titulobkSingCAPS .titulo12bk')
            
            count = all_entries.count()
            logger.info(f"Total de entradas encontradas: {count}")
            
            for i in range(count):
                processed_entry = all_entries.nth(i).text_content().replace(" ", "").strip()
                [code, _, _, _, wing_cell] = processed_entry.split('\n')
                inmate = names.nth(i).text_content().strip()
                wing_cell = wing_cell.replace("ALA:", "")
                split_index = wing_cell.rfind('/')
                wing = self.normalize_text(wing_cell[:split_index].strip())  # Normaliza o texto da ala
                cell = wing_cell[split_index + 1:].strip()
                
                # Usar a função de mapeamento para criar o objeto Prisoner
                prisoner = self.map_prisoner_data(
                    unit_code, 
                    wing, 
                    cell, 
                    code[2:],  # Remover os dois primeiros caracteres do código
                    inmate
                )
                
                if prisoner:
                    self.prisoner_repository.add(prisoner)
                    processed_prisoners.append(prisoner)
                    logger.debug(f"Prisioneiro adicionado: {prisoner.code} - {prisoner.name}")
            
            logger.info(f"Dados da unidade {unit_code} processados com sucesso. Total: {len(processed_prisoners)} prisioneiros.")
            return processed_prisoners
        
        except Exception as e:
            logger.error(f"Erro ao processar dados da unidade {unit_code}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return []
    
    def process_multiple_units(self, headless, login, password, selected_units):
        """
        Processa os dados de múltiplas unidades prisionais.
        
        Parameters
        ----------
        headless : bool
            Indica se o navegador deve ser executado em modo headless
        login : str
            Login para acesso ao sistema
        password : str
            Senha para acesso ao sistema
        selected_units : list
            Lista de códigos das unidades selecionadas
            
        Returns
        -------
        dict
            Dicionário com os dados de todas as unidades processadas
        """
        logger.info(f"Processando {len(selected_units)} unidades: {', '.join(selected_units)}")
        all_units_data = {}
        
        with PlaywrightAdapter(headless=headless) as adapter:
            # Autenticar no sistema
            adapter.navigate("https://canaime.com.br/sgp2rr/login/login_principal.php")
            adapter.fill_form("input[name='usuario']", login)
            adapter.fill_form("input[name='senha']", password)
            adapter.click("input[type='submit']")
            
            # Verificar se o login foi bem-sucedido
            if adapter.get_element_count("img[src*='logo_canaime.jpg']") < 1:
                logger.error("Falha na autenticação. Verifique o login e a senha.")
                return {}
            
            # Processar cada unidade selecionada
            for unit_code in selected_units:
                try:
                    prisoners = self.process_unit_data(adapter, unit_code)
                    if prisoners:
                        # Converter para o formato esperado pelo código atual
                        unit_data = []
                        for prisoner in prisoners:
                            unit_data.append({
                                "Bloco": "",  # Isso será preenchido posteriormente se necessário
                                "Ala": prisoner.wing,
                                "Cela": prisoner.cell,
                                "Código": prisoner.code,
                                "Preso": prisoner.name
                            })
                        all_units_data[unit_code] = unit_data
                except Exception as e:
                    logger.error(f"Erro ao processar unidade {unit_code}: {str(e)}", exc_info=True)
                    Logger.capture_error(e)
        
        return all_units_data 