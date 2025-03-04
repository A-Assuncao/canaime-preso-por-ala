"""
Controlador de Login.

Responsável por mediar a interação entre a view de login e os serviços de autenticação.
"""
from threading import Thread
from infrastructure.browser.playwright_adapter import PlaywrightAdapter
from utils.logger import Logger

logger = Logger.get_logger()

# URL de login do sistema Canaimé
URL_LOGIN_CANAIME = 'https://canaime.com.br/sgp2rr/login/login_principal.php'


class LoginController:
    """
    Controlador para a tela de login.
    
    Attributes
    ----------
    view : LoginView
        Referência para a view de login
    """
    
    def __init__(self, view=None):
        """
        Inicializa o controlador de login.
        
        Parameters
        ----------
        view : LoginView, optional
            Referência para a view de login
        """
        self.view = view
    
    def iniciar_login(self, usuario, senha):
        """
        Inicia o processo de login.
        
        Parameters
        ----------
        usuario : str
            Nome de usuário
        senha : str
            Senha
            
        Returns
        -------
        None
        """
        if not usuario or not senha:
            self.view.mostrar_erro("Preencha todos os campos.")
            return
        
        # Iniciar animação de carregamento
        if self.view:
            self.view.iniciar_animacao()
        
        # Iniciar o processo de login em uma thread separada
        thread = Thread(target=self.fazer_login, args=(usuario, senha))
        thread.daemon = True
        thread.start()
    
    def fazer_login(self, usuario, senha):
        """
        Executa o processo de login no Canaimé.
        
        Parameters
        ----------
        usuario : str
            Nome de usuário
        senha : str
            Senha
            
        Returns
        -------
        None
        """
        logger.info("Iniciando processo de login")
        try:
            with PlaywrightAdapter(headless=True) as adapter:
                # Navegar para a página de login
                if not adapter.navigate(URL_LOGIN_CANAIME):
                    self.view.atualizar_interface(
                        lambda: self.view.mostrar_erro("Erro de conexão, tente mais tarde...")
                    )
                    return
                
                # Preencher formulário e submeter
                adapter.fill_form("input[name='usuario']", usuario)
                adapter.fill_form("input[name='senha']", senha)
                adapter.click("input[type='submit']")
                
                # Verificar se o login foi bem-sucedido
                element_count = adapter.get_element_count("img[src*='logo_canaime.jpg']")
                
                if element_count > 0:
                    self.view.atualizar_interface(
                        lambda: self.view.login_sucesso(usuario, senha)
                    )
                else:
                    self.view.atualizar_interface(
                        lambda: self.view.mostrar_erro("Credenciais inválidas!")
                    )
        except Exception as e:
            logger.error(f"Erro durante o login: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            self.view.atualizar_interface(
                lambda: self.view.mostrar_erro("Erro de conexão, tente mais tarde...")
            )


def executar_login():
    """
    Função principal para executar o processo de login.
    
    Returns
    -------
    tuple or None
        Tupla (usuario, senha) se o login for bem-sucedido, None caso contrário
    """
    import tkinter as tk
    from views.login_view import LoginView
    
    # Criar janela
    root = tk.Tk()
    
    # Criar controlador e view
    login_controller = LoginController()
    login_view = LoginView(root, login_controller)
    
    # Conectar view ao controlador
    login_controller.view = login_view
    
    # Executar loop principal
    root.mainloop()
    
    # Retornar credenciais
    return login_view.get_credentials() 