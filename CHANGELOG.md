# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [v1.4.0] - 2026-05-16

### Adicionado
- **Nome comercial do produto:** **Plantão Helper - PAMC** (`APP_DISPLAY_NAME` em `config/config.py`), com tagline e título de janela centralizados (`app_window_title()`).
- Fluxo de atualização com tela **“Download concluído”** e escolha **Abrir nova versão** / **Continuar com a versão atual**.
- Testes: `tests/test_updater_urls.py`, `tests/test_logger_discord.py`, `tests/test_update_helper.py`.

### Alterado
- **Atualização automática** revisada: download com progresso (%, velocidade, ETA); abertura do novo `.exe` via `subprocess.Popen` (sem depender de PowerShell); instalador salvo na pasta do programa (não em `%TEMP%`).
- URL do instalador no GitHub: `canaime-preso-por-ala-v{versão}.exe` (com `v` no nome do arquivo).
- Interface de login exibe **Plantão Helper - PAMC** e tagline em vez de apenas “Planilha PAMC”.
- Versão do aplicativo: **v1.4.0**.

### Corrigido
- Erro de sintaxe na janela de progresso (`update_progress_dialog.py`).
- Envio ao Discord apenas quando `DISCORD_WEBHOOK_URL` está configurada.
- `Ctrl+C` no terminal com app Tkinter (`utils/console_interrupt.py`).
- Lock de atualização liberado após falha ou cancelamento do download.

### Arquivos principais
- `config/config.py`, `gui/login/login_canaime.py`, `utils/updater.py`, `utils/update_helper.py`, `gui/update/update_progress_dialog.py`, `README.md`.

## [v1.3.0] - 2026-05-16

### Adicionado
- **Atualização automática** com helper **PowerShell** (`utils/update_helper.py`): aguarda o PID do app encerrar, inicia o novo `.exe` e remove o script temporário.
- **Janela de progresso** do download (`gui/update/update_progress_dialog.py`): porcentagem, tamanho, velocidade e tempo restante; aviso para não fechar durante o download.
- **Lock de atualização** (`utils/update_lock.py`) para evitar downloads/instâncias duplicados em paralelo.

### Alterado
- `utils/updater.py`: download em thread com arquivo `.part`, destino na pasta do executável, `os._exit` após disparar o helper (libera processo e arquivo antigo).
- `main.py`: verificação de update com `tk.Tk` oculto antes da tela de login.
- Versão do aplicativo: **v1.3.0**.

### Arquivos principais
- `utils/updater.py`, `utils/update_helper.py`, `utils/update_lock.py`, `gui/update/update_progress_dialog.py`, `main.py`, `tests/test_update_helper.py`.

## [v1.2.0] - 2026-05-16

### Adicionado
- **PDF Chamada** (`services/chamada_pdf.py`): alinhamento para impressão **frente e verso** — cada ala (a partir da 2ª) começa em **página ímpar**; se o `PageBreak` cair em página par, insere folha em branco antes do cabeçalho da ala (`_EnsureOddPageStart`).
- Testes em `tests/test_chamada_pdf_odd_pages.py` para validar páginas ímpares de início por ala.

### Alterado
- Versão do aplicativo: **v1.2.0** (`config/config.py`).

### Arquivos principais
- `services/chamada_pdf.py`, `config/config.py`, `README.md`, `tests/test_chamada_pdf_odd_pages.py`.

## [v1.1.0] - 2026-05-08

### Adicionado
- **Modo Contagem**: geração de PDF (`services/contagem_pdf.py`) para conferência numérica por cela, com QTD do sistema (lista PAMC), coluna **PREENCHER** para anotação manual e título por ala (sem linha de descrição de regime).
- Seleção de alas **igual à Chamada** (diálogo Bloco A/B); alas sem lista de celas no `units_config` **não** geram bloco no PDF.
- PDF de contagem em **A4 paisagem**, até **4 alas por linha**, linhas verticais mais grossas entre alas para recorte; cabeçalho institucional (penitenciária, título do documento, emitido/plantão) **repetido em todas as páginas** via callback de página.
- Altura das linhas da mini-tabela ajustada dinamicamente (`rowHeights`) para a maior ala caber no frame do ReportLab, evitando erro de fluxo em alas com muitas celas.
- **Feedback visual de sucesso** na tela de login: linhas em verde no painel de status (`add_status_success`), no mesmo estilo de timestamp dos logs, ao concluir Chamada, Contagem ou fluxo de continuação após validação; mensagem de encerramento atualizada no `main.py`.

### Corrigido
- **PDF Chamada** (`services/chamada_pdf.py`): células da coluna **Qtd** com `BOX` fechado (topo/fundo); `LINEABOVE`/`LINEBELOW` brancos só entre linhas de Qtd vazias; `BOX` da quantidade aplicado por último.
- **Contagem PDF**: correção de `NameError` (`wing_tables` não inicializado); import de `TA_LEFT`; remoção de `KeepTogether` na grade externa onde gerava conflito com o layout.
- **Contagem PDF**: erro “Flowable too large” ao aninhar tabelas altas em página seguinte — resolvido com alturas de linha fixas calculadas a partir da altura útil da página.

### Alterado
- Colunas **QTD** e **PREENCHER** com a mesma largura na mini-tabela de contagem; espaçamento vertical das linhas de dados revisado.

### Arquivos principais
- `services/contagem_pdf.py` (novo), `main.py`, `gui/login/login_canaime.py`, `services/chamada_pdf.py`, `config/config.py`.

## [v1.0.3] - 2025-08-12

### Adicionado
- Botão "✅ Continuar" na janela de validação para prosseguir a geração da planilha ignorando os presos não mapeados.
- Alerta informativo antes de continuar, explicando que os nomes listados NÃO serão contabilizados na planilha final.

### Alterado
- A janela de validação é fechada automaticamente após o usuário confirmar o alerta ao optar por continuar.
- A interface passa a receber os dados já mapeados junto com a mensagem de validação para permitir a continuação local sem reiniciar o processo.

### Arquivos Modificados
- `main.py` – Envio da mensagem de validação incluindo os dados mapeados para a UI.
- `gui/login/login_canaime.py` – Adição do botão "✅ Continuar", fluxo de alerta/continuação e fechamento automático do popup.

## [v1.0.2] - 2025-01-12

### Corrigido
- **CRÍTICO**: Correção na exibição de janela de erro para presos não mapeados
  - Problema onde mensagens de validation_error não chegavam na interface
  - Processo filho terminava antes da mensagem ser processada
  - Adicionado delay de 500ms após envio da mensagem para garantir processamento
  - Corrigido flag de finalização para evitar duplicação de mensagens
- **INTERFACE**: Remoção de logs indesejados de contagem regressiva
  - Removidas mensagens "Processo terminou, aguardando mensagens pendentes..."
  - Logs mais limpos e menos verbosos durante finalização
- **VALIDAÇÃO**: Melhorias na depuração do sistema de validação
  - Adicionados logs de debug para rastrear criação de janelas de erro
  - Melhor rastreamento do fluxo de mensagens entre processos
  - Forçar foco na janela principal antes de criar popups

### Melhorado
- **SISTEMA DE MENSAGENS**: Timing aprimorado na comunicação entre processos
- **EXPERIÊNCIA DO USUÁRIO**: Interface mais responsiva durante erros de validação
- **LOGS**: Sistema de logging mais limpo e focado

### Técnico
- Refatoração da lógica de finalização de processos
- Melhoria no sistema de comunicação via Queue entre processos
- Correção na ordem de execução das funções de validação
- Implementação de flags de controle para evitar duplicação de mensagens

### Arquivos Modificados
- `main.py` - Correção no timing de mensagens validation_error e flags de controle
- `gui/login/login_canaime.py` - Remoção de logs indesejados e melhorias na depuração

## [v1.0.1] - 2025-01-12

### Adicionado
- Sistema de separação visual no log com separadores de sessão
- Informações detalhadas de início e fim de cada execução do programa
- Separação automática entre diferentes execuções do programa
- Informações de versão, sistema operacional e usuário no início da sessão
- Função `section_separator()` para criar separadores visuais em seções importantes
- Formato de timestamp melhorado com milissegundos (dd/mm/aaaa HH:mm:ss,mmm)
- **SEGURANÇA**: Sistema de variáveis de ambiente para dados sensíveis
- Arquivo `.env` para configuração de credenciais e URLs
- Arquivo `.env.example` como template de configuração
- Proteção de dados sensíveis (webhook Discord, URLs do sistema)
- **VALIDAÇÃO**: Sistema de validação de presos não mapeados
- Janela de erro detalhada para presos não mapeados
- Funcionalidade de copiar lista de presos não mapeados
- Interrupção do programa quando presos não mapeados são encontrados

### Corrigido
- **CRÍTICO**: Correção na detecção de login mal-sucedido
  - Sistema agora detecta corretamente quando credenciais estão incorretas
  - Verifica URL final correta (`index_areas.php` para login bem-sucedido)
  - Evita geração de planilhas vazias com valores "0" quando login falha
  - Adiciona múltiplas verificações de segurança para autenticação
- **CRÍTICO**: Correção de logs duplicados
  - Padronização do uso do Logger personalizado em todos os módulos
  - Remoção de handlers duplicados no logger
  - Correção do `data_processor.py` para usar Logger personalizado
  - Limpeza automática de handlers existentes na inicialização

### Melhorado
- Sistema de logging centralizado e padronizado
- Detecção de erros de login mais robusta e informativa
- Mensagens de erro mais claras e específicas para o usuário
- Estrutura de logs mais organizada e legível
- Separação visual simplificada (apenas uma linha de `=` antes do início)
- **SEGURANÇA**: Remoção de dados hardcoded do código fonte
- Configuração flexível via variáveis de ambiente
- Documentação completa de configuração
- **VALIDAÇÃO**: Interface de erro mais amigável e informativa
- Logs detalhados de presos não mapeados
- Prevenção de planilhas com dados incompletos
- **INTERFACE**: Janela de erro de login amigável e informativa
- Mensagens de erro mais claras com ícones e instruções
- Diferenciação entre erros de login e outros tipos de erro
- **INTERFACE**: Janelas de erro maiores e centralizadas
- Melhor aproveitamento do espaço da tela
- Layout mais proporcional e legível

### Técnico
- Refatoração do sistema de logging para evitar duplicações
- Melhoria na arquitetura de detecção de autenticação
- Padronização de imports e uso do logger em todo o projeto
- Implementação de verificações múltiplas para validação de login
- **SEGURANÇA**: Migração de dados sensíveis para variáveis de ambiente
- Implementação de sistema de configuração via `.env`
- Proteção contra commit acidental de dados sensíveis
- **VALIDAÇÃO**: Sistema de validação pré-processamento
- Interface gráfica para exibição de erros de validação
- Integração com sistema de mensagens entre processos
- **INTERFACE**: Sistema de tratamento de erros diferenciado
- Detecção automática de tipos de erro (login vs outros)
- Interface gráfica especializada para erros de autenticação

### Arquivos Modificados
- `services/canaime_service.py` - Correção na detecção de login e URLs via .env
- `utils/logger.py` - Sistema de separação visual e webhook via .env
- `data/data_processor.py` - Padronização do logger, URLs via .env e logs detalhados de validação
- `gui/login/login_canaime.py` - Correção de handlers duplicados, interface de validação e tratamento de erros de login
- `utils/updater.py` - URL de atualização via .env
- `main.py` - Integração com sistema de finalização de sessão e validação de presos
- `.env` - Arquivo de configuração com dados sensíveis
- `.env.example` - Template de configuração
- `README.md` - Documentação de configuração e segurança

### Segurança
- **Webhook Discord**: Movido para variável de ambiente
- **URLs do Sistema**: Configuráveis via variáveis de ambiente
- **Credenciais**: Centralizadas no arquivo `.env`
- **Proteção**: Arquivo `.env` no `.gitignore` para evitar commits acidentais
- **Flexibilidade**: Configuração adaptável para diferentes ambientes

### Validação
- **Presos Não Mapeados**: Detecção automática antes do processamento
- **Interface de Erro**: Janela detalhada com lista formatada
- **Cópia de Dados**: Funcionalidade para copiar lista de presos não mapeados
- **Interrupção Segura**: Programa para antes de gerar planilhas incompletas
- **Logs Detalhados**: Registro completo de presos não mapeados

### Compatibilidade
- Mantém compatibilidade com versões anteriores
- Não altera a interface do usuário
- Preserva todas as funcionalidades existentes
- Configuração opcional via arquivo `.env`

## [1.0.0] - 2024-12-18

### Adicionado
- Sistema completo de login com interface gráfica integrada
- Processamento automático de dados de presos do sistema Canaimé
- Geração de relatórios Excel com cálculo automático de plantões (ALFA, BRAVO, CHARLIE)
- Salvamento de arquivos via diálogo com nomenclatura automática baseada no plantão
- Sistema de configuração de unidades prisionais centralizado
- Integração com planilhas de controle e SEI
- Mapeamento completo de alas e blocos incluindo casos especiais
- Sistema de logging centralizado em arquivo único (app_log.log)
- Encerramento automático da aplicação após processamento
- Suporte completo para prisão domiciliar (PRIS/DOM)

### Funcionalidades Principais
- **Login Automatizado**: Interface gráfica para credenciais do sistema Canaimé
- **Processamento de Dados**: Extração automática de informações de presos
- **Mapeamento de Alas**: Configuração completa de blocos A, B, Externo e Carceragem
- **Geração de Excel**: Preenchimento automático das planilhas de controle e SEI
- **Cálculo de Plantões**: Determinação automática do plantão baseado no horário
- **Casos Especiais**: Suporte para HGR, PRIS/DOM, TRATOX, TRIAGEM e REMIÇÃO

### Corrigido
- **Regex de Extração**: Correção na captura de alas com "/" como PRIS/DOM
- **Mapeamento PRIS/DOM**: Processamento correto de presos em prisão domiciliar
- **KeyError REMIÇÃO**: Normalização de "REMIÇÃO 01/02" para "REMIÇÃO01/02"
- **Imports**: Resolução completa de problemas de importação com sistema híbrido de paths
- **Logging**: Centralização de todos os logs em app_log.log
- **KeyError 'name'**: Correção de erro em excel_config_control.py
- **Encerramento**: Implementação de fechamento completo da aplicação

### Removido
- Funcionalidade de salvamento em JSON
- Arquivo warnings.log separado (centralizado em app_log.log)
- Texto "Pronto para iniciar..." da interface
- Verificação de integridade do arquivo Excel
- Colchetes no nome do arquivo Excel

### Técnico
- Migração para arquitetura MVC com princípios SOLID
- Sistema de paths híbrido com utils/paths.py
- Configuração centralizada em config/
- Separação de responsabilidades entre services/ e data/
- Sistema de logging robusto com captura de erros
- Tratamento de exceções abrangente

### Configurações Suportadas
- **Blocos**: A (Preventivado/Semiaberto), B (Fechado/Saúde/Projetos), Externo, Carceragem
- **Alas Especiais**: PRIS/DOM, HGR, TRATOX, TRIAGEM, REMIÇÃO01/02
- **Unidades**: PAMC (Penitenciária Agrícola de Monte Cristo)

## [0.2.2] - 2024-03-19

### Alterado
- Migração do arquivo de configuração de unidades de `units_config.json` para `units_config.py` para melhor manutenção e tipagem
- Melhorias na interface gráfica de status durante o processamento
- Otimização do sistema de logging para melhor rastreamento de erros

### Corrigido
- Ajuste no sistema de atualização automática para evitar loops infinitos
- Correção na geração de relatórios Excel para unidades sem dados
- Melhor tratamento de erros durante o login no sistema

### Adicionado
- Suporte a HTTPS nas requisições do sistema
- Nova janela de status com animação durante o processamento
- Sistema de fila para comunicação entre processos
- Melhor feedback visual durante o processamento das unidades

## [0.2.1] - 2024-03-12

### Adicionado
- Sistema inicial de atualização automática
- Interface gráfica para seleção de unidades
- Geração de relatórios em Excel
- Sistema de logging básico

### Corrigido
- Problemas de conexão com o sistema Canaimé
- Erros na extração de dados de algumas unidades
- Formatação dos relatórios Excel 