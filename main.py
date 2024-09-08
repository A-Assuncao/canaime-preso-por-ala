import itertools
import sys
import tkinter as tk
from multiprocessing import Process, Queue, Event
from queue import Empty

from gui.login.login_canaime import executar_login
from gui.selectors.unit_selector import select_units
from services.playwright_service import execute_playwright_task
from services.report_service import create_excel_report
from utils import updater
from utils.logger import Logger

current_version = 'v0.1.0'  # Versão atual do aplicativo

logger = Logger.get_logger()  # Obter o logger configurado


def process_task(headless, queue, stop_event, login, password, selected_units):
    """
    Função para ser executada no processo separado, executa as tarefas necessárias usando Playwright.
    """
    try:
        # Execute Playwright tasks e obtenha os dados
        all_units_data = execute_playwright_task(headless, login, password, selected_units)
        queue.put("Processo Completo.")

        if all_units_data:
            # Verificar se há dados para cada unidade
            if any(len(unit_data) > 0 for unit_data in all_units_data.values()):
                create_excel_report(all_units_data)
                queue.put("Arquivo salvo com sucesso.")
            else:
                queue.put("Nenhum dado válido encontrado para gerar o relatório.")
        else:
            queue.put("Nenhum dado processado.")
    except Exception as e:
        queue.put(f"Erro: {str(e)}")
    finally:
        stop_event.set()  # Sinaliza que o processo terminou


class StatusApp:
    def __init__(self, root, headless, login, password, selected_units):
        self.root = root
        self.headless = headless
        self.login = login
        self.password = password
        self.selected_units = selected_units
        self.frames = itertools.cycle(["◐", "◓", "◑", "◒"])
        self.queue = Queue()  # Fila para comunicação entre processos
        self.stop_event = Event()  # Evento para sinalizar a parada do processo

        self.root.title("Status")
        largura_janela = 300
        altura_janela = 60
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        self.root.attributes('-topmost', True)

        self.label_status = tk.Label(root, text="")
        self.label_status.pack(pady=10)

        self.rodando = True
        self.iniciar_animacao()
        self.root.after(100, self.executar_tarefas)

        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    def iniciar_animacao(self):
        self.root.after(0, self.animar_bolinha)

    def animar_bolinha(self):
        if not self.rodando:
            return
        frame = next(self.frames)
        self.label_status.config(text=f"Executando ações... {frame}")
        self.root.after(200, self.animar_bolinha)

    def executar_tarefas(self):
        p = Process(target=process_task,
                    args=(self.headless, self.queue, self.stop_event, self.login, self.password, self.selected_units))
        p.start()
        self.root.after(100, self.verificar_fila)

    def verificar_fila(self):
        if not self.stop_event.is_set():
            try:
                message = self.queue.get_nowait()
                self.atualizar_status(message)
            except Empty:
                logger.debug("Fila vazia, aguardando novas mensagens.")
            except Exception as e:
                logger.error(f"Erro ao verificar a fila: {e}", exc_info=True)
            finally:
                self.root.after(100, self.verificar_fila)
        else:
            self.rodando = False
            self.fechar()

    def atualizar_status(self, mensagem):
        self.label_status.config(text=mensagem)

    def fechar(self):
        self.rodando = False
        self.root.withdraw()
        self.root.quit()


def main(headless: bool = True) -> None:
    logger.info("Aplicação iniciada.")
    login, password = executar_login()
    if not login or not password:
        logger.warning("Login não efetuado. Encerrando.")
        return

    selected_units = select_units()
    logger.debug(f"Unidades selecionadas: {selected_units}")

    if not selected_units:
        logger.warning("Nenhuma unidade selecionada. Encerrando.")
        return

    try:
        root = tk.Tk()
        StatusApp(root, headless, login, password, selected_units)
        root.mainloop()
    except Exception as e:
        logger.error(f"Erro durante o main loop: {str(e)}", exc_info=True)
    finally:
        logger.info("Aplicação finalizada.")


if __name__ == '__main__':
    import multiprocessing

    multiprocessing.freeze_support()

    logger.info("Verificando atualizações.")
    if updater.update_application(current_version):
        logger.info("Aplicação atualizada. Reiniciando.")
        sys.exit(0)
    main(headless=True)
