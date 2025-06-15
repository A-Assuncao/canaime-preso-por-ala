# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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