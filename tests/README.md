# Testes Automatizados - Canaime Preso por Ala

Este diretório contém os testes automatizados para o sistema de geração de relatórios de presos por ala.

## Estrutura de Testes

Os testes estão organizados da seguinte forma:

- `unit/`: Testes unitários que verificam o funcionamento isolado de cada componente
- `integration/`: Testes de integração que verificam como os componentes trabalham juntos
- `conftest.py`: Arquivo de configuração do pytest com fixtures comuns
- `run_tests.py`: Script para facilitar a execução dos testes

## Requisitos

Para executar os testes, você precisa instalar as dependências de desenvolvimento:

```
pip install pytest pytest-cov pytest-mock
```

## Executando os Testes

### Usando o script run_tests.py

O script `run_tests.py` facilita a execução dos testes com diferentes configurações:

```
# Executar todos os testes
python tests/run_tests.py

# Executar apenas testes unitários
python tests/run_tests.py --type unit

# Executar apenas testes de integração
python tests/run_tests.py --type integration

# Executar com saída detalhada
python tests/run_tests.py --verbose
```

### Usando pytest diretamente

Também é possível executar os testes diretamente com o pytest:

```
# Executar todos os testes com cobertura
pytest tests/ --cov=. --cov-report=term --cov-report=html

# Executar um arquivo de teste específico
pytest tests/unit/test_data_processor.py

# Executar um teste específico
pytest tests/unit/test_data_processor.py::TestUnitProcessor::test_normalize_text
```

## Relatórios de Cobertura

Após executar os testes com a flag `--cov`, será gerado um relatório de cobertura de código:

- No terminal (com `--cov-report=term`)
- Em HTML (com `--cov-report=html`), disponível na pasta `htmlcov/`

## Adicionando Novos Testes

Para adicionar novos testes:

1. Para testes unitários, crie ou edite arquivos em `tests/unit/`
2. Para testes de integração, crie ou edite arquivos em `tests/integration/`
3. Siga o padrão de nomenclatura: `test_nome_do_modulo.py`
4. As classes de teste devem começar com `Test` e os métodos com `test_`

## Fixtures e Mocks

As fixtures comuns para todos os testes estão definidas em `conftest.py`. Elas incluem:

- `mock_playwright`: Mock para o Playwright para não precisar iniciar um navegador real
- `mock_tkinter`: Mock para o Tkinter para não precisar abrir janelas gráficas

Para criar mocks específicos para cada teste, use `@pytest.fixture` dentro das classes de teste. 