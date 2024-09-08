from playwright.sync_api import sync_playwright
from data.data_processor import UnitProcessor
from services.canaime_service import CanaimeLogin
from utils.logger import Logger

logger = Logger.get_logger()


def execute_playwright_task(headless, login, password, selected_units):
    logger.info("Executando tarefa do Playwright.")
    try:
        with sync_playwright() as p:
            # Inicializar a classe de login e realizar o login
            login_handler = CanaimeLogin(p, headless=headless, login=login, password=password)
            page, browser = login_handler.perform_login()  # Obtém a página e o navegador

            # Instanciar o UnitProcessor com a página logada
            unit_processor = UnitProcessor(page)

            # Inicializar dicionário para armazenar dados de todas as unidades
            all_units_data = {}

            # Iterar sobre as unidades selecionadas e coletar dados
            try:
                for unit in selected_units:
                    logger.debug(f"Processando unidade: {unit}")
                    try:
                        unit_data = unit_processor.create_unit_list(unit)
                        all_units_data.update(unit_data)
                        logger.debug(f"Dados da unidade {unit}: {unit_data}")
                    except Exception as e:
                        logger.error(f"Erro ao processar unidade {unit}: {str(e)}")
                        Logger.capture_error(e)
            finally:
                browser.close()  # Garante que o navegador será fechado
    except Exception as e:
        logger.error(f"Erro no Playwright: {str(e)}")
        Logger.capture_error(e)

    return all_units_data
