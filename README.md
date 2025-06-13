# Canaime Preso por Ala

Este projeto tem como objetivo automatizar a coleta de dados de presidiários de diferentes unidades prisionais usando a biblioteca Playwright para navegação automatizada e gerar relatórios detalhados em Excel.

**Versão Atual:** v0.2.2

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

O projeto **Canaime Preso por Ala** é uma ferramenta automatizada que:

- Realiza login automático no sistema de gerenciamento de presidiários
- Permite seleção flexível de unidades prisionais para processamento
- Coleta dados detalhados sobre presos em diferentes alas
- Gera relatórios organizados em formato Excel
- Possui interface gráfica amigável para interação com o usuário
- Inclui sistema de atualização automática
- Mantém logs detalhados das operações

O objetivo principal é fornecer uma ferramenta eficiente para monitoramento e análise de dados de detentos, reduzindo o tempo necessário para coleta manual de informações.

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

2. Uma interface gráfica será aberta solicitando:
   - Login e senha do sistema
   - Seleção das unidades prisionais desejadas
   - Opção de uso de HTTPS (recomendado)

3. Após confirmar, o programa:
   - Realizará login no sistema automaticamente
   - Coletará os dados das unidades selecionadas
   - Exibirá uma janela de status com progresso em tempo real
   - Gerará o relatório em Excel automaticamente

4. O relatório será salvo como `Presos por Ala.xlsx` na pasta do projeto.

## Atualização do Software

O projeto inclui um sistema de atualização automática. Ele verifica se há novas versões disponíveis e aplica as atualizações automaticamente.

- Para verificar e aplicar atualizações, basta executar o script principal (`main.py`). Se uma nova versão estiver disponível, o programa será atualizado e reiniciado automaticamente.

## Estrutura do Projeto

Abaixo está a estrutura atualizada do projeto:

```
📦 canaime-preso-por-ala
│
├── 📂 config             # Arquivos de configuração e geração de planilhas
│   ├── excel_config_control.py  # Configurações da aba 'Controle' do Excel
│   ├── excel_config_sei.py      # Configurações da aba 'SEI' do Excel
│   └── units_config.py        # Configurações das unidades e alas
│
├── 📂 data               # Manipulação e processamento de dados
│   ├── data_processor.py       # Processa e formata os dados extraídos
│   └── 📂 processed           # Armazenar dados gerados em tempo de execução
│
├── 📂 gui                # Interface gráfica com o usuário
│   ├── 📂 login                # Componentes relacionados ao login
│   │   └── login_canaime.py    # Tela de login para o sistema Canaimé
│   └── 📂 selectors            # Componentes de seleção
│       └── unit_selector.py    # Seleção de unidades para geração de relatório
│
├── 📂 services           # Serviços principais
│   ├── playwright_service.py   # Executa tarefas usando Playwright
│   └── report_service.py       # Gera relatórios Excel
│
├── 📂 utils              # Utilitários do sistema
│   ├── logger.py              # Sistema de logging
│   └── updater.py             # Sistema de atualização automática
│
├── .gitignore            # Arquivos e pastas ignoradas pelo Git
├── LICENSE               # Licença do projeto
├── main.py               # Ponto de entrada da aplicação
├── README.md             # Este arquivo
└── requirements.txt      # Dependências do projeto
```

## Contribuição

1. Faça um fork do projeto.

2. Crie uma branch para sua feature (`git checkout -b feature/SuaFeature`).

3. Commit suas mudanças (`git commit -m 'Adiciona a SuaFeature'`).

4. Faça um push para a branch (`git push origin feature/SuaFeature`).

5. Abra um Pull Request.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENÇA](LICENSE) para mais detalhes.
