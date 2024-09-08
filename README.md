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

Abaixo está a estrutura de pastas e arquivos do projeto:

```
📦 canaime-preso-por-ala
│
├── 📂 config             # Arquivos de configuração e geração de planilhas
│   ├── excel_config_control.py  # Configurações da aba 'Controle' do Excel
│   ├── excel_config_sei.py      # Configurações da aba 'SEI' do Excel
│   └── units_config.json        # Configurações das unidades e alas
│
├── 📂 data               # Manipulação e processamento de dados
│   ├── data_processor.py       # Processa e formata os dados extraídos
│
├── 📂 gui                # Interface gráfica com o usuário (login e seleção de unidades)
│   ├── login_canaime.py        # Tela de login para o sistema Canaimé
│   └── unit_selector.py        # Seleção de unidades para geração de relatório
│
├── 📂 services           # Serviços de integração com Canaimé e geração de relatórios
│   ├── canaime_service.py      # Realiza o login no sistema Canaimé
│   ├── playwright_service.py   # Executa tarefas usando Playwright
│   └── report_service.py       # Gera relatórios Excel com base nos dados extraídos
│
├── 📂 utils              # Utilitários do sistema
│   ├── logger.py              # Captura erros e gera logs
│   └── updater.py             # Verifica atualizações da aplicação
│
├── 📂 venv               # Ambiente virtual (não incluído no GitHub)
│
├── .gitignore            # Arquivos e pastas ignoradas pelo Git
├── LICENSE               # Licença do projeto
├── main.py               # Arquivo principal da aplicação
├── README.md             # Este arquivo
└── requirements.txt      # Lista de dependências do projeto
```

## Contribuição

1. Faça um fork do projeto.

2. Crie uma branch para sua feature (`git checkout -b feature/SuaFeature`).

3. Commit suas mudanças (`git commit -m 'Adiciona a SuaFeature'`).

4. Faça um push para a branch (`git push origin feature/SuaFeature`).

5. Abra um Pull Request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENÇA](LICENSE) para mais detalhes.
