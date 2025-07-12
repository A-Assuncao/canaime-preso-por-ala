# Canaimé - Planilha PAMC

Sistema automatizado para geração de planilhas PAMC do sistema Canaimé.

## Funcionalidades

- **Login automatizado** no sistema Canaimé com detecção robusta de erros
- **Coleta de dados** da PAMC com processamento otimizado
- **Geração de planilhas Excel** com abas Controle e SEI automatizadas
- **Sistema de validação** que detecta presos não mapeados antes do processamento
- **Interface gráfica moderna** com janelas de erro informativas e amigáveis
- **Sistema de atualizações automáticas** para manter o programa sempre atualizado
- **Logs detalhados** com separação visual e informações de sessão completas
- **Configuração segura** via arquivo `.env` para proteção de credenciais

## Sistema de Logs

O sistema agora possui um sistema de logs aprimorado com separação visual clara entre execuções:

### Exemplo de Log

```
================================================================================
INICIANDO PROGRAMA - 12/01/2025 10:30:15,123
Versão: v1.0.0
Sistema: Windows 10.0.19045
Usuário: usuario123
2025-01-12 10:30:15,124 - INFO - Iniciando a aplicação Canaimé...
2025-01-12 10:30:15,125 - INFO - O status de atualização automática: Nenhuma atualização disponível
2025-01-12 10:30:20,456 - INFO - Iniciando processo de login...
2025-01-12 10:30:20,457 - INFO - Tentando acessar https://canaime.com.br/sgp2rr/login/login_principal.php (verificação SSL desabilitada)
2025-01-12 10:30:20,458 - INFO - Iniciando o login...
2025-01-12 10:30:20,789 - INFO - Obteve resposta inicial com status: 200
2025-01-12 10:30:20,790 - INFO - Realizando login com usuário: 007msn88
2025-01-12 10:30:23,123 - INFO - Resposta do login: status=200, url=https://canaime.com.br/sgp2rr/areas/index_areas.php
2025-01-12 10:30:23,124 - INFO - Login realizado com sucesso
2025-01-12 10:30:23,125 - INFO - Login foi bem sucedido
2025-01-12 10:30:23,126 - INFO - Iniciando a lista da PAMC...
2025-01-12 10:30:35,789 - INFO - Processados 1820 registros da PAMC
2025-01-12 10:30:35,790 - INFO - Número de presos por cela calculado.
2025-01-12 10:30:35,791 - INFO - Aba "Controle" preenchida.
2025-01-12 10:30:35,792 - INFO - Aba "SEI" preenchida.
2025-01-12 10:30:35,793 - INFO - Preenchendo a aba Controle no excel...
2025-01-12 10:30:35,794 - INFO - Preenchendo a aba SEI no excel...
2025-01-12 10:30:35,795 - INFO - Salvando arquivo excel...
2025-01-12 10:30:42,123 - INFO - Arquivo salvo como: PLANTÃO 12012025_103042.xlsx (156789 bytes)
2025-01-12 10:30:42,124 - INFO - Encerrando processos em segundo plano...
2025-01-12 10:30:42,125 - INFO - Encerrando aplicação...
================================================================================
FINALIZANDO PROGRAMA - 12/01/2025 10:30:42,126
================================================================================
```

### Características do Sistema de Logs

- **Separação Visual**: Linhas de `=` separam cada execução do programa
- **Timestamp Detalhado**: Formato `dd/mm/aaaa HH:mm:ss,mmm` com milissegundos
- **Informações de Sessão**: Versão, sistema operacional e usuário no início
- **Logs Únicos**: Eliminação de mensagens duplicadas
- **Detecção de Erros**: Logs específicos para falhas de login e outros erros

## Sistema de Validação

O sistema agora inclui validação automática de presos não mapeados:

### Validação de Presos Não Mapeados

Quando presos são encontrados em alas/celas que não estão configuradas no sistema, o programa:

1. **Detecta automaticamente** os presos não mapeados
2. **Interrompe o processamento** antes de gerar planilhas incompletas
3. **Exibe uma janela de erro** detalhada com:
   - Lista completa de presos não mapeados
   - Código, nome, ala e cela de cada preso
   - Botão para copiar a lista completa
   - Instruções para correção

### Exemplo de Janela de Erro

```
❌ ERRO DE VALIDAÇÃO

Os seguintes presos não puderam ser mapeados para alas/celas válidas:

PRESOS NÃO MAPEADOS ENCONTRADOS:
======================================================================
 1. Código: 12345    | Nome: João Silva                    | Ala: A01      | Cela: 15
 2. Código: 67890    | Nome: Maria Santos                  | Ala: B02      | Cela: 22
 3. Código: 11111    | Nome: Pedro Costa                   | Ala: C03      | Cela: 08
======================================================================
TOTAL: 3 presos não mapeados

INSTRUÇÕES:
1. Copie esta lista usando o botão 'Copiar Lista'
2. Verifique as alas e celas no sistema Canaimé
3. Atualize a configuração das unidades se necessário
4. Execute o programa novamente

[📋 Copiar Lista] [❌ Fechar]
```

### Benefícios da Validação

- **Prevenção de Erros**: Evita planilhas com dados incompletos
- **Facilita Correção**: Lista clara e copiável dos problemas
- **Logs Detalhados**: Registro completo no `app_log.log`
- **Interface Amigável**: Janela de erro informativa e fácil de usar
- **Funcionamento Garantido**: Sistema corrigido para sempre exibir a janela de erro ao usuário

### Correções Recentes (v1.0.2)

O sistema de validação foi aprimorado para garantir que as janelas de erro sejam sempre exibidas:

- **Correção Crítica**: Resolvido problema onde mensagens de presos não mapeados não chegavam na interface
- **Timing Aprimorado**: Implementado delay para garantir processamento das mensagens entre processos
- **Logs Limpos**: Removidas mensagens de contagem regressiva que não agregavam valor
- **Interface Responsiva**: Melhor experiência do usuário durante erros de validação

## Instalação

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as credenciais no arquivo `.env`
4. Execute: `python main.py`

## Configuração

### 1. Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Credenciais do Sistema Canaimé
CANAIME_USER=seu_usuario_aqui
CANAIME_PASSWORD=sua_senha_aqui

# URLs do Sistema
CANAIME_BASE_URL=https://canaime.com.br

# Webhook do Discord para notificações de erro (opcional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/seu_webhook_aqui

# URL de Atualizações
UPDATE_URL=https://github.com/A-Assuncao/canaime-preso-por-ala/releases/latest/download/
```

### 2. Variáveis de Ambiente

- **CANAIME_USER**: Seu usuário do sistema Canaimé
- **CANAIME_PASSWORD**: Sua senha do sistema Canaimé
- **CANAIME_BASE_URL**: URL base do sistema (padrão: https://canaime.com.br)
- **DISCORD_WEBHOOK_URL**: Webhook do Discord para notificações de erro (opcional)
- **UPDATE_URL**: URL para verificar atualizações automáticas

### 3. Segurança

⚠️ **IMPORTANTE**: 
- O arquivo `.env` contém dados sensíveis e NÃO deve ser compartilhado
- O arquivo `.env` já está no `.gitignore` para não ser commitado
- Use o arquivo `.env.example` como template

## Uso

1. Execute o programa
2. Digite suas credenciais na interface de login
3. Aguarde o processamento automático
4. Escolha onde salvar a planilha gerada

## Estrutura do Projeto

```
canaime-preso-por-ala/
├── config/          # Configurações do sistema
├── data/           # Processamento de dados
├── gui/            # Interface gráfica
├── services/       # Serviços de autenticação e relatórios
├── utils/          # Utilitários e logger
├── views/          # Visualizações
├── main.py         # Arquivo principal
└── requirements.txt # Dependências
```

## Logs

Todos os logs são salvos em `app_log.log` na raiz do projeto. O sistema agora inclui:

- Separação visual entre execuções
- Informações detalhadas de sessão
- Detecção aprimorada de erros
- Logs únicos sem duplicação

## Troubleshooting

### Problemas Comuns

#### Janela de Erro de Validação Não Aparece
- **Problema**: Presos não mapeados detectados mas janela não é exibida
- **Solução**: Atualizar para v1.0.2 ou superior - problema foi corrigido
- **Verificação**: Consultar `app_log.log` para confirmar detecção dos presos não mapeados

#### Logs Muito Verbosos
- **Problema**: Muitas mensagens de "aguardando mensagens pendentes"
- **Solução**: Atualizar para v1.0.2 - logs foram limpos e otimizados
- **Benefício**: Logs mais focados e informativos

#### Login Não Funciona
- **Problema**: Credenciais corretas mas login falha
- **Verificação**: Consultar logs para ver URL de redirecionamento
- **Solução**: Verificar conectividade e credenciais no arquivo `.env`

#### Presos Não Mapeados
- **Problema**: Alguns presos não aparecem na planilha final
- **Solução**: Sistema agora detecta automaticamente e exibe janela de erro
- **Ação**: Copiar lista da janela de erro e atualizar configuração de unidades

## Suporte

Para suporte técnico ou reportar bugs:

1. **Consulte os logs**: Verifique `app_log.log` para informações detalhadas
2. **Versão atual**: Certifique-se de estar usando a versão mais recente
3. **Informações do erro**: Forneça logs completos e descrição do problema
4. **Configuração**: Verifique se o arquivo `.env` está configurado corretamente
