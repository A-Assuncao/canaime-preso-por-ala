import pytest
from unittest.mock import MagicMock, patch
from services.playwright_service import execute_playwright_task


class TestPlaywrightService:
    """Testes para o serviço de Playwright que interage com o site Canaimé."""
    
    @patch('services.playwright_service.sync_playwright')
    @patch('services.playwright_service.CanaimeLogin')
    @patch('services.playwright_service.UnitProcessor')
    def test_execute_playwright_task(self, mock_unit_processor_class, mock_canaime_login_class, mock_sync_playwright):
        """Testa a execução da tarefa de Playwright para obtenção de dados das unidades."""
        # Configura mock para sync_playwright
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        
        # Configura os mocks
        mock_login_instance = MagicMock()
        mock_canaime_login_class.return_value = mock_login_instance
        
        # Configura o retorno do login
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_login_instance.perform_login.return_value = (mock_page, mock_browser)
        
        # Configura o processador de unidades
        mock_unit_processor = MagicMock()
        mock_unit_processor_class.return_value = mock_unit_processor
        
        # Configura os dados de retorno para duas unidades
        mock_unit_data1 = {"UNIT1": [{"Bloco": "A", "Ala": "1", "Cela": "101", "Código": "123", "Preso": "João"}]}
        mock_unit_data2 = {"UNIT2": [{"Bloco": "B", "Ala": "2", "Cela": "201", "Código": "456", "Preso": "Maria"}]}
        
        mock_unit_processor.create_unit_list.side_effect = [
            mock_unit_data1,
            mock_unit_data2
        ]
        
        # Parametros do teste
        headless = True
        login = "usuario_teste"
        password = "senha_teste"
        selected_units = ["UNIT1", "UNIT2"]
        
        # Executa a função que está sendo testada
        result = execute_playwright_task(headless, login, password, selected_units)
        
        # Verifica se o login foi chamado corretamente
        mock_canaime_login_class.assert_called_once_with(
            mock_playwright, 
            headless=headless, 
            login=login, 
            password=password
        )
        
        # Verifica se o login foi executado
        mock_login_instance.perform_login.assert_called_once()
        
        # Verifica se o UnitProcessor foi criado com a página correta
        mock_unit_processor_class.assert_called_once_with(mock_page)
        
        # Verifica se o processador de unidades foi chamado para cada unidade
        assert mock_unit_processor.create_unit_list.call_count == 2
        mock_unit_processor.create_unit_list.assert_any_call("UNIT1")
        mock_unit_processor.create_unit_list.assert_any_call("UNIT2")
        
        # Verifica se o resultado contém os dados das duas unidades
        assert "UNIT1" in result
        assert "UNIT2" in result
        assert result["UNIT1"] == mock_unit_data1["UNIT1"]
        assert result["UNIT2"] == mock_unit_data2["UNIT2"]
        
        # Verifica se o navegador foi fechado ao final
        mock_browser.close.assert_called_once()
    
    @patch('services.playwright_service.sync_playwright')
    @patch('services.playwright_service.CanaimeLogin')
    @patch('services.playwright_service.UnitProcessor')
    def test_execute_playwright_task_with_exception(self, mock_unit_processor_class, mock_canaime_login_class, mock_sync_playwright):
        """Testa o comportamento em caso de exceção durante a execução."""
        # Configura mock para sync_playwright
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        
        # Configura o mock para lançar uma exceção
        mock_login_instance = MagicMock()
        mock_canaime_login_class.return_value = mock_login_instance
        mock_login_instance.perform_login.side_effect = Exception("Erro de login simulado")
        
        # Parametros do teste
        headless = True
        login = "usuario_teste"
        password = "senha_teste"
        selected_units = ["UNIT1"]
        
        # Executa a função que está sendo testada
        result = execute_playwright_task(headless, login, password, selected_units)
        
        # Verifica se a função retorna um dicionário vazio em caso de erro
        assert result == {} 