import pytest
from unittest.mock import MagicMock, patch, call
import logging
import os
from utils.logger import Logger


class TestLogger:
    """Testes para o módulo de logger da aplicação."""
    
    def setup_method(self):
        """Configuração executada antes de cada teste."""
        # Resetar o estado do logger para garantir testes isolados
        Logger.reset()
    
    @patch('utils.logger.logging.getLogger')
    def test_get_logger(self, mock_get_logger):
        """Testa a obtenção do logger configurado."""
        # Configura o mock
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Obtém o logger
        logger = Logger.get_logger()
        
        # Verifica se o logger foi obtido corretamente
        mock_get_logger.assert_called_once_with("CanaimeApp")
        
        # Verifica se o nível do logger foi configurado
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        
        # Verifica se o logger retornado é o esperado
        assert logger == mock_logger
    
    @patch('utils.logger.os.path.exists')
    @patch('utils.logger.logging.getLogger')
    def test_get_logger_existing_dir(self, mock_get_logger, mock_exists):
        """Testa a obtenção do logger quando o diretório já existe."""
        # Configura o mock para simular que o diretório já existe
        mock_exists.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Obtém o logger
        logger = Logger.get_logger()
        
        # Verifica se o logger retornado é o esperado
        assert logger == mock_logger
    
    @patch('utils.logger.logging.getLogger')
    def test_logger_singleton(self, mock_get_logger):
        """Testa se o logger é um singleton."""
        # Configura mocks para duas chamadas diferentes
        mock_logger1 = MagicMock()
        mock_get_logger.return_value = mock_logger1
        
        # Obtém o logger duas vezes
        logger1 = Logger.get_logger()
        
        # Verifica que getLogger só foi chamado uma vez até agora
        assert mock_get_logger.call_count == 1
        
        logger2 = Logger.get_logger()
        
        # Verifica que getLogger ainda só foi chamado uma vez (singleton)
        assert mock_get_logger.call_count == 1
        
        # Verifica se as duas variáveis referem-se ao mesmo objeto
        assert logger1 is logger2
    
    @patch('utils.logger.Logger.get_logger')
    @patch('utils.logger.Logger.send_to_discord')
    def test_capture_error(self, mock_send_to_discord, mock_get_logger):
        """Testa a captura de erros."""
        # Configura os mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_exception = Exception("Erro de teste")
        
        # Captura o erro
        error_log = Logger.capture_error(mock_exception)
        
        # Verifica se o logger foi chamado corretamente
        mock_logger.error.assert_called_once()
        
        # Verifica se o erro foi enviado para o Discord
        mock_send_to_discord.assert_called_once()
        
        # Verifica se o conteúdo do log contém as informações esperadas
        assert "Erro capturado: Erro de teste" in error_log
        assert "Traceback" in error_log
        assert "Informações do Sistema" in error_log
    
    @patch('utils.logger.Logger.get_logger')
    def test_log_methods(self, mock_get_logger):
        """Testa os métodos de log."""
        # Configura o mock para o logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Testa o método info
        Logger.info("Mensagem info")
        mock_logger.info.assert_called_once_with("Mensagem info")
        
        # Testa o método error
        Logger.error("Mensagem erro")
        mock_logger.error.assert_called_once_with("Mensagem erro")
        
        # Testa o método debug
        Logger.debug("Mensagem debug")
        mock_logger.debug.assert_called_once_with("Mensagem debug")
        
        # Testa o método warning
        Logger.warning("Mensagem aviso")
        mock_logger.warning.assert_called_once_with("Mensagem aviso")
    
    @patch('utils.logger.requests.post')
    def test_send_to_discord_success(self, mock_post):
        """Testa o envio bem-sucedido para o Discord."""
        # Configura o mock para simular uma resposta bem-sucedida
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        # Captura a saída para verificar a mensagem impressa
        with patch('builtins.print') as mock_print:
            Logger.send_to_discord("Mensagem de teste")
            
            # Verifica se a mensagem de sucesso foi impressa
            mock_print.assert_called_once_with("Log enviado com sucesso para o Discord.")
        
        # Verifica se o post foi feito corretamente
        mock_post.assert_called_once()
    
    @patch('utils.logger.requests.post')
    def test_send_to_discord_failure(self, mock_post):
        """Testa o envio com falha para o Discord."""
        # Configura o mock para simular uma resposta com falha
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # Captura a saída para verificar a mensagem impressa
        with patch('builtins.print') as mock_print:
            Logger.send_to_discord("Mensagem de teste")
            
            # Verifica se a mensagem de falha foi impressa
            mock_print.assert_called_once_with("Falha ao enviar log para Discord: 400")
        
        # Verifica se o post foi feito corretamente
        mock_post.assert_called_once() 