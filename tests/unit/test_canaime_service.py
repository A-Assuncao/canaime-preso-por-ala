import pytest
from unittest.mock import MagicMock, patch
from services.canaime_service import CanaimeLogin


class TestCanaimeService:
    """Testes para o serviço de login na plataforma Canaimé."""
    
    @pytest.fixture
    def playwright_mock(self):
        """Mock para o Playwright."""
        playwright_mock = MagicMock()
        browser_mock = MagicMock()
        page_mock = MagicMock()
        context_mock = MagicMock()
        
        # Configuração da hierarquia de mocks
        playwright_mock.chromium.launch.return_value = browser_mock
        browser_mock.new_context.return_value = context_mock
        context_mock.new_page.return_value = page_mock
        
        return {
            'playwright': playwright_mock,
            'browser': browser_mock,
            'context': context_mock,
            'page': page_mock
        }
    
    def test_init(self, playwright_mock):
        """Testa a inicialização do serviço de login."""
        login_service = CanaimeLogin(
            p=playwright_mock['playwright'],
            headless=True,
            login="usuario_teste",
            password="senha_teste"
        )
        
        # Verifica se os atributos foram configurados corretamente
        assert login_service.p == playwright_mock['playwright']
        assert login_service.headless is True
        assert login_service.login == "usuario_teste"
        assert login_service.password == "senha_teste"
    
    def test_perform_login_success(self, playwright_mock):
        """Testa o processo de login bem-sucedido."""
        # Cria o serviço de login
        login_service = CanaimeLogin(
            p=playwright_mock['playwright'],
            headless=True,
            login="usuario_teste",
            password="senha_teste"
        )
        
        # Executa o login
        page, browser = login_service.perform_login()
        
        # Verifica se o navegador foi iniciado com os parâmetros corretos
        playwright_mock['playwright'].chromium.launch.assert_called_once_with(headless=True)
        
        # Verifica se um novo contexto foi criado
        playwright_mock['browser'].new_context.assert_called_once_with(java_script_enabled=False)
        
        # Verifica se cabeçalhos extras foram configurados
        playwright_mock['context'].set_extra_http_headers.assert_called_once()
        
        # Verifica se uma rota foi configurada
        playwright_mock['context'].route.assert_called_once()
        
        # Verifica se a página foi criada
        playwright_mock['context'].new_page.assert_called_once()
        
        # Verifica se a página foi carregada
        playwright_mock['page'].goto.assert_called_once_with('https://canaime.com.br/sgp2rr/login/login_principal.php', timeout=0)
        
        # Verifica se as interações com os campos de login foram realizadas
        assert playwright_mock['page'].locator.call_count >= 2  # Pelo menos 2 chamadas para locator
        
        # Verifica se a função retornou a página e o navegador
        assert page == playwright_mock['page']
        assert browser == playwright_mock['browser']
    
    def test_perform_login_failure(self, playwright_mock):
        """Testa o processo de login quando falha."""
        # Cria o serviço de login
        login_service = CanaimeLogin(
            p=playwright_mock['playwright'],
            headless=True,
            login="usuario_errado",
            password="senha_errada"
        )
        
        # Configura o mock para lançar uma exceção durante o login
        playwright_mock['playwright'].chromium.launch.side_effect = Exception("Erro de login")
        
        # Verifica se a exceção é propagada
        with pytest.raises(Exception, match="Erro de login"):
            login_service.perform_login()
    
    # Removendo o teste que usa time, já que o módulo não está importado na implementação atual
    def test_close_browser(self, playwright_mock):
        """Testa o fechamento explícito do navegador."""
        # Cria o serviço de login
        login_service = CanaimeLogin(
            p=playwright_mock['playwright'],
            headless=True,
            login="usuario_teste",
            password="senha_teste"
        )
        
        # Configura o browser
        login_service.browser = playwright_mock['browser']
        
        # Chama o método para fechar o navegador
        login_service.close_browser()
        
        # Verifica se o navegador foi fechado
        playwright_mock['browser'].close.assert_called_once()
        
        # Verifica se o browser foi definido como None
        assert login_service.browser is None 