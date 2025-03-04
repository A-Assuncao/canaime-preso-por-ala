import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Adiciona o diretório raiz do projeto ao PYTHONPATH para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fixtures comuns para todos os testes
@pytest.fixture
def mock_playwright():
    """Mock para o Playwright para não precisar iniciar um navegador real durante os testes."""
    with patch('playwright.sync_api.sync_playwright') as mock:
        # Configura os mocks necessários para simular o comportamento do Playwright
        playwright_instance = MagicMock()
        mock.return_value.__enter__.return_value = playwright_instance
        
        # Mock para o browser
        browser = MagicMock()
        playwright_instance.chromium.launch.return_value = browser
        
        # Mock para a página
        page = MagicMock()
        browser.new_page.return_value = page
        
        yield {
            'playwright': playwright_instance,
            'browser': browser,
            'page': page
        }

@pytest.fixture
def mock_tkinter():
    """Mock para o Tkinter para não precisar abrir janelas durante os testes."""
    with patch('tkinter.Tk') as mock_tk:
        root = MagicMock()
        mock_tk.return_value = root
        yield root 