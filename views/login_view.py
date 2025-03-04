"""
View de Login.

Interface gráfica para autenticação do usuário no sistema Canaimé.
"""
import tkinter as tk
import itertools
import time

from utils.logger import Logger

logger = Logger.get_logger()


class LoginView:
    """
    View para a tela de login.
    
    Attributes
    ----------
    root : tk.Tk
        Referência para a janela principal
    controller : LoginController
        Referência para o controlador de login
    usuario : str
        Nome de usuário após o login bem-sucedido
    senha : str
        Senha após o login bem-sucedido
    """
    
    def __init__(self, root, controller):
        """
        Inicializa a interface de login.
        
        Parameters
        ----------
        root : tk.Tk
            Janela principal
        controller : LoginController
            Controlador de login
        """
        self.root = root
        self.controller = controller
        
        # Configuração da interface
        self.configurar_janela()
        self.criar_widgets()
        
        # Variáveis para armazenar credenciais
        self.usuario = None
        self.senha = None
        
        # Animação e status
        self.frames = itertools.cycle(["◐", "◓", "◑", "◒"])
        self.rodando = False
    
    def configurar_janela(self):
        """Configura a janela principal da aplicação."""
        self.root.title("Login Canaimé")
        largura_janela, altura_janela = 300, 225
        self.centralizar_janela(largura_janela, altura_janela)
        self.root.attributes('-topmost', True)
    
    def centralizar_janela(self, largura_janela, altura_janela):
        """
        Centraliza a janela na tela.
        
        Parameters
        ----------
        largura_janela : int
            Largura da janela
        altura_janela : int
            Altura da janela
        """
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
    
    def criar_widgets(self):
        """Cria todos os widgets da interface."""
        # Campo de usuário
        self.label_usuario = tk.Label(self.root, text="Usuário:", anchor='w')
        self.label_usuario.pack(pady=(10, 2))
        
        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack(pady=(0, 10))
        self.entry_usuario.focus_set()
        
        # Campo de senha
        self.label_senha = tk.Label(self.root, text="Senha:", anchor='w')
        self.label_senha.pack(pady=(10, 2))
        
        self.entry_senha = tk.Entry(self.root, show="*")
        self.entry_senha.pack(pady=(0, 10))
        
        # Botão de login
        self.btn_login = tk.Button(self.root, text="Login", command=self.executar_login)
        self.btn_login.pack(pady=10)
        
        # Label para mostrar status (como animação de carregamento)
        self.label_status = tk.Label(self.root, text="")
        self.label_status.pack(pady=10)
        
        # Configuração de eventos
        self.entry_senha.bind("<Return>", lambda event: self.executar_login())
        self.root.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def executar_login(self):
        """Inicia o processo de login."""
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        self.controller.iniciar_login(usuario, senha)
    
    def iniciar_animacao(self):
        """Inicia a animação de carregamento."""
        self.btn_login.config(state=tk.DISABLED)
        self.rodando = True
        self.animar_bolinha()
    
    def animar_bolinha(self):
        """Animação de carregamento."""
        if not self.rodando:
            return
        
        frame = next(self.frames)
        self.label_status.config(text=f"Realizando login... {frame}")
        self.root.after(200, self.animar_bolinha)
    
    def parar_animacao(self):
        """Para a animação de carregamento."""
        self.rodando = False
        self.label_status.config(text="")
        self.btn_login.config(state=tk.NORMAL)
    
    def login_sucesso(self, usuario, senha):
        """
        Processa o login bem-sucedido.
        
        Parameters
        ----------
        usuario : str
            Nome de usuário
        senha : str
            Senha
        """
        self.usuario = usuario
        self.senha = senha
        logger.info(f"Login bem-sucedido para o usuário: {usuario}")
        self.parar_animacao()
        self.label_status.config(text="Login realizado com sucesso!")
        self.root.after(1000, self.fechar)
    
    def mostrar_erro(self, mensagem):
        """
        Exibe uma mensagem de erro.
        
        Parameters
        ----------
        mensagem : str
            Mensagem de erro
        """
        self.parar_animacao()
        logger.error(f"Erro de login: {mensagem}")
        self.label_status.config(text=mensagem)
    
    def cancelar(self):
        """Cancela o processo de login."""
        logger.info("Login cancelado pelo usuário")
        self.usuario = None
        self.senha = None
        self.fechar()
    
    def fechar(self):
        """Fecha a janela de login."""
        self.root.withdraw()
        self.root.quit()
    
    def atualizar_interface(self, callback):
        """
        Atualiza a interface a partir de threads secundárias.
        
        Parameters
        ----------
        callback : function
            Função a ser executada na thread principal
        """
        self.root.after(0, callback)
    
    def get_credentials(self):
        """
        Obtém as credenciais após o login.
        
        Returns
        -------
        tuple or None
            Tupla (usuario, senha) se o login for bem-sucedido, None caso contrário
        """
        if self.usuario and self.senha:
            return self.usuario, self.senha
        return None, None 