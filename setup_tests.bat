@echo off
echo Instalando dependências de desenvolvimento...
pip install -r requirements-dev.txt

echo.
echo Configuração concluída! Agora você pode executar os testes usando:
echo python tests/run_tests.py
echo.
echo Ou para mais opções:
echo python tests/run_tests.py --help 