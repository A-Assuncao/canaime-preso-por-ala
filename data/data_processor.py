import json
from playwright.sync_api import Page
from utils.resource_manager import resource_path
import logging

logger = logging.getLogger(__name__)


class UnitProcessor:
    def __init__(self, page: Page):
        self.page = page
        self.units_config = self.load_units_config()

    def load_units_config(self):
        """
        Carrega a configuração das unidades a partir do arquivo JSON.

        Returns
        -------
        dict
            Dicionário com a configuração das unidades, ou um dicionário vazio em caso de falha.
        """
        try:
            # Supondo que você esteja carregando o config/units_config.json:
            units_config_path = resource_path('config/units_config.json')
            logger.info(f"Carregando a configuração das unidades de {units_config_path}")

            # Use-o assim ao carregar o arquivo:
            with open(units_config_path, 'r', encoding='utf-8') as file:
                units_config = json.load(file)
                logger.info("Configuração das unidades carregada com sucesso.")
                return units_config

        except FileNotFoundError:
            logger.error(f"Arquivo de configuração não encontrado: {units_config_path}")
            return {}

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar o JSON: {e}")
            return {}

    def map_prisoner_data(self, unit_config, wing, cell, code, inmate):
        """
        Mapeia os dados do preso para a estrutura da unidade conforme definida no JSON de configuração.

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
        return None

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

        # Carregar a configuração para a unidade específica
        unit_config = self.units_config.get(unit, {})
        if not unit_config:
            logger.warning(f"Configuração para a unidade {unit} não encontrada.")
            return {}

        logger.info(f"Processando a unidade {unit}.")

        # Carregar a página e coletar os elementos necessários
        self.page.goto(
            f'https://canaime.com.br/sgp2rr/areas/impressoes/UND_ChamadaFOTOS_todos2.php?id_und_prisional={unit}',
            timeout=0
        )
        all_entries = self.page.locator('.titulobkSingCAPS')
        names = self.page.locator('.titulobkSingCAPS .titulo12bk')

        count = all_entries.count()
        logger.info(f"Total de entradas encontradas: {count}")

        for i in range(count):
            processed_entry = all_entries.nth(i).text_content().replace(" ", "").strip()
            [code, _, _, _, wing_cell] = processed_entry.split('\n')
            inmate = names.nth(i).text_content().strip()
            wing_cell = wing_cell.replace("ALA:", "")
            split_index = wing_cell.rfind('/')
            wing = wing_cell[:split_index].strip()
            cell = wing_cell[split_index + 1:].strip()

            # Adicionar os dados brutos à lista raw
            raw_unit_list.append({
                "Wing": wing,
                "Cell": cell,
                "Code": code[2:],  # Remover os dois primeiros caracteres do código
                "Inmate": inmate
            })

            # Usar a função de mapeamento para formatar os dados corretamente
            formatted_data = self.map_prisoner_data(unit_config, wing, cell, code[2:], inmate)
            if formatted_data:
                mapped_unit_list.append(formatted_data)

        return {unit: mapped_unit_list}
