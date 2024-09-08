import logging
import os
import traceback

class Logger:
    _initialized = False  # Verifica se o logger já foi configurado
    _logger = None  # Instância de logger

    @staticmethod
    def get_logger():
        if not Logger._initialized:
            Logger._logger = logging.getLogger("CanaimeApp")
            Logger._logger.setLevel(logging.INFO)

            # Definir o caminho absoluto para o arquivo de log
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_file = os.path.join(base_dir, 'data', 'processed', 'app_log.log')

            # Criar o diretório se não existir
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            Logger._logger.addHandler(handler)
            Logger._initialized = True  # Marcar como inicializado
        return Logger._logger

    @staticmethod
    def capture_error(error: Exception, open_log: bool = False) -> None:
        logger = Logger.get_logger()
        error_message = f'Ocorreu um erro: {str(error)}'
        traceback_message = traceback.format_exc()

        logger.error(f'{error_message}\nTraceback:\n{traceback_message}')

        if open_log:
            os.startfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'processed', 'app_log.log'))
