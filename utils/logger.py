import logging
import traceback
import requests
import platform
import socket
import psutil
import os

class Logger:
    _initialized = False
    _logger = None
    WEBHOOK_URL = ("https://discord.com/api/webhooks/1320799823707766814/"
                   "FIaVMJ3FoRIn3VcFa1cwCfB0mMnylomZCEFX1NcxdWERwmyQCQ6UxuypzIKgDTpXZaoe")

    @staticmethod
    def get_logger(log_file_path=None, level=logging.INFO):
        if not Logger._initialized:
            Logger._logger = logging.getLogger("CanaimeApp")
            Logger._logger.setLevel(level)

            # Configurar o manipulador de arquivo
            if log_file_path is None:
                log_file_path = os.path.join(os.getcwd(), 'app_log.log')

            handler = logging.FileHandler(log_file_path, encoding='utf-8')
            handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            Logger._logger.addHandler(handler)

            Logger._initialized = True
        return Logger._logger

    @staticmethod
    def capture_error(error: Exception):
        logger = Logger.get_logger()
        error_message = f"Erro capturado: {str(error)}"
        traceback_message = traceback.format_exc()

        # Obter informações do sistema
        system_info = Logger.get_system_info()

        detailed_log = f'{error_message}\nTraceback:\n{traceback_message}\n\nInformações do Sistema:\n{system_info}'
        logger.error(detailed_log)

        # Enviar para o Discord
        Logger.send_to_discord(detailed_log)

    @staticmethod
    def send_to_discord(message):
        try:
            data = {"content": f"Log de Erro:\n```{message}```"}
            response = requests.post(Logger.WEBHOOK_URL, json=data)
            if response.status_code == 204:
                print("Log enviado com sucesso para o Discord.")
            else:
                print(f"Falha ao enviar log para Discord: {response.status_code}")
        except Exception as e:
            print(f"Erro ao enviar log para o Discord: {e}")

    @staticmethod
    def get_system_info():
        """Obtém informações detalhadas do sistema."""
        try:
            system_info = {
                "Sistema Operacional": platform.system(),
                "Versão do SO": platform.version(),
                "Nome do Computador": socket.gethostname(),
                "Endereço IP": socket.gethostbyname(socket.gethostname()),
                "Processador": platform.processor(),
                "Arquitetura": platform.architecture()[0],
                "Plataforma": platform.platform(),
                "Memória Total": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
                "Memória Disponível": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
                "Uso de CPU": f"{psutil.cpu_percent()}%",
                "Número de Núcleos": psutil.cpu_count(logical=True),
                "Discos": "; ".join([f"{part.device} ({psutil.disk_usage(part.mountpoint).total / (1024 ** 3):.2f} GB)"
                                     for part in psutil.disk_partitions()])
            }
            return "\n".join([f"{key}: {value}" for key, value in system_info.items()])
        except Exception as e:
            return f"Erro ao coletar informações do sistema: {e}"

if __name__ == "__main__":
    try:
        # Simular um erro para teste
        raise ValueError("Este é um erro de teste para o Discord.")
    except Exception as e:
        Logger.capture_error(e)
