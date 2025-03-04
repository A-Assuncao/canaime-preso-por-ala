import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk

# Importa as funções e classes a serem testadas
from main import main, StatusApp, process_task


class TestMainFlow:
    """Testes de integração para o fluxo principal da aplicação."""
    
    @patch('main.executar_login')
    @patch('main.select_units')
    @patch('main.tk.Tk')
    @patch('main.StatusApp')
    def test_main_flow_successful(self, mock_status_app, mock_tk, mock_select_units, mock_executar_login):
        """Testa o fluxo principal da aplicação com login e seleção de unidades bem-sucedidos."""
        # Configura os mocks
        mock_executar_login.return_value = ("usuario_teste", "senha_teste")
        mock_select_units.return_value = ["UNIT1", "UNIT2"]
        
        # Executa a função principal
        main(headless=True)
        
        # Verifica se todas as etapas foram executadas corretamente
        mock_executar_login.assert_called_once()
        mock_select_units.assert_called_once()
        mock_tk.assert_called_once()
        mock_status_app.assert_called_once()
    
    @patch('main.executar_login')
    @patch('main.select_units')
    @patch('main.tk.Tk')
    @patch('main.StatusApp')
    def test_main_flow_no_login(self, mock_status_app, mock_tk, mock_select_units, mock_executar_login):
        """Testa o fluxo principal quando o login falha."""
        # Configura os mocks para simular falha no login
        mock_executar_login.return_value = (None, None)
        
        # Executa a função principal
        main(headless=True)
        
        # Verifica que select_units não foi chamado após falha no login
        mock_executar_login.assert_called_once()
        mock_select_units.assert_not_called()
        mock_tk.assert_not_called()
        mock_status_app.assert_not_called()
    
    @patch('main.executar_login')
    @patch('main.select_units')
    @patch('main.tk.Tk')
    @patch('main.StatusApp')
    def test_main_flow_no_units(self, mock_status_app, mock_tk, mock_select_units, mock_executar_login):
        """Testa o fluxo principal quando nenhuma unidade é selecionada."""
        # Configura os mocks para simular que nenhuma unidade foi selecionada
        mock_executar_login.return_value = ("usuario_teste", "senha_teste")
        mock_select_units.return_value = []
        
        # Executa a função principal
        main(headless=True)
        
        # Verifica que StatusApp não foi chamado após não selecionar unidades
        mock_executar_login.assert_called_once()
        mock_select_units.assert_called_once()
        mock_tk.assert_not_called()
        mock_status_app.assert_not_called()

    @patch('models.services.data_service.DataService.process_multiple_units')
    @patch('main.create_excel_report')
    def test_process_task_successful(self, mock_create_excel_report, mock_process_multiple_units):
        """Testa o processamento de tarefa com dados válidos."""
        # Configura mock para simular dados retornados pelo serviço de dados
        mock_unit_data = {
            "UNIT1": [{"Bloco": "A", "Ala": "1", "Cela": "101", "Código": "123", "Preso": "João"}]
        }
        mock_process_multiple_units.return_value = mock_unit_data
        
        # Cria objetos necessários para o teste
        queue = MagicMock()
        stop_event = MagicMock()
        
        # Executa a função
        process_task(
            headless=True,
            queue=queue,
            stop_event=stop_event,
            login="usuario_teste",
            password="senha_teste",
            selected_units=["UNIT1"]
        )
        
        # Verifica se as mensagens corretas foram colocadas na fila
        queue.put.assert_any_call("Processo Completo.")
        queue.put.assert_any_call("Arquivo salvo com sucesso.")
        
        # Verifica se o relatório foi criado
        mock_create_excel_report.assert_called_once_with(mock_unit_data)
        
        # Verifica se o evento de parada foi acionado
        stop_event.set.assert_called_once()
    
    @patch('models.services.data_service.DataService.process_multiple_units')
    @patch('main.create_excel_report')
    def test_process_task_empty_data(self, mock_create_excel_report, mock_process_multiple_units):
        """Testa o processamento de tarefa sem dados válidos."""
        # Configura mock para simular dados vazios
        mock_unit_data = {
            "UNIT1": []
        }
        mock_process_multiple_units.return_value = mock_unit_data
        
        # Cria objetos necessários para o teste
        queue = MagicMock()
        stop_event = MagicMock()
        
        # Executa a função
        process_task(
            headless=True,
            queue=queue,
            stop_event=stop_event,
            login="usuario_teste",
            password="senha_teste",
            selected_units=["UNIT1"]
        )
        
        # Verifica se as mensagens corretas foram colocadas na fila
        queue.put.assert_any_call("Processo Completo.")
        queue.put.assert_any_call("Nenhum dado válido encontrado para gerar o relatório.")
        
        # Verifica que o relatório não foi criado
        mock_create_excel_report.assert_not_called()
        
        # Verifica se o evento de parada foi acionado
        stop_event.set.assert_called_once()
    
    @patch('models.services.data_service.DataService.process_multiple_units')
    def test_process_task_exception(self, mock_process_multiple_units):
        """Testa o comportamento quando ocorre uma exceção durante o processamento."""
        # Configura mock para simular uma exceção
        mock_process_multiple_units.side_effect = Exception("Erro de teste")
        
        # Cria objetos necessários para o teste
        queue = MagicMock()
        stop_event = MagicMock()
        
        # Executa a função
        process_task(
            headless=True,
            queue=queue,
            stop_event=stop_event,
            login="usuario_teste",
            password="senha_teste",
            selected_units=["UNIT1"]
        )
        
        # Verifica se a mensagem de erro foi colocada na fila
        queue.put.assert_called_once_with("Erro: Erro de teste")
        
        # Verifica se o evento de parada foi acionado mesmo com o erro
        stop_event.set.assert_called_once() 