# Canaime Preso por Ala

Este projeto tem como objetivo automatizar a coleta de dados de presidiários de diferentes unidades prisionais usando a biblioteca Playwright para navegação automatizada e gerar relatórios detalhados em Excel.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Atualização do Software](#atualização-do-software)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Sobre o Projeto

O projeto **Canaime Preso por Ala** automatiza o login em um sistema de gerenciamento de presidiários, coleta dados sobre presos em diferentes alas de unidades prisionais e gera relatórios em formato Excel. O objetivo é fornecer uma ferramenta eficiente para monitoramento e análise de dados de detentos.

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Acesso à internet para baixar pacotes e realizar atualizações

## Instalação

1. Clone este repositório:

    ```bash
    git clone https://github.com/A-Assuncao/canaime-preso-por-ala.git
    cd canaime-preso-por-ala
    ```

2. Crie um ambiente virtual e ative-o:

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências do projeto:

    ```bash
    pip install -r requirements.txt
    ```

4. Instale o Playwright e seus navegadores necessários:

    ```bash
    playwright install
    ```

## Uso

1. Execute o script principal para iniciar o programa:

    ```bash
    python main.py
    ```

2. Uma interface gráfica será aberta. Digite seu login e senha e selecione as unidades prisionais que deseja processar.

3. Após clicar em "Confirmar", o programa fará login no sistema e coletará os dados.

4. O relatório será gerado em formato Excel e salvo como `Presos por Ala.xlsx` na pasta do projeto.

## Atualização do Software

O projeto inclui um sistema de atualização automática. Ele verifica se há novas versões disponíveis e aplica as atualizações automaticamente.

- Para verificar e aplicar atualizações, basta executar o script principal (`main.py`). Se uma nova versão estiver disponível, o programa será atualizado e reiniciado automaticamente.

## Estrutura do Projeto

```canaime_preso_por_ala/
│
├── main.py
├── gui/
│   ├── __init__.py
│   ├── login_canaime.py
│   ├── unit_selector.py
│
├── services/
│   ├── __init__.py
│   ├── logger_service.py
│   ├── report_service.py
│   ├── canaime_service.py
│
├── utils/
│   ├── __init__.py
│   ├── updater.py
│
├── data/
│   ├── __init__.py
│   ├── data_processor.py
│
└── README.md

```

## Contribuição

1. Faça um fork do projeto.

2. Crie uma branch para sua feature (`git checkout -b feature/SuaFeature`).

3. Commit suas mudanças (`git commit -m 'Adiciona a SuaFeature'`).

4. Faça um push para a branch (`git push origin feature/SuaFeature`).

5. Abra um Pull Request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENÇA](LICENSE) para mais detalhes.
