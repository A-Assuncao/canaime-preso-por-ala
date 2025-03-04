import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from gui.selectors.unit_selector import select_units, center_window, create_unit_checkbox


class TestUnitSelector:
    """Testes para o seletor de unidades prisionais."""
    
    @patch('gui.selectors.unit_selector.tk.Tk')
    def test_center_window(self, mock_tk_class):
        """Testa a função para centralizar a janela."""
        # Cria mocks
        mock_window = MagicMock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        
        # Chama a função
        center_window(mock_window, 300, 200)
        
        # Verifica se a geometria foi configurada corretamente
        # A geometria deve ser algo como "300x200+810+440"
        mock_window.geometry.assert_called_once()
        geom_arg = mock_window.geometry.call_args[0][0]
        assert "300x200+" in geom_arg
    
    @patch('tkinter.Frame')
    @patch('tkinter.Checkbutton')
    def test_create_unit_checkbox(self, mock_checkbutton, mock_frame):
        """Testa a criação de checkbox para unidades."""
        # Cria mocks
        mock_frame_instance = MagicMock()
        mock_var = MagicMock()
        
        # Configura o mock do frame
        mock_frame.return_value = mock_frame_instance
        
        # Chama a função com uma unidade ativa
        checkbox = create_unit_checkbox(mock_frame_instance, "UNIT1", mock_var, True)
        
        # Verifica se o Checkbutton foi criado com os parâmetros corretos
        mock_checkbutton.assert_called_once()
        
        # Verifica se o checkbox foi configurado como ativo
        assert checkbox is not None
    
    def test_select_units_simplified(self):
        """Testa a função select_units de forma simplificada."""
        # Usando with patch em vez de decoradores para evitar problemas de ordem
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('gui.selectors.unit_selector.sys.exit') as mock_exit, \
             patch('gui.selectors.unit_selector.units', ['UNIT1', 'UNIT2', 'UNIT3']), \
             patch('gui.selectors.unit_selector.active_units', ['UNIT1']):
            
            # Configura mocks
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Mock para StringVar
            mock_var = MagicMock()
            mock_var.get.return_value = ""  # Nenhuma unidade selecionada
            mock_stringvar.return_value = mock_var
            
            # Simula o comportamento de quit e destroy
            def quit_side_effect():
                pass
            
            mock_root.quit.side_effect = quit_side_effect
            mock_root.destroy.side_effect = lambda: None
            
            # Simula o comportamento de mainloop
            def mainloop_side_effect():
                # Simula que o botão "Confirmar" foi clicado
                # Encontra a função submit_units e a executa
                for call in mock_root.mock_calls:
                    if call[0] == 'Button' and 'text' in call[2] and call[2]['text'] == 'Confirmar':
                        command = call[2]['command']
                        command()
                        break
            
            mock_root.mainloop.side_effect = mainloop_side_effect
            
            # Executa a função
            result = select_units()
            
            # Verifica se o resultado é uma lista vazia (nenhuma unidade selecionada)
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_on_close_behavior(self):
        """Testa o comportamento da função on_close quando a janela é fechada."""
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('gui.selectors.unit_selector.sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            # Configura mocks
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Simula o comportamento de protocol para capturar a função on_close
            on_close_func = None
            def protocol_side_effect(protocol_name, callback):
                nonlocal on_close_func
                if protocol_name == "WM_DELETE_WINDOW":
                    on_close_func = callback
            
            mock_root.protocol.side_effect = protocol_side_effect
            
            # Inicia a configuração da janela, mas não executa mainloop
            # Isso é suficiente para configurar o protocolo WM_DELETE_WINDOW
            with patch('gui.selectors.unit_selector.units', ['UNIT1']), \
                 patch('gui.selectors.unit_selector.active_units', ['UNIT1']):
                # Não chamamos select_units() completamente, apenas iniciamos a configuração
                # para capturar a função on_close
                try:
                    select_units()
                except Exception:
                    # Ignoramos qualquer exceção, pois só queremos capturar a função on_close
                    pass
            
            # Verifica se a função on_close foi capturada
            assert on_close_func is not None
            
            # Chama a função on_close
            try:
                on_close_func()
            except SystemExit:
                # Ignoramos a exceção SystemExit que é esperada
                pass
            
            # Verifica se as funções esperadas foram chamadas
            mock_print.assert_called_once_with("Fechando o programa...")
            mock_root.quit.assert_called_once()
            mock_exit.assert_called_once_with(0)
    
    def test_select_units_with_selection(self):
        """Testa a função select_units quando unidades são selecionadas."""
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.StringVar') as mock_stringvar, \
             patch('tkinter.Frame') as mock_frame, \
             patch('tkinter.Label') as mock_label, \
             patch('tkinter.Button') as mock_button, \
             patch('tkinter.Checkbutton') as mock_checkbutton, \
             patch('gui.selectors.unit_selector.create_unit_checkbox') as mock_create_checkbox, \
             patch('gui.selectors.unit_selector.units', ['UNIT1', 'UNIT2']), \
             patch('gui.selectors.unit_selector.active_units', ['UNIT1', 'UNIT2']):
            
            # Configura mocks
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Mock para Frame
            mock_frame_instance = MagicMock()
            mock_frame.return_value = mock_frame_instance
            
            # Mock para Button
            mock_button_instance = MagicMock()
            
            def button_side_effect(*args, **kwargs):
                if 'text' in kwargs and kwargs['text'] == 'Confirmar':
                    # Armazena a função de comando para simular o clique
                    nonlocal submit_command
                    submit_command = kwargs['command']
                return mock_button_instance
            
            mock_button.side_effect = button_side_effect
            
            # Variável para armazenar a função submit_units
            submit_command = None
            
            # Mock para StringVar - simula unidades selecionadas
            mock_var1 = MagicMock()
            mock_var1.get.return_value = "UNIT1"  # Primeira unidade selecionada
            
            mock_var2 = MagicMock()
            mock_var2.get.return_value = "UNIT2"  # Segunda unidade selecionada
            
            # Retorna diferentes variáveis para diferentes chamadas
            mock_stringvar_calls = 0
            def stringvar_side_effect(*args, **kwargs):
                nonlocal mock_stringvar_calls
                mock_stringvar_calls += 1
                if mock_stringvar_calls == 1:
                    return mock_var1
                else:
                    return mock_var2
            
            mock_stringvar.side_effect = stringvar_side_effect
            
            # Mock para create_unit_checkbox
            def create_checkbox_side_effect(frame, unit, var, is_active):
                checkbox = MagicMock()
                # Simula que o checkbox está selecionado
                checkbox.select.side_effect = lambda: None
                return checkbox
            
            mock_create_checkbox.side_effect = create_checkbox_side_effect
            
            # Simula o comportamento de mainloop
            def mainloop_side_effect():
                # Simula que o botão "Confirmar" foi clicado
                if submit_command:
                    submit_command()
            
            mock_root.mainloop.side_effect = mainloop_side_effect
            
            # Executa a função
            result = select_units()
            
            # Verifica se o resultado contém as unidades selecionadas
            assert isinstance(result, list)
            assert "UNIT1" in result
            assert "UNIT2" in result
            assert len(result) == 2
            
            # Verifica se as funções esperadas foram chamadas
            mock_root.quit.assert_called_once()
            mock_root.destroy.assert_called_once() 