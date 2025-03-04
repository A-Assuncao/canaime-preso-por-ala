import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from gui.login.login_canaime import LoginApp, executar_login, URL_LOGIN_CANAIME


class TestLoginCanaime:
    """Testes para a interface de login do sistema Canaimé."""
    
    @pytest.fixture
    def mock_root(self):
        """Mock para a janela raiz do tkinter."""
        root = MagicMock()
        # Simula as dimensões da tela
        root.winfo_screenwidth.return_value = 1920
        root.winfo_screenheight.return_value = 1080
        return root
    
    def test_login_app_init(self, mock_root):
        """Testa a inicialização da classe LoginApp."""
        app = LoginApp(mock_root)
        
        # Verifica se a janela foi configurada corretamente
        mock_root.title.assert_called_once_with("Login Canaimé")
        mock_root.attributes.assert_called_once_with('-topmost', True)
        
        # Verifica se os widgets foram criados
        assert app.label_usuario is not None
        assert app.entry_usuario is not None
        assert app.label_senha is not None
        
        # Verifica se as variáveis foram inicializadas corretamente
        assert app.usuario is None
        assert app.senha is None
        assert app.rodando is False
    
    def test_executar_login_success(self):
        """Testa a função executar_login com credenciais válidas."""
        # Patch direto da função tk.Tk
        with patch('tkinter.Tk') as mock_tk:
            # Configura o mock para a janela raiz
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Patch para a classe LoginApp
            with patch('gui.login.login_canaime.LoginApp') as mock_login_app_class:
                # Configura o mock para a instância de LoginApp
                mock_app_instance = MagicMock()
                mock_login_app_class.return_value = mock_app_instance
                
                # Simula que o usuário inseriu credenciais válidas
                mock_app_instance.usuario = "usuario_teste"
                mock_app_instance.senha = "senha_teste"
                mock_app_instance.get_credentials.return_value = ("usuario_teste", "senha_teste")
                
                # Executa a função sendo testada
                login, password = executar_login()
                
                # Verifica se a função retornou as credenciais corretamente
                assert login == "usuario_teste"
                assert password == "senha_teste"
                
                # Verifica se a janela foi corretamente inicializada e fechada
                mock_tk.assert_called_once()
                mock_login_app_class.assert_called_once_with(mock_root)
                mock_root.mainloop.assert_called_once()
                mock_app_instance.get_credentials.assert_called_once()
    
    def test_executar_login_cancel(self):
        """Testa a função executar_login quando o usuário cancela o login."""
        # Patch direto da função tk.Tk
        with patch('tkinter.Tk') as mock_tk:
            # Configura o mock para a janela raiz
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Patch para a classe LoginApp
            with patch('gui.login.login_canaime.LoginApp') as mock_login_app_class:
                # Configura o mock para a instância de LoginApp
                mock_app_instance = MagicMock()
                mock_login_app_class.return_value = mock_app_instance
                
                # Simula que o usuário cancelou o login (não forneceu credenciais)
                mock_app_instance.usuario = None
                mock_app_instance.senha = None
                mock_app_instance.get_credentials.return_value = (None, None)
                
                # Executa a função sendo testada
                login, password = executar_login()
                
                # Verifica se a função retornou None para ambas as credenciais
                assert login is None
                assert password is None
                mock_app_instance.get_credentials.assert_called_once()
    
    def test_animar_bolinha(self, mock_root):
        """Testa a animação do status de login."""
        with patch('itertools.cycle') as mock_cycle:
            mock_cycle.return_value = iter(["◐", "◓", "◑", "◒"])
            
            with patch('time.sleep') as mock_sleep:
                app = LoginApp(mock_root)
                app.label_status = MagicMock()
                
                # Inicia a animação e para após o primeiro frame
                app.rodando = True
                
                # Mock para fazer a função retornar após a primeira iteração
                def side_effect(*args, **kwargs):
                    app.rodando = False
                mock_sleep.side_effect = side_effect
                
                # Chama o método a ser testado
                app.animar_bolinha()
                
                # Verifica se o label foi configurado com o primeiro frame da animação
                app.label_status.config.assert_called_with(text="Realizando login... ◐")
                
                # Verifica se sleep foi chamado
                mock_sleep.assert_called_once_with(0.2)
    
    def test_fazer_login_sucesso(self, mock_root):
        """Testa o processo de login bem-sucedido."""
        with patch('gui.login.login_canaime.sync_playwright') as mock_sync_playwright:
            # Configura os mocks para simular um login bem-sucedido
            mock_playwright = MagicMock()
            mock_page = MagicMock()
            mock_browser = MagicMock()
            
            # Configura a hierarquia de mocks
            mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
            mock_playwright.chromium.launch.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            
            # Simula que há elementos suficientes (imagens) na página após login bem-sucedido
            mock_page.locator.return_value.count.return_value = 5
            
            # Cria a instância da app e configura as entradas
            app = LoginApp(mock_root)
            app.entry_usuario = MagicMock()
            app.entry_senha = MagicMock()
            app.entry_usuario.get.return_value = "usuario_teste"
            app.entry_senha.get.return_value = "senha_teste"
            
            # Patch para o método realizar_login para isolar o teste
            with patch.object(app, 'realizar_login') as mock_realizar_login:
                # Executa o método
                app.fazer_login()
                
                # Verifica se o browser foi lançado corretamente
                mock_playwright.chromium.launch.assert_called_once_with(headless=True)
                mock_browser.new_page.assert_called_once()
                
                # Verifica se o método realizar_login foi chamado corretamente
                mock_realizar_login.assert_called_once_with(mock_page, "usuario_teste", "senha_teste")
                
                # Verifica se o browser foi fechado
                mock_browser.close.assert_called_once()
    
    def test_fazer_login_campos_vazios(self, mock_root):
        """Testa o processo de login com campos vazios."""
        # Cria a instância da app e configura as entradas vazias
        app = LoginApp(mock_root)
        app.entry_usuario = MagicMock()
        app.entry_senha = MagicMock()
        app.entry_usuario.get.return_value = ""
        app.entry_senha.get.return_value = ""
        
        # Mock para o método mostrar_erro
        with patch.object(app, 'mostrar_erro') as mock_mostrar_erro:
            # Executa o método
            app.fazer_login()
            
            # Verifica se mostrar_erro foi chamado com a mensagem correta
            mock_mostrar_erro.assert_called_once_with("Usuário e senha são obrigatórios.")
    
    def test_fazer_login_excecao(self, mock_root):
        """Testa o processo de login com exceção."""
        with patch('gui.login.login_canaime.sync_playwright') as mock_sync_playwright:
            # Configura o mock para lançar uma exceção
            mock_sync_playwright.return_value.__enter__.side_effect = Exception("Erro de conexão")
            
            # Cria a instância da app e configura as entradas
            app = LoginApp(mock_root)
            app.entry_usuario = MagicMock()
            app.entry_senha = MagicMock()
            app.entry_usuario.get.return_value = "usuario_teste"
            app.entry_senha.get.return_value = "senha_teste"
            
            # Mock para o método mostrar_erro
            with patch.object(app, 'mostrar_erro') as mock_mostrar_erro:
                # Executa o método
                app.fazer_login()
                
                # Verifica se mostrar_erro foi chamado com a mensagem correta
                mock_mostrar_erro.assert_called_once_with("Erro de conexão, tente mais tarde...")
    
    def test_realizar_login_sucesso(self, mock_root):
        """Testa a realização do login bem-sucedido."""
        # Cria a instância da app
        app = LoginApp(mock_root)
        
        # Mock para o page do Playwright
        mock_page = MagicMock()
        # Simula que há elementos suficientes (imagens) na página após login bem-sucedido
        mock_page.locator.return_value.count.return_value = 5
        
        # Mock para o método login_sucesso
        with patch.object(app, 'login_sucesso') as mock_login_sucesso:
            # Executa o método
            app.realizar_login(mock_page, "usuario_teste", "senha_teste")
            
            # Verifica se as ações no página foram realizadas corretamente
            mock_page.goto.assert_called_once_with(URL_LOGIN_CANAIME)
            mock_page.fill.assert_any_call("input[name='usuario']", "usuario_teste")
            mock_page.fill.assert_any_call("input[name='senha']", "senha_teste")
            mock_page.press.assert_called_once_with("input[name='senha']", "Enter")
            mock_page.wait_for_timeout.assert_called_once_with(5000)
            mock_page.locator.assert_called_once_with('img')
            
            # Verifica se login_sucesso foi chamado corretamente
            mock_login_sucesso.assert_called_once_with("usuario_teste", "senha_teste")
    
    def test_realizar_login_falha(self, mock_root):
        """Testa a realização do login com falha."""
        # Cria a instância da app
        app = LoginApp(mock_root)
        
        # Mock para o page do Playwright
        mock_page = MagicMock()
        # Simula que não há elementos suficientes (imagens) na página (login falhou)
        mock_page.locator.return_value.count.return_value = 3
        
        # Mock para o método mostrar_erro
        with patch.object(app, 'mostrar_erro') as mock_mostrar_erro:
            # Executa o método
            app.realizar_login(mock_page, "usuario_errado", "senha_errada")
            
            # Verifica se as ações no página foram realizadas corretamente
            mock_page.goto.assert_called_once_with(URL_LOGIN_CANAIME)
            
            # Verifica se mostrar_erro foi chamado com a mensagem correta
            mock_mostrar_erro.assert_called_once_with("Usuário ou senha inválidos.")
    
    def test_login_sucesso(self, mock_root):
        """Testa o método login_sucesso."""
        app = LoginApp(mock_root)
        app.label_status = MagicMock()
        app.rodando = True
        
        # Mock para o método atualizar_interface para capturar o callback
        def mock_atualizar_interface(callback):
            # Executa o callback diretamente
            callback()
        
        with patch.object(app, 'atualizar_interface', side_effect=mock_atualizar_interface):
            # Executa o método
            app.login_sucesso("usuario_teste", "senha_teste")
            
            # Verifica se as credenciais foram armazenadas
            assert app.usuario == "usuario_teste"
            assert app.senha == "senha_teste"
            
            # Verifica se rodando foi definido como False
            assert app.rodando is False
            
            # Verifica se o status foi atualizado corretamente
            app.label_status.config.assert_called_with(text="Login efetuado com sucesso!")
            
            # Verifica se after foi chamado para fechar a janela
            # Como a chamada é feita dentro de um lambda/tuple, não podemos verificar diretamente
            assert mock_root.after.called
    
    def test_mostrar_erro(self, mock_root):
        """Testa o método mostrar_erro."""
        app = LoginApp(mock_root)
        app.label_status = MagicMock()
        app.btn_login = MagicMock()
        app.rodando = True
        
        # Mock para o método atualizar_interface para capturar o callback
        original_atualizar_interface = app.atualizar_interface
        
        def mock_atualizar_interface(callback):
            # Executa o callback diretamente
            callback()
            return original_atualizar_interface(callback)
            
        with patch.object(app, 'atualizar_interface', side_effect=mock_atualizar_interface):
            # Executa o método
            app.mostrar_erro("Mensagem de erro de teste")
            
            # Verifica se rodando foi definido como False
            assert app.rodando is False
            
            # Verifica se o status foi atualizado corretamente
            app.label_status.config.assert_called_with(text="Mensagem de erro de teste")
            
            # Verifica se o botão foi habilitado novamente
            app.btn_login.config.assert_called_with(state=tk.NORMAL)
    
    def test_get_credentials(self, mock_root):
        """Testa o método get_credentials."""
        app = LoginApp(mock_root)
        
        # Caso 1: Nenhuma credencial definida
        assert app.get_credentials() == (None, None)
        
        # Caso 2: Credenciais definidas
        app.usuario = "usuario_teste"
        app.senha = "senha_teste"
        assert app.get_credentials() == ("usuario_teste", "senha_teste") 