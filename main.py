import tkinter as tk
import argparse
import sys
import os
import traceback
from tkinter import messagebox, ttk, filedialog
import logging
import multiprocessing
from multiprocessing import Process, Queue, Event
from queue import Empty
import itertools
from openpyxl import Workbook
from datetime import datetime
from config.config import APP_VERSION
from config.run_modes import (
    DEFAULT_RUN_MODE,
    RUN_MODE_CHAMADA,
    RUN_MODE_CONTAGEM,
    RUN_MODE_PLANILHA,
)

# Configurar o diretório raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Importações absolutas
from gui.login.login_canaime import LoginApp
from services.canaime_service import CanaimeLogin
from data.data_processor import UnitProcessor
from utils.updater import check_and_update
from utils.logger import Logger
from utils.pamc_folder_manager import ensure_pamc_folder, copy_file_to_pamc
from config.excel_config_sei import generate_unit_sei_sheet
from config.excel_config_control import generate_unit_control_sheet, calculate_shift

# Configurar o logger para não mostrar dados sensíveis
logger = Logger.get_logger()

def process_task(headless, queue, stop_event, login, password, run_mode, chamada_selected_alas=None):
    """Função para ser executada no processo separado, executa as tarefas necessárias usando requests."""
    try:
        allowed_modes = {RUN_MODE_PLANILHA, RUN_MODE_CHAMADA, RUN_MODE_CONTAGEM}
        if run_mode not in allowed_modes:
            run_mode = DEFAULT_RUN_MODE

        queue.put(("log", "Iniciando o login..."))
        canaime_login_service = CanaimeLogin(headless=headless, login=login, password=password)
        session, _ = canaime_login_service.perform_login()
        queue.put(("log", "Login foi bem sucedido"))

        if run_mode == RUN_MODE_CHAMADA:
            from services.chamada_pdf import build_chamada_pdf

            alist = chamada_selected_alas or []
            if not alist:
                queue.put(("error", "Nenhuma ala selecionada para a chamada.", ""))
                return

            selected_set = {(str(t[0]), str(t[1])) for t in alist if isinstance(t, (list, tuple)) and len(t) == 2}
            if not selected_set:
                queue.put(("error", "Seleção de alas inválida.", ""))
                return

            queue.put(("log", f"Modo Chamada: {len(selected_set)} ala(s) selecionada(s)."))
            preview_parts = [f"{b}/{a}" for b, a in sorted(selected_set)[:15]]
            preview = ", ".join(preview_parts)
            if len(selected_set) > 15:
                preview += ", …"
            queue.put(("log", f"Alas: {preview}"))

            selected_unit = "PAMC"
            queue.put(("log", "Carregando lista geral de presos..."))
            unit_processor = UnitProcessor(session)
            unit_list_processed = unit_processor.create_unit_list(selected_unit)

            if unit_processor.unmapped_count > 0:
                queue.put(
                    (
                        "log",
                        f"Aviso: {unit_processor.unmapped_count} preso(s) não mapeado(s) — não entram na chamada.",
                    )
                )

            rows = unit_list_processed.get(selected_unit, [])
            current_date = datetime.now()
            shift_name = calculate_shift(current_date)
            formatted_date = current_date.strftime("%d%m%Y_%H%M")
            filename = f"Chamada {shift_name} {formatted_date}.pdf"

            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.attributes("-topmost", True)
            temp_root.lift()
            temp_root.focus_force()

            try:
                output_path = filedialog.asksaveasfilename(
                    parent=temp_root,
                    title="Salvar chamada como",
                    defaultextension=".pdf",
                    filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
                    initialfile=filename,
                )
            finally:
                temp_root.destroy()

            if not output_path:
                queue.put(("error", "Salvamento cancelado pelo usuário", ""))
                return

            if not output_path.lower().endswith(".pdf"):
                output_path += ".pdf"

            try:
                n_wings = build_chamada_pdf(
                    output_path,
                    rows,
                    selected_set,
                    unit_label=selected_unit,
                    generated_at=current_date,
                )
            except ValueError as e:
                queue.put(("error", str(e), ""))
                return

            if not os.path.exists(output_path):
                queue.put(("error", "Arquivo PDF não foi criado.", ""))
                return

            file_size = os.path.getsize(output_path)
            queue.put(("log", f"PDF salvo: {os.path.basename(output_path)} ({file_size} bytes), {n_wings} ala(s) com presos."))

            try:
                pamc_copy_path = copy_file_to_pamc(output_path)
                queue.put(("log", f"Cópia salva em: {pamc_copy_path}"))
            except Exception as e:
                queue.put(("log", f"AVISO: Não foi possível salvar cópia na pasta PAMC: {e}"))

            queue.put(("success", "Chamada gerada com sucesso!"))
            queue.put(("exit_app", "Execução concluída. Encerrando aplicação…"))
            stop_event.set()
            return

        if run_mode == RUN_MODE_CONTAGEM:
            from services.contagem_pdf import build_contagem_pdf

            alist = chamada_selected_alas or []
            if not alist:
                queue.put(("error", "Nenhuma ala selecionada para a contagem.", ""))
                return

            selected_set = {(str(t[0]), str(t[1])) for t in alist if isinstance(t, (list, tuple)) and len(t) == 2}
            if not selected_set:
                queue.put(("error", "Seleção de alas inválida.", ""))
                return

            queue.put(("log", f"Modo Contagem: {len(selected_set)} ala(s) selecionada(s)."))
            preview_parts = [f"{b}/{a}" for b, a in sorted(selected_set)[:15]]
            preview = ", ".join(preview_parts)
            if len(selected_set) > 15:
                preview += ", …"
            queue.put(("log", f"Alas: {preview}"))

            selected_unit = "PAMC"
            queue.put(("log", "Carregando lista geral de presos..."))
            unit_processor = UnitProcessor(session)
            unit_list_processed = unit_processor.create_unit_list(selected_unit)

            if unit_processor.unmapped_count > 0:
                queue.put(
                    (
                        "log",
                        f"Aviso: {unit_processor.unmapped_count} preso(s) não mapeado(s) — não entram na agregação por cela.",
                    )
                )

            rows = unit_list_processed.get(selected_unit, [])
            current_date = datetime.now()
            shift_name = calculate_shift(current_date)
            formatted_date = current_date.strftime("%d%m%Y_%H%M")
            filename = f"Contagem {shift_name} {formatted_date}.pdf"

            temp_root = tk.Tk()
            temp_root.withdraw()
            temp_root.attributes("-topmost", True)
            temp_root.lift()
            temp_root.focus_force()

            try:
                output_path = filedialog.asksaveasfilename(
                    parent=temp_root,
                    title="Salvar contagem como",
                    defaultextension=".pdf",
                    filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
                    initialfile=filename,
                )
            finally:
                temp_root.destroy()

            if not output_path:
                queue.put(("error", "Salvamento cancelado pelo usuário", ""))
                return

            if not output_path.lower().endswith(".pdf"):
                output_path += ".pdf"

            try:
                n_blocks = build_contagem_pdf(
                    output_path,
                    rows,
                    selected_set,
                    unit_label=selected_unit,
                    generated_at=current_date,
                )
            except ValueError as e:
                queue.put(("error", str(e), ""))
                return

            if not os.path.exists(output_path):
                queue.put(("error", "Arquivo PDF não foi criado.", ""))
                return

            file_size = os.path.getsize(output_path)
            queue.put(
                ("log", f"PDF salvo: {os.path.basename(output_path)} ({file_size} bytes), {n_blocks} bloco(s) de ala.")
            )

            try:
                pamc_copy_path = copy_file_to_pamc(output_path)
                queue.put(("log", f"Cópia salva em: {pamc_copy_path}"))
            except Exception as e:
                queue.put(("log", f"AVISO: Não foi possível salvar cópia na pasta PAMC: {e}"))

            queue.put(("success", "Contagem gerada com sucesso!"))
            queue.put(("exit_app", "Execução concluída. Encerrando aplicação…"))
            stop_event.set()
            return

        selected_unit = "PAMC"
        queue.put(("log", "Iniciando a lista da PAMC..."))

        unit_processor = UnitProcessor(session)
        unit_list_processed = unit_processor.create_unit_list(selected_unit)
        
        # Validar presos não mapeados antes de continuar
        if unit_processor.unmapped_count > 0:
            logger.info(f"Enviando erro de validação: {unit_processor.unmapped_count} presos não mapeados")
            # Enviar também a lista já mapeada para permitir continuar sem os não mapeados
            queue.put(("validation_error", "Presos não mapeados encontrados", unit_processor.unmapped_prisoners, unit_list_processed))
            # Aguardar um pouco para garantir que a mensagem seja processada
            import time
            time.sleep(0.5)
            # NÃO definir stop_event.set() aqui - deixar a interface processar a mensagem
            return
        
        # Não logar a lista completa, apenas continuar o processo
        num_records = len(unit_list_processed.get(selected_unit, []))
        queue.put(("log", f"Processados {num_records} registros da PAMC"))
        
        # Criar workbook para o Excel
        workbook = Workbook()
        # Remover a aba padrão
        default_sheet = workbook.active
        workbook.remove(default_sheet)
        
        # Importar as funções necessárias do report_service
        from services.report_service import calculate_data, fill_control_sheet, fill_sei_sheet
        import pandas as pd
        
        queue.put(("log", "Preenchendo a aba Controle no excel..."))
        # Gerar aba Controle
        try:
            control_ws = generate_unit_control_sheet(workbook, selected_unit)
            
            # Converter dados para DataFrame e calcular
            if unit_list_processed.get(selected_unit):
                df = pd.DataFrame(unit_list_processed[selected_unit])
                calculated_data = calculate_data(df)
                # Preencher a aba de controle com os dados calculados
                fill_control_sheet(control_ws, calculated_data)
                
        except Exception as e:
            logger.error(f"Erro ao gerar aba Controle: {e}", exc_info=True)
            queue.put(("error", f"Erro ao gerar aba Controle: {e}", traceback.format_exc()))
            raise
        
        queue.put(("log", "Preenchendo a aba SEI no excel..."))
        # Gerar aba SEI
        try:
            sei_ws = generate_unit_sei_sheet(workbook, selected_unit)
            # Preencher a aba SEI com dados da aba Controle
            fill_sei_sheet(sei_ws, control_ws)
            
        except Exception as e:
            logger.error(f"Erro ao gerar aba SEI: {e}", exc_info=True)
            queue.put(("error", f"Erro ao gerar aba SEI: {e}", traceback.format_exc()))
            raise
        
        queue.put(("log", "Salvando arquivo excel..."))
        # Salvar arquivo Excel
        try:
            # Gerar o nome do arquivo com o formato: plantao ddmmaaaa_HHmm.xlsx
            current_date = datetime.now()
            shift_name = calculate_shift(current_date)
            formatted_date = current_date.strftime("%d%m%Y_%H%M")
            filename = f"{shift_name} {formatted_date}.xlsx"
            
            # Criar uma janela temporária para o filedialog
            temp_root = tk.Tk()
            temp_root.withdraw()  # Esconder a janela principal
            temp_root.attributes('-topmost', True)  # Sempre em primeiro plano
            temp_root.lift()  # Trazer para frente
            temp_root.focus_force()  # Forçar o foco
            
            # Mostrar caixa de diálogo para escolher onde salvar
            output_path = filedialog.asksaveasfilename(
                parent=temp_root,
                title="Salvar planilha como",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename
            )
            
            # Destruir a janela temporária
            temp_root.destroy()
            
            if not output_path:  # Usuário cancelou
                queue.put(("error", "Salvamento cancelado pelo usuário", ""))
                return
            
            # Verificar se o workbook tem abas antes de salvar
            if len(workbook.worksheets) == 0:
                raise Exception("Workbook não possui abas válidas")
            
            # Garantir que a extensão seja .xlsx
            if not output_path.lower().endswith('.xlsx'):
                output_path += '.xlsx'
            
            # Salvar o arquivo
            try:
                workbook.save(output_path)
                
            except PermissionError:
                # Se houver erro de permissão, tentar salvar com nome diferente
                base_path = output_path.rsplit('.', 1)[0]
                counter = 1
                while True:
                    alternative_path = f"{base_path}_{counter}.xlsx"
                    try:
                        workbook.save(alternative_path)
                        output_path = alternative_path
                        break
                    except PermissionError:
                        counter += 1
                        if counter > 10:  # Limite de tentativas
                            raise Exception("Não foi possível salvar o arquivo após várias tentativas")
            
            # Verificar se o arquivo foi criado e não está vazio
            if not os.path.exists(output_path):
                raise Exception("Arquivo não foi criado")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("Arquivo criado está vazio")
            elif file_size < 5000:  # Arquivo muito pequeno pode indicar problema
                queue.put(("log", f"AVISO: Arquivo pode estar corrompido (tamanho: {file_size} bytes)"))
            
            queue.put(("log", f"Arquivo salvo como: {os.path.basename(output_path)} ({file_size} bytes)"))
            
            # Copiar o arquivo para a pasta PAMC
            try:
                pamc_copy_path = copy_file_to_pamc(output_path)
                queue.put(("log", f"Cópia salva em: {pamc_copy_path}"))
            except Exception as e:
                queue.put(("log", f"AVISO: Não foi possível salvar cópia na pasta PAMC: {e}"))
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo Excel: {e}", exc_info=True)
            queue.put(("error", f"Erro ao salvar arquivo Excel: {e}", traceback.format_exc()))
            raise
        
        queue.put(("success", "Processamento concluído com sucesso!"))
        
        # Sinal para encerrar completamente a aplicação
        queue.put(("exit_app", "Execução concluída. Encerrando aplicação…"))
        stop_event.set()

    except Exception as e:
        error_message = f"Erro durante o processo: {e}"
        # Enviar erro imediatamente (sem logar o traceback aqui)
        queue.put(("error", str(e), traceback.format_exc()))
        # Aguardar um pouco para garantir que a mensagem seja processada
        import time
        time.sleep(0.1)
        # Não continuar com o finally até que o erro seja processado
        return
    finally:
        queue.put(("log", "Finalizando processo..."))
        stop_event.set()

def main(headless=True):
    """Função principal para executar a aplicação."""
    # Garantir que a pasta PAMC existe ANTES de inicializar o logger
    try:
        pamc_folder = ensure_pamc_folder()
        print(f"Pasta PAMC criada/verificada com sucesso: {pamc_folder}")
    except Exception as e:
        print(f"Erro ao criar pasta PAMC: {e}")
    
    # Iniciar a sessão do logger (que agora usará a pasta PAMC)
    Logger.start_session()
    logger = Logger.get_logger()
    logger.info("Iniciando a aplicação Canaimé...")
    
    # Log da verificação da pasta PAMC
    try:
        logger.info(f"Pasta PAMC verificada: {pamc_folder}")
    except:
        logger.info("Pasta PAMC criada com sucesso")

    parser = argparse.ArgumentParser(description="Canaimé Application")
    parser.add_argument("--skip-update", action="store_true", help="Skip the update check on startup")
    args = parser.parse_args()

    if not args.skip_update:
        try:
            if not check_and_update(APP_VERSION):
                logger.info("O status de atualização automática: Nenhuma atualização disponível")
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")

    login_app = None
    try:
        login_root = tk.Tk()
        login_app = LoginApp(login_root, headless=headless, process_task_func=process_task)
        login_root.mainloop()

    except Exception as e:
        error_message = f"Ocorreu um erro inesperado: {e}"
        logger.critical(error_message, exc_info=True)
        show_error_popup(error_message, traceback.format_exc())
    finally:
        # Finalizar a sessão do logger antes de encerrar
        Logger.end_session()
        # Garantir que o programa seja encerrado completamente
        sys.exit(0)

def show_error_popup(error_message, traceback_text):
    """Exibe uma janela de popup com a mensagem de erro e o traceback."""
    error_window = tk.Toplevel()
    error_window.title("Erro no Programa")
    error_window.geometry("600x400")
    error_window.attributes('-topmost', True)
    error_window.configure(bg='#1b2838')

    title_label = tk.Label(
        error_window,
        text="Um Erro Ocorreu!",
        font=('Segoe UI', 16, 'bold'),
        bg='#1b2838',
        fg='#e74c3c'
    )
    title_label.pack(pady=10)

    msg_label = tk.Label(
        error_window,
        text=error_message,
        font=('Segoe UI', 10),
        bg='#1b2838',
        fg='#ffffff',
        wraplength=550
    )
    msg_label.pack(pady=5)

    traceback_frame = tk.Frame(error_window, bg='#2b3a4a', bd=1, relief="solid")
    traceback_frame.pack(padx=20, pady=10, fill='both', expand=True)

    traceback_text_widget = tk.Text(
        traceback_frame,
        wrap='word',
        font=('Consolas', 9),
        bg='#2b3a4a',
        fg='#e74c3c',
        relief='flat',
        bd=0,
        insertbackground='#ffffff'
    )
    traceback_text_widget.insert(tk.END, traceback_text)
    traceback_text_widget.config(state='disabled')
    traceback_text_widget.pack(side='left', fill='both', expand=True)

    scrollbar = tk.Scrollbar(traceback_frame, command=traceback_text_widget.yview)
    scrollbar.pack(side='right', fill='y')
    traceback_text_widget.config(yscrollcommand=scrollbar.set)

    def copy_to_clipboard():
        error_window.clipboard_clear()
        error_window.clipboard_append(traceback_text)
        messagebox.showinfo("Copiado", "Erro copiado para a área de transferência!", parent=error_window)

    copy_button = tk.Button(
        error_window,
        text="Copiar Erro",
        font=('Segoe UI', 10, 'bold'),
        bg='#3498db',
        fg='white',
        relief='flat',
        cursor='hand2',
        command=copy_to_clipboard,
        activebackground='#287bb8'
    )
    copy_button.pack(pady=10)

    error_window.grab_set()
    error_window.wait_window()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main(headless=False)
