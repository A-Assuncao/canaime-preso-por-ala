import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
import itertools
import time
import logging
import threading
import sys
import os

from multiprocessing import Process, Queue, Event
from queue import Empty

# Configurar paths do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
utils_path = os.path.join(BASE_DIR, 'utils')
config_path = os.path.join(BASE_DIR, 'config')

if utils_path not in sys.path:
    sys.path.append(utils_path)
if config_path not in sys.path:
    sys.path.append(config_path)

try:
    from paths import setup_project_paths
    setup_project_paths()
    from config import APP_VERSION
    from logger import Logger
except ImportError as e:
    # Fallback para definições básicas
    APP_VERSION = "v0.2.2"
    
    class Logger:
        @staticmethod
        def get_logger():
            return logging.getLogger("CanaimeApp")

# URL de login do sistema Canaimé (não mais usada diretamente aqui)
# URL_LOGIN_CANAIME = 'https://canaime.com.br/sgp2rr/login/login_principal.php'

logger = Logger.get_logger()

class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.tag_config('info', foreground='#add8e6') # Light blue
        self.text_widget.tag_config('warning', foreground='#ffa500') # Orange
        self.text_widget.tag_config('error', foreground='#ff4500') # Red-orange
        self.text_widget.tag_config('critical', foreground='#dc143c') # Crimson
        self.text_widget.tag_config('debug', foreground='#90ee90') # Light green

    def emit(self, record):
        msg = self.format(record)
        # Adiciona a mensagem com uma tag baseada no nível do log
        self.text_widget.insert(tk.END, msg + '\n', record.levelname.lower())
        self.text_widget.yview(tk.END) # Auto-scroll

class LoginApp:
    def __init__(self, root, headless, process_task_func):
        self.root = root
        self.login_successful = False
        self.frames = itertools.cycle(["◐", "◓", "◑", "◒"])
        self.animation_running = False
        self.headless = headless
        self.process_task_func = process_task_func # Function from main.py to run in separate process
        self.process_queue = Queue() # Queue for communication from child process
        self.process_stop_event = Event() # Event to signal child process to stop

        self.root.title(f"Planilha PAMC {APP_VERSION}")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E2C44")  # Cor de fundo azul escuro

        self.center_window()
        self.create_widgets()
        self.bind_events()

        # Add the custom handler to the logger
        # self.log_handler = LogHandler(self.log_text)
        # logger.addHandler(self.log_handler)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main Frame
        main_frame = tk.Frame(self.root, bg="#1E2C44")
        main_frame.pack(pady=50, padx=40, fill="both", expand=True)

        # Logo Placeholder (you would replace this with an actual image)
        logo_label = tk.Label(
            main_frame,
            text="👮",  # Placeholder icon
            font=('Segoe UI', 60),
            fg="#FFD700", # Gold color
            bg="#1E2C44"
        )
        logo_label.pack(pady=(0, 20))

        # Title
        title_label = tk.Label(
            main_frame,
            text="LOGIN CANAIMÉ",
            font=('Segoe UI', 24, 'bold'),
            fg="#FFFFFF",  # White color
            bg="#1E2C44"
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text=f"Planilha PAMC {APP_VERSION}",
            font=('Segoe UI', 9),
            fg="#FFFFFF",
            bg="#1E2C44",
            anchor="e"  # Align to right
        )
        subtitle_label.pack(fill="x", padx=5, pady=(0, 30))

        # Username Entry
        self.username_entry = tk.Entry(
            main_frame,
            font=('Segoe UI', 12),
            bg="#2B3C57",  # Darker blue for entry
            fg="#FFFFFF",
            insertbackground="#FFFFFF",  # White cursor
            relief="flat",
            highlightbackground="#2B3C57",
            highlightthickness=1,
            bd=0 # Remove border
        )
        self.username_entry.pack(pady=(0, 20), fill="x", padx=15)
        self.set_placeholder(self.username_entry, " Usuário")
        self.username_entry.bind("<FocusIn>", lambda e: self.on_entry_focus_in(self.username_entry, " Usuário"))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_entry_focus_out(self.username_entry, " Usuário"))

        # Password Entry
        self.password_entry = tk.Entry(
            main_frame,
            font=('Segoe UI', 12),
            bg="#2B3C57",
            fg="#FFFFFF",
            show="*",
            insertbackground="#FFFFFF",
            relief="flat",
            highlightbackground="#2B3C57",
            highlightthickness=1,
            bd=0 # Remove border
        )
        self.password_entry.pack(pady=(0, 40), fill="x", padx=15)
        self.set_placeholder(self.password_entry, " Senha")
        self.password_entry.bind("<FocusIn>", lambda e: self.on_entry_focus_in(self.password_entry, " Senha", is_password=True))
        self.password_entry.bind("<FocusOut>", lambda e: self.on_entry_focus_out(self.password_entry, " Senha", is_password=True))

        # Login Button
        self.login_button = tk.Button(
            main_frame,
            text="Login",
            font=('Segoe UI', 14, 'bold'),
            bg="#1A73E8",  # Blue color as in image
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.iniciar_login,
            activebackground="#155CBF",
            pady=10
        )
        self.login_button.pack(pady=(0, 20), fill="x")
        
        # Status Frame para mostrar logs e status
        status_frame = tk.Frame(main_frame, bg="#2B3C57", bd=1, relief="solid")
        status_frame.pack(pady=10, fill="both", expand=True)
        
        # Status Text para mostrar logs
        self.status_text = tk.Text(
            status_frame,
            wrap='word',
            font=('Consolas', 9),
            bg='#2B3C57',
            fg='#FFFFFF',
            relief='flat',
            bd=0,
            insertbackground='#FFFFFF',
            height=6
        )
        self.status_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar para o Status Text
        status_scrollbar = tk.Scrollbar(status_frame, command=self.status_text.yview)
        status_scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        
        # Configurar o handler de log para o status_text
        self.log_handler = LogHandler(self.status_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(self.log_handler)

    def bind_events(self):
        self.root.bind('<Return>', lambda event: self.iniciar_login()) # Bind Enter key to login

    def set_placeholder(self, entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.config(fg='gray')

    def on_entry_focus_in(self, entry, placeholder_text, is_password=False):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='white')
            if is_password:
                entry.config(show='*')
        entry.config(highlightbackground="#1A73E8") # Highlight on focus

    def on_entry_focus_out(self, entry, placeholder_text, is_password=False):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')
            if is_password:
                entry.config(show='')
        entry.config(highlightbackground="#2B3C57") # Default color when not focused

    def iniciar_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Handle placeholder text
        if username == " Usuário":
            username = ""
        if password == " Senha":
            password = ""

        if not username or not password:
            self.add_status_message("ERRO: Por favor, insira o usuário e a senha.")
            return

        # Limpar o status text e mostrar mensagem de início
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')
        self.add_status_message("Iniciando processo de login...")

        self.login_button.config(state=tk.DISABLED)
        self.animation_running = True

        logger.info("Iniciando processo de login...")

        try:
            # Iniciar o processo em segundo plano
            p = Process(target=self.process_task_func,
                        args=(self.headless, self.process_queue, self.process_stop_event, username, password))
            p.start()
            
            self.root.after(100, self.verificar_fila)
        except Exception as e:
            error_msg = f"Erro ao iniciar processo: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.add_status_message(f"ERRO: {error_msg}")
            self.login_button.config(state=tk.NORMAL)
            self.animation_running = False

    def animar_bolinha(self):
        # Função de animação removida do novo layout
        pass

    def verificar_fila(self):
        if not self.process_stop_event.is_set():
            try:
                message_type, *message_content = self.process_queue.get_nowait()
                
                if message_type == "log":
                    log_message = message_content[0]
                    logger.info(log_message) # Logs from child process
                    self.add_status_message(log_message)
                elif message_type == "success":
                    self.login_successful = True
                    self.finalizar_processo("Sucesso", message_content[0])
                elif message_type == "exit_app":
                    # Encerrar completamente a aplicação
                    self.add_status_message(message_content[0])
                    self.root.after(500, self.encerrar_aplicativo)
                elif message_type == "error":
                    self.finalizar_processo("Erro", message_content[0], message_content[1])
                elif message_type == "status":
                    # Mensagem de status sem ser log
                    self.add_status_message(message_content[0])
            except Empty:
                # Sem mensagens ainda, continuar verificando
                pass
            except Exception as e:
                error_msg = f"Erro ao processar mensagem da fila: {e}"
                logger.error(error_msg, exc_info=True)
                self.add_status_message(f"ERRO: {error_msg}")
            finally:
                self.root.after(100, self.verificar_fila)
        else:
            # Processo terminou, mas pode ter sucesso sem mensagem final ou erro já tratado
            self.finalizar_processo("", "") # Call to clean up UI

    def finalizar_processo(self, title, message, traceback_text=None):
        self.login_button.config(state=tk.NORMAL)
        self.animation_running = False

        if title == "Sucesso":
            self.add_status_message(f"SUCESSO: {message}")
            # O encerramento será tratado pelo sinal exit_app
        elif title == "Erro":
            self.add_status_message(f"ERRO: {message}")
            if traceback_text:
                # Mostra o erro detalhado no status
                self.add_status_message("Detalhes do erro:")
                self.add_status_message(traceback_text[:500] + "..." if len(traceback_text) > 500 else traceback_text)
        
        # Remove o handler de log ao finalizar
        if hasattr(self, 'log_handler') and self.log_handler in logger.handlers:
            logger.removeHandler(self.log_handler)

    def encerrar_aplicativo(self):
        """Encerra o aplicativo completamente após o sucesso"""
        # Ensure the child process is terminated if still running
        if not self.process_stop_event.is_set():
            self.process_stop_event.set()
            logger.info("Encerrando processos em segundo plano...")
        
        # Encerrar a aplicação completamente
        logger.info("Encerrando aplicação...")
        self.root.destroy()
        import sys
        sys.exit(0)  # Força o encerramento completo do programa

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Você deseja sair da aplicação?"):
            self.encerrar_aplicativo()

    def add_status_message(self, message):
        """Adiciona uma mensagem ao status_text e faz scroll para o final"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
