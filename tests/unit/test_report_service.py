import pytest
from unittest.mock import MagicMock, patch, call
import pandas as pd
from openpyxl.styles import Alignment
from services.report_service import create_excel_report, get_shift_name, calculate_data


class TestReportService:
    """Testes para o serviço de geração de relatórios."""
    
    @pytest.fixture
    def sample_unit_data(self):
        """Dados de amostra para testes de relatórios."""
        return {
            "UNIT1": [
                {"Bloco": "A", "Ala": "1", "Cela": "101", "Código": "123", "Preso": "João Silva"},
                {"Bloco": "A", "Ala": "1", "Cela": "101", "Código": "456", "Preso": "Maria Souza"},
                {"Bloco": "A", "Ala": "2", "Cela": "201", "Código": "789", "Preso": "José Santos"},
                {"Bloco": "B", "Ala": "3", "Cela": "301", "Código": "012", "Preso": "Ana Pereira"}
            ],
            "UNIT2": [
                {"Bloco": "C", "Ala": "4", "Cela": "401", "Código": "345", "Preso": "Carlos Lima"},
                {"Bloco": "C", "Ala": "4", "Cela": "402", "Código": "678", "Preso": "Juliana Costa"}
            ]
        }
    
    @pytest.fixture
    def calculated_data(self):
        """Dados calculados para testes de relatórios."""
        return {
            "A": {
                "1": {"101": 2},
                "2": {"201": 1}
            },
            "B": {
                "3": {"301": 1}
            }
        }
    
    @patch('services.report_service.datetime')
    def test_get_shift_name(self, mock_datetime):
        """Testa a obtenção do nome do plantão baseado na data."""
        # Configurando mock para simular diferentes datas
        from datetime import datetime
        
        # Verificamos que a função retorna um dos plantões válidos
        mock_datetime.now.return_value = datetime(2024, 1, 1)
        mock_datetime.datetime = datetime
        
        shift_name = get_shift_name()
        valid_shifts = ['ALFA', 'BRAVO', 'CHARLIE', 'DELTA']
        assert shift_name in valid_shifts, f"O plantão '{shift_name}' não é um dos plantões válidos: {valid_shifts}"
    
    def test_calculate_data(self, sample_unit_data):
        """Testa o cálculo de dados para o relatório."""
        # Criar DataFrame a partir dos dados da unidade
        df = pd.DataFrame(sample_unit_data["UNIT1"])
        
        # Executar a função sendo testada
        result = calculate_data(df)
        
        # Verificações para a estrutura correta de dados
        assert "A" in result
        assert "1" in result["A"]
        assert "101" in result["A"]["1"]
        assert result["A"]["1"]["101"] == 2
        
        assert "A" in result
        assert "2" in result["A"]
        assert "201" in result["A"]["2"]
        assert result["A"]["2"]["201"] == 1
        
        assert "B" in result
        assert "3" in result["B"]
        assert "301" in result["B"]["3"]
        assert result["B"]["3"]["301"] == 1
    
    @patch('services.report_service.Workbook')
    @patch('services.report_service.filedialog')
    @patch('services.report_service.datetime')
    @patch('services.report_service.get_shift_name')
    @patch('services.report_service.generate_unit_control_sheet')
    @patch('services.report_service.generate_unit_sei_sheet')
    def test_create_excel_report(self, mock_generate_sei, mock_generate_control, 
                             mock_get_shift, mock_datetime, mock_filedialog, 
                             mock_workbook_class, sample_unit_data):
        """Testa a criação do relatório Excel com os dados das unidades."""
        # Configuração dos mocks
        mock_workbook = MagicMock()
        mock_workbook_class.return_value = mock_workbook
        
        mock_sheet = MagicMock()
        mock_workbook.create_sheet.return_value = mock_sheet
        mock_workbook.active = mock_sheet
        
        # Mock para o nome do arquivo salvo
        from datetime import datetime
        mock_datetime.now.return_value = datetime(2024, 1, 15)
        mock_datetime.datetime = datetime
        mock_datetime.strftime = datetime.strftime
        
        mock_get_shift.return_value = "ALFA"
        
        # Mock para o diálogo de salvamento
        mock_filedialog.asksaveasfilename.return_value = "teste_relatorio.xlsx"
        
        # Executa a função a ser testada
        create_excel_report(sample_unit_data)
        
        # Verifica se o workbook foi criado
        mock_workbook_class.assert_called_once()
        
        # Verifica se os geradores de planilhas foram chamados para cada unidade
        assert mock_generate_control.call_count == 2
        assert mock_generate_sei.call_count == 2
        
        # Verifica se o arquivo foi salvo
        mock_workbook.save.assert_called_once_with("teste_relatorio.xlsx")
    
    @patch('services.report_service.Workbook')
    @patch('services.report_service.filedialog')
    def test_create_excel_report_cancelled(self, mock_filedialog, mock_workbook_class, sample_unit_data):
        """Testa o comportamento quando o usuário cancela o salvamento do relatório."""
        # Configuração dos mocks
        mock_workbook = MagicMock()
        mock_workbook_class.return_value = mock_workbook
        
        # Mock para o diálogo de salvamento cancelado
        mock_filedialog.asksaveasfilename.return_value = ""
        
        # Executa a função a ser testada
        create_excel_report(sample_unit_data)
        
        # Verifica se o workbook foi criado (é criado mesmo quando cancelado)
        mock_workbook_class.assert_called_once()
        
        # Verifica que o save não foi chamado quando o caminho está vazio
        mock_workbook.save.assert_not_called()
    
    @patch('services.report_service.Workbook')
    @patch('services.report_service.filedialog')
    @patch('services.report_service.datetime')
    @patch('services.report_service.get_shift_name')
    def test_create_excel_report_empty_data(self, mock_get_shift, mock_datetime, 
                                        mock_filedialog, mock_workbook_class):
        """Testa o comportamento quando não há dados para gerar o relatório."""
        # Configuração dos mocks
        mock_workbook = MagicMock()
        mock_workbook_class.return_value = mock_workbook
        
        # Mock para o diálogo de salvamento
        mock_filedialog.asksaveasfilename.return_value = "teste_relatorio.xlsx"
        
        # Executa a função com dados vazios
        create_excel_report({})
        
        # Verifica se o workbook foi criado (é criado mesmo com dados vazios)
        mock_workbook_class.assert_called_once()
        
        # Verifica que nenhuma aba de planilha foi gerada para unidades
        assert mock_workbook.create_sheet.call_count == 0
    
    def test_alignment_creation(self):
        """Testa a criação de alinhamentos para células Excel."""
        # Criando objetos reais de alinhamento
        center_alignment = Alignment(horizontal='center', vertical='center')
        left_alignment = Alignment(horizontal='left', vertical='center')
        
        # Verificar as propriedades dos objetos
        assert center_alignment.horizontal == 'center'
        assert center_alignment.vertical == 'center'
        
        assert left_alignment.horizontal == 'left'
        assert left_alignment.vertical == 'center' 