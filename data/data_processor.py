import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import logging

# Configurar paths do projeto
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'))

from resource_manager import resource_path
from units_config import UNITS_CONFIG
from logger import Logger

# Configurar o logger
logger = Logger.get_logger()


class UnitProcessor:
    def __init__(self, session: requests.Session):
        self.session = session
        self.units_config = UNITS_CONFIG
        # Contador para presos não mapeados
        self.unmapped_count = 0
        # Lista para armazenar informações de presos não mapeados
        self.unmapped_prisoners = []

    def map_prisoner_data(self, unit_config, wing, cell, code, inmate):
        """
        Mapeia os dados do preso para a estrutura da unidade conforme definida no arquivo de configuração.

        Parameters
        ----------
        unit_config : dict
            Configuração da unidade.
        wing : str
            Ala do preso.
        cell : str
            Cela do preso.
        code : str
            Código do preso.
        inmate : str
            Nome do preso.

        Returns
        -------
        dict or None
            Dicionário formatado com os dados do preso, ou None se a ala ou cela não estiver definida.
        """
        # Tratar casos especiais PRIMEIRO - PRIS/DOM
        if wing.startswith("PRIS/DOM"):
            return {
                "Bloco": "Externo",
                "Ala": "PRIS/DOM",
                "Cela": cell,
                "Código": code,
                "Preso": inmate
            }
        
        # Processamento normal para alas dos blocos A, B, etc.
        for block_key, block_data in unit_config.get("blocks", {}).items():
            if wing in block_data["alas"]:
                # Se a ala for encontrada, verificar se a cela está listada
                if "celas" in block_data["alas"][wing]:
                    celas_list = block_data["alas"][wing]["celas"]
                    # Permitir adicionar celas em alas que possuem lista vazia
                    if not celas_list or cell in celas_list:
                        return {
                            "Bloco": block_key,
                            "Ala": wing,
                            "Cela": cell,
                            "Código": code,
                            "Preso": inmate
                        }
            
        # Se chegou até aqui, realmente não foi mapeado
        self.unmapped_count += 1
        self.unmapped_prisoners.append({
            "Código": code,
            "Nome": inmate,
            "Ala": wing,
            "Cela": cell
        })
        
        # Usar o logger normal para registrar no app_log.log
        logger.warning(f"Não foi possível mapear os dados do preso {code} - {inmate} ({wing}/{cell})")
        return None

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
        if text and isinstance(text, str):
            if text.startswith("REMI") and text.endswith("01"):
                logger.debug(f"Texto recebido: {text} -> Texto normalizado: REMIÇÃO01")
                return "REMIÇÃO01"
            elif text.startswith("REMI") and text.endswith("02"):
                logger.debug(f"Texto recebido: {text} -> Texto normalizado: REMIÇÃO02")
                return "REMIÇÃO02"
        return text

    def extrair_codigo_preso(self, entry_text, entry_html):
        """
        Extrai o código do preso a partir do texto da entrada
        
        Args:
            entry_text: Texto completo da entrada
            entry_html: HTML da entrada para busca alternativa
            
        Returns:
            str: Código do preso
        """
        # Busca pelo padrão "id XXXX" no texto da entrada
        id_match = re.search(r'id\s+(\d+)', entry_text)
        if id_match:
            return id_match.group(1)
            
        # Se não encontrar pelo padrão "id", procura no primeiro texto da entrada
        # por qualquer número que possa ser o ID
        primeiro_texto = entry_html.get_text().strip().split('\n')[0]
        if primeiro_texto:
            num_match = re.search(r'id\s*(\d+)', primeiro_texto)
            if num_match:
                return num_match.group(1)
                
            # Se ainda não encontrou, procura por qualquer número no primeiro texto
            num_match = re.search(r'(\d+)', primeiro_texto)
            if num_match:
                return num_match.group(1)
        
        # Se ainda não encontrou, tenta outros padrões
        codigo_match = re.search(r'C:(\d+)', entry_text)
        if codigo_match:
            return codigo_match.group(1)
        
        # Procura por sequência alfanumérica no início do texto
        codigo_match = re.search(r'^([A-Z0-9]+)', entry_text)
        if codigo_match:
            # Se começar com "id", remove isso
            codigo = codigo_match.group(1)
            if codigo.lower().startswith('id'):
                codigo = codigo[2:].strip()
            return codigo
                
        # Se nenhum método funcionar, retorna string vazia
        return ""

    def create_unit_list(self, unit: str) -> dict:
        """
        Cria uma lista de dicionários contendo detalhes das alas, celas, códigos e presos para a unidade especificada.

        Parameters
        ----------
        unit : str
            Código da unidade prisional.

        Returns
        -------
        dict
            Dicionário com os dados da unidade.
        """
        raw_unit_list = []  # Lista antes do mapeamento
        mapped_unit_list = []  # Lista após o mapeamento
        
        # Resetar contadores e listas para cada unidade
        self.unmapped_count = 0
        self.unmapped_prisoners = []

        # Carregar a configuração para a unidade específica
        unit_config = self.units_config.get(unit, {})
        if not unit_config:
            logger.warning(f"Configuração para a unidade {unit} não encontrada.")
            return {}

        logger.info(f"Iniciando processamento da unidade {unit}...")

        # Carregar a página e coletar os elementos necessários
        base_url = os.getenv("CANAIME_BASE_URL", "https://canaime.com.br")
        url = f'{base_url}/sgp2rr/areas/impressoes/UND_ChamadaFOTOS_todos2.php?id_und_prisional={unit}'
        logger.info(f"Acessando URL: {url}")
        
        try:
            response = self.session.get(url, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("Página carregada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao acessar a página: {str(e)}", exc_info=True)
            raise Exception(f"Não foi possível acessar a página da unidade. Erro: {str(e)}")

        # Localiza todas as tabelas que contêm os dados dos presos
        inmate_tables = soup.select('table[width="700"][border="1"]')
        count = len(inmate_tables)
        logger.info(f"Total de presos encontrados: {count}")

        for table in inmate_tables:
            try:
                # Busca a célula com os dados do preso
                data_cell = table.select_one('.titulobkSingCAPS')
                if not data_cell:
                    logger.warning("Célula com dados do preso não encontrada")
                    continue

                # Obtém o nome do preso
                name_element = data_cell.select_one('.titulo12bk')
                inmate = name_element.text.strip() if name_element else ""

                # Obtém o texto completo da entrada e processa
                entry_text = ''.join(data_cell.stripped_strings).replace(" ", "")

                # Extrai o código do preso
                code = self.extrair_codigo_preso(entry_text, data_cell)

                # Extrai a informação de ala/cela
                # Regex melhorada para capturar alas que contêm "/" como PRIS/DOM
                wing_cell_match = re.search(r'ALA:(PRIS/DOM|[^/]+)/(.+?)(?=\s|$)', entry_text)
                
                if wing_cell_match:
                    raw_wing = wing_cell_match.group(1).strip()
                    wing = self.normalize_text(raw_wing)
                    cell = wing_cell_match.group(2).strip()



                    # Adicionar os dados brutos à lista raw
                    raw_unit_list.append({
                        "Wing": wing,
                        "Cell": cell,
                        "Code": code,
                        "Inmate": inmate
                    })
                    logger.debug(f"Processado preso {code} - {inmate} ({wing}/{cell})")

                    # Usar a função de mapeamento para formatar os dados corretamente
                    formatted_data = self.map_prisoner_data(unit_config, wing, cell, code, inmate)
                    if formatted_data:
                        mapped_unit_list.append(formatted_data)
                        logger.debug(f"Dados mapeados para o preso {code}")
                else:
                    logger.warning(f"Formato inesperado para entrada: {entry_text}")

            except Exception as e:
                logger.error(f"Erro ao processar preso: {str(e)}", exc_info=True)
                continue

        # Log do total de presos não mapeados
        if self.unmapped_count > 0:
            logger.warning(f"ATENÇÃO: {self.unmapped_count} presos não mapeados encontrados!")
            logger.warning("Lista de presos não mapeados:")
            for i, prisoner in enumerate(self.unmapped_prisoners, 1):
                logger.warning(f"  {i}. Código: {prisoner['Código']} | Nome: {prisoner['Nome']} | Ala: {prisoner['Ala']} | Cela: {prisoner['Cela']}")
            logger.warning("O programa será interrompido para corrigir estes problemas.")

        logger.info(f"Processamento concluído. Total de presos processados: {len(mapped_unit_list)}")
        return {unit: mapped_unit_list}

    def process_unit(self, unit: str) -> None:
        """
        Processa uma unidade específica.

        Parameters
        ----------
        unit : str
            Código da unidade prisional.
        """
        try:
            # Obtém os dados da unidade
            logger.info(f"Iniciando processamento da unidade {unit} em process_unit...")
            
            # Como create_unit_list já foi chamado anteriormente, não precisamos chamar novamente
            # Apenas usar os dados que já foram processados
            logger.info(f"Processamento da unidade {unit} concluído com sucesso")
            logger.info(f"Resumo do processamento em process_unit:")
            logger.info(f"  - Total de registros não mapeados: {self.unmapped_count}")
            
        except Exception as e:
            logger.error(f"Erro ao processar unidade {unit} em process_unit: {str(e)}", exc_info=True)
            raise Exception(f"Erro ao processar unidade {unit}: {str(e)}")
