from playwright.sync_api import sync_playwright
from data.data_processor import UnitProcessor
from services.canaime_service import CanaimeLogin
from utils.logger import Logger

logger = Logger.get_logger()


def execute_playwright_task(headless, login, password, selected_units, use_https=True):
    logger.info("Executando tarefa do Playwright.")
    try:
        with sync_playwright() as p:
            # Inicializar a classe de login e realizar o login
            login_handler = CanaimeLogin(p, headless=headless, login=login, password=password, use_https=use_https)
            try:
                page, browser = login_handler.perform_login()  # Obtém a página e o navegador
            except Exception as e:
                logger.error(f"Erro durante o login: {str(e)}", exc_info=True)
                raise Exception(f"Falha ao conectar com o site. Detalhes: {str(e)}")

            # Instanciar o UnitProcessor com a página logada
            unit_processor = UnitProcessor(page, use_https=use_https)

            # Inicializar dicionário para armazenar dados de todas as unidades
            all_units_data = {}

            # Iterar sobre as unidades selecionadas e coletar dados
            try:
                for unit in selected_units:
                    logger.info(f"Processando unidade: {unit}")
                    try:
                        unit_data = unit_processor.create_unit_list(unit)
                        all_units_data.update(unit_data)
                        logger.debug(f"Dados da unidade {unit}: {unit_data}")
                    except Exception as e:
                        logger.error(f"Erro ao processar unidade {unit}: {str(e)}", exc_info=True)
                        Logger.capture_error(e)
            finally:
                browser.close()  # Garante que o navegador será fechado
    except Exception as e:
        logger.error(f"Erro no Playwright: {str(e)}", exc_info=True)
        Logger.capture_error(e)
        raise Exception(f"Erro ao executar tarefa: {str(e)}")

    logger.info(f"Dados de {unit} capturados.")

    return all_units_data
