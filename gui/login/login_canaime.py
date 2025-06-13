import tkinter as tk
from threading import Thread
from playwright.sync_api import sync_playwright
import itertools
import time


# URL de login do sistema Canaimé
URL_LOGIN_CANAIME = 'https://canaime.com.br/sgp2rr/login/login_principal.php'


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.configurar_janela()
        self.criar_widgets()

        # Variáveis para armazenar credenciais
        self.usuario = None
        self.senha = None
        self.use_https = True

        # Animação e status
        self.animacao = None
        self.rodando = False

    def configurar_janela(self):
        """Configura a janela principal da aplicação."""
        self.root.title("Login Canaimé")
        largura_janela, altura_janela = 300, 275
        self.centralizar_janela(largura_janela, altura_janela)
        self.root.attributes('-topmost', True)

    def centralizar_janela(self, largura_janela, altura_janela):
        """Centraliza a janela na tela."""
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    def criar_widgets(self):
        """Cria todos os widgets da interface."""
        self.label_usuario = tk.Label(self.root, text="Usuário:", anchor='w')
        self.label_usuario.pack(pady=(10, 2))

        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack(pady=(0, 10))
        self.entry_usuario.focus_set()

        self.label_senha = tk.Label(self.root, text="Senha:", anchor='w')
        self.label_senha.pack(pady=(10, 2))

        self.entry_senha = tk.Entry(self.root, show="*")
        self.entry_senha.pack(pady=(0, 10))

        # Frame para o checkbox e explicação
        frame_https = tk.Frame(self.root)
        frame_https.pack(pady=(0, 10), fill='x', padx=10)

        self.use_https_var = tk.BooleanVar(value=True)
        self.check_https = tk.Checkbutton(frame_https, text="Usar HTTPS", variable=self.use_https_var)
        self.check_https.pack(anchor='w')

        # Label com explicação
        self.label_explicacao = tk.Label(frame_https, text="Desmarque para usar HTTP", 
                                       wraplength=280, justify='left', fg='gray')
        self.label_explicacao.pack(anchor='w', pady=(0, 5))

        self.btn_login = tk.Button(self.root, text="Login", command=self.iniciar_login)
        self.btn_login.pack(pady=10)

        # Label para mostrar status (como animação de carregamento)
        self.label_status = tk.Label(self.root, text="")
        self.label_status.pack(pady=10)

        # Vincular o evento de pressionar Enter ao método de login
        self.root.bind('<Return>', self.on_enter)

    def iniciar_login(self):
        """Inicia o processo de login em uma thread separada."""
        self.btn_login.config(state=tk.DISABLED)
        self.label_status.config(text="Realizando login...")
        self.rodando = True

        # Iniciar animação e processo de login
        Thread(target=self.animar_bolinha).start()
        Thread(target=self.fazer_login).start()

    def animar_bolinha(self):
        """Anima a bolinha enquanto o login está em andamento."""
        for frame in itertools.cycle(["◐", "◓", "◑", "◒"]):
            if not self.rodando:
                break
            self.label_status.config(text=f"Realizando login... {frame}")
            time.sleep(0.2)

    def on_enter(self, event):
        """Método chamado quando a tecla Enter é pressionada."""
        self.iniciar_login()

    def fazer_login(self):
        """Executa o login utilizando Playwright em uma thread separada."""
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            self.mostrar_erro("Usuário e senha são obrigatórios.")
            return

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                self.realizar_login(page, usuario, senha)
                browser.close()

        except Exception as e:
            mensagem = str(e)
            if "certificado" in mensagem.lower():
                self.mostrar_erro("O certificado do site está expirado. Por favor, desmarque a opção 'Usar HTTPS' e tente novamente.")
            elif "timeout" in mensagem.lower():
                self.mostrar_erro("O site demorou muito para responder. Verifique sua conexão com a internet e tente novamente.")
            elif "não foi possível acessar" in mensagem.lower():
                self.mostrar_erro("Não foi possível acessar o site. Verifique sua conexão com a internet ou tente usar HTTP se o certificado estiver expirado.")
            else:
                self.mostrar_erro(f"Erro de conexão: {mensagem}")

    def realizar_login(self, page, usuario, senha):
        """Realiza o processo de login utilizando Playwright."""
        protocol = 'https' if self.use_https_var.get() else 'http'
        url = f'{protocol}://canaime.com.br/sgp2rr/login/login_principal.php'
        
        try:
            page.goto(url, timeout=30000)  # 30 segundos de timeout
            page.fill("input[name='usuario']", usuario)
            page.fill("input[name='senha']", senha)
            page.press("input[name='senha']", "Enter")
            page.wait_for_timeout(5000)

            if page.locator('img').count() < 4:
                self.mostrar_erro("Usuário ou senha inválidos.")
            else:
                self.login_sucesso(usuario, senha)
        except Exception as e:
            raise Exception(f"Erro ao tentar login: {str(e)}")

    def login_sucesso(self, usuario, senha):
        """Atualiza a interface para mostrar sucesso no login."""
        self.usuario = usuario
        self.senha = senha
        self.use_https = self.use_https_var.get()
        self.rodando = False
        self.atualizar_interface(lambda: (
            self.label_status.config(text="Login efetuado com sucesso!"),
            self.root.after(1000, self.root.destroy)
        ))

    def mostrar_erro(self, mensagem):
        """Mostra mensagem de erro e habilita o botão de login novamente."""
        self.rodando = False
        self.atualizar_interface(lambda: (
            self.label_status.config(text=mensagem),
            self.btn_login.config(state=tk.NORMAL)
        ))

    def atualizar_interface(self, func):
        """Atualiza a interface da aplicação."""
        self.root.after(0, func)

    def get_credentials(self):
        """Retorna as credenciais de login (usuário, senha e uso de HTTPS)."""
        return self.usuario, self.senha, self.use_https


# Função para executar a aplicação de login e retornar as credenciais
def executar_login():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
    return app.get_credentials()


if __name__ == "__main__":
    usuario, senha, use_https = executar_login()
    print(f"Usuário: {usuario}, Senha: {senha}, HTTPS: {use_https}")
