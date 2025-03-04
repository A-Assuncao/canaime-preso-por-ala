import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from utils.resource_manager import resource_path, get_executable_dir


class TestResourceManager:
    """Testes para o gerenciador de recursos da aplicação."""
    
    def test_resource_path_structure(self):
        """Testa a estrutura básica da função resource_path."""
        # Teste simples para verificar se a função retorna uma string
        result = resource_path("test_path")
        assert isinstance(result, str)
        assert "test_path" in result
    
    @patch('utils.resource_manager.os.path.join')
    def test_resource_path_join_called(self, mock_join):
        """Testa se os.path.join é chamado corretamente."""
        mock_join.return_value = "/mocked/path/test_path"
        
        result = resource_path("test_path")
        
        # Verifica se join foi chamado com algum caminho base e o caminho relativo
        mock_join.assert_called_once()
        args = mock_join.call_args[0]
        assert len(args) == 2
        assert args[1] == "test_path"
        
        # Verifica se o resultado é o valor mockado
        assert result == "/mocked/path/test_path"
    
    @patch('utils.resource_manager.sys')
    @patch('utils.resource_manager.os.path.abspath')
    @patch('utils.resource_manager.os.path.join')
    def test_resource_path_not_frozen(self, mock_join, mock_abspath, mock_sys):
        """Testa o comportamento quando não está em modo frozen."""
        # Configura o mock para simular que não está em modo frozen
        mock_sys._MEIPASS = None
        mock_sys.frozen = False
        delattr(mock_sys, '_MEIPASS')
        
        mock_abspath.return_value = "/absolute/current/dir"
        mock_join.return_value = "/absolute/current/dir/test_path"
        
        result = resource_path("test_path")
        
        # Verifica se abspath foi chamado com "."
        mock_abspath.assert_called_once_with(".")
        
        # Verifica se join foi chamado com o caminho absoluto e o caminho relativo
        mock_join.assert_called_once_with("/absolute/current/dir", "test_path")
        
        # Verifica se o resultado é o esperado
        assert result == "/absolute/current/dir/test_path"
    
    def test_get_executable_dir_structure(self):
        """Testa a estrutura básica da função get_executable_dir."""
        # Teste simples para verificar se a função retorna uma string
        result = get_executable_dir()
        assert isinstance(result, str)
        
        # Verifica se o caminho existe
        assert os.path.exists(result) 