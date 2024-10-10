# Envio de Emails em Massa

Este projeto é uma aplicação de desktop para envio automatizado de emails em massa, desenvolvida em Python. Ela permite enviar códigos únicos para uma lista de endereços de email de forma eficiente e personalizável.

## Características

- Interface gráfica intuitiva usando PySimpleGUI
- Envio de emails personalizados com códigos únicos
- Configuração flexível de servidor SMTP, conteúdo do email e outros parâmetros
- Leitura de listas de emails e códigos a partir de arquivos de texto
- Controle de intervalo entre envios para evitar sobrecarga do servidor
- Salvamento automático de configurações
- Log de atividades para rastreamento de envios

## Requisitos

- Python 3.6+
- PySimpleGUI

## Instalação

1. Clone o repositório ou baixe os arquivos do projeto.
2. Instale as dependências:
   ```
   pip install PySimpleGUI
   ```

## Uso

1. Execute o script principal:
   ```
   python nome_do_script.py
   ```
2. Na interface gráfica, preencha os campos necessários:
   - Configurações do servidor SMTP
   - Detalhes do email (remetente, assunto, conteúdo)
   - Caminhos para os arquivos de emails e códigos
   - Intervalo entre envios
3. Clique em "Iniciar Envio" para começar o processo.

## Configuração

- `emails.txt`: Lista de endereços de email de destino (um por linha)
- `codigos.txt`: Lista de códigos únicos correspondentes (um por linha)
- As configurações são salvas automaticamente em `config.json` após cada uso

## Notas

- Certifique-se de que a quantidade de emails corresponde à quantidade de códigos
- Verifique as políticas de spam e limites de envio do seu provedor de email
- Use com responsabilidade e em conformidade com as leis de proteção de dados

## Contribuições

Contribuições são bem-vindas. Por favor, abra uma issue para discutir mudanças importantes antes de submeter um pull request.

## Licença

[MIT License](https://opensource.org/licenses/MIT)