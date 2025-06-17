# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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