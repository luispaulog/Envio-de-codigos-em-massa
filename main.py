import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header
import time
import logging
import os
import PySimpleGUI as sg
import threading
import json
from typing import List, Dict

# Constants
CONFIG_FILE = 'config.json'
LOG_FILE = 'envio_emails.log'
DEFAULT_CONFIG = {
    'SMTP_SERVER': 'smtp.seu-servidor.com',
    'PORTA': '587',
    'EMAIL_USUARIO': 'seu-email@dominio.com',
    'SENHA_USUARIO': '',
    'ASSUNTO_EMAIL': 'Seu Código Único',
    'ARQUIVO_EMAILS': 'emails.txt',
    'ARQUIVO_CODIGOS': 'codigos.txt',
    'TEMPO_FILA': '2',
    'REMETENTE_NOME': 'NOME EMPRESA',
    'EMAIL_SAUDACAO': 'Prezado(a),',
    'EMAIL_INSTRUCAO': 'Utilize-o conforme as instruções que você recebeu.',
    'EMAIL_ASSINATURA': 'Atenciosamente,',
    'EMAIL_EQUIPE': 'Equipe xxx',
    'MENSAGEM_PERSONALIZADA': 'Segue abaixo o seu código único:'
}

# Fixed UI text
BOTAO_INICIAR = 'Iniciar Envio'
TITULO_JANELA = 'Envio de Emails em Massa'
POPUP_SUCESSO = 'Envio de emails concluído com sucesso.'
POPUP_ERRO = 'Ocorreu um erro:'

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class ConfigManager:
    @staticmethod
    def load() -> Dict:
        try:
            with open(CONFIG_FILE, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return DEFAULT_CONFIG

    @staticmethod
    def save(config: Dict) -> None:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)


class FileHandler:
    @staticmethod
    def read_file(filename: str) -> List[str]:
        with open(filename, 'r') as file:
            return [line.strip() for line in file]

    @staticmethod
    def create_example_files() -> None:
        for filename, content in {
            DEFAULT_CONFIG['ARQUIVO_EMAILS']: ['exemplo@dominio.com', 'outro@dominio.com'],
            DEFAULT_CONFIG['ARQUIVO_CODIGOS']: ['CODIGO123', 'CODIGO456']
        }.items():
            if not os.path.exists(filename):
                with open(filename, 'w') as file:
                    file.write('\n'.join(content))


class EmailSender:
    def __init__(self, config: Dict):
        self.config = config
        self.smtp_server = config['SMTP_SERVER']
        self.port = int(config['PORTA'])
        self.user = config['EMAIL_USUARIO']
        self.password = config['SENHA_USUARIO']
        self.tempo_fila = int(config['TEMPO_FILA'])

    def send_email(self, email_destino: str, codigo: str) -> None:
        mensagem = MIMEMultipart()
        mensagem['From'] = formataddr(
            (str(Header(self.config['REMETENTE_NOME'], 'utf-8')), self.user))
        mensagem['To'] = email_destino
        mensagem['Subject'] = self.config['ASSUNTO_EMAIL']

        corpo = f"""
        <html>
        <body>
            <p>{self.config['EMAIL_SAUDACAO']}</p>
            <p>{self.config['MENSAGEM_PERSONALIZADA']}</p>
            <h2 style="color: #2E86C1;">{codigo}</h2>
            <p>{self.config['EMAIL_INSTRUCAO']}</p>
            <p>{self.config['EMAIL_ASSINATURA']}</p>
            <p>{self.config['EMAIL_EQUIPE']}</p>
        </body>
        </html>
        """

        mensagem.attach(MIMEText(corpo, 'html'))

        with smtplib.SMTP(self.smtp_server, self.port) as servidor:
            servidor.starttls()
            servidor.login(self.user, self.password)
            servidor.sendmail(self.user, email_destino, mensagem.as_string())
        logging.info(f"Email enviado para {
                     email_destino} com o código {codigo}.")

    def start_sending(self, emails: List[str], codigos: List[str], window: sg.Window) -> None:
        try:
            if len(emails) != len(codigos):
                raise ValueError(
                    "A quantidade de códigos não corresponde à quantidade de emails.")

            logging.info("Iniciando o envio de emails.")
            for i, (email, codigo) in enumerate(zip(emails, codigos)):
                self.send_email(email, codigo)
                time.sleep(self.tempo_fila)
                window['PROGRESSO'].update(i + 1, len(emails))

            logging.info("Envio de emails concluído.")
            window.write_event_value('ENVIO_CONCLUIDO', None)
        except Exception as e:
            logging.error(str(e))
            window.write_event_value('ERRO', str(e))


class GUI:
    def __init__(self):
        self.config = ConfigManager.load()
        self.window = self.create_window()

    def create_window(self) -> sg.Window:
        sg.theme('SystemDefault1')
        layout = [
            [sg.Text('Servidor SMTP:', size=(18, 1), justification='right'), sg.InputText(
                self.config['SMTP_SERVER'], key='SMTP_SERVER', size=(40, 1))],
            [sg.Text('Porta:', size=(18, 1), justification='right'), sg.InputText(
                self.config['PORTA'], key='PORTA', size=(40, 1))],
            [sg.Text('Email do Usuário:', size=(18, 1), justification='right'), sg.InputText(
                self.config['EMAIL_USUARIO'], key='EMAIL_USUARIO', size=(40, 1))],
            [sg.Text('Senha:', size=(18, 1), justification='right'), sg.InputText(
                self.config['SENHA_USUARIO'], key='SENHA_USUARIO', password_char='*', size=(40, 1))],
            [sg.Text('Assunto do Email:', size=(18, 1), justification='right'), sg.InputText(
                self.config['ASSUNTO_EMAIL'], key='ASSUNTO_EMAIL', size=(40, 1))],
            [sg.Text('Arquivo de Emails:', size=(18, 1), justification='right'), sg.InputText(
                self.config['ARQUIVO_EMAILS'], key='ARQUIVO_EMAILS', size=(40, 1)), sg.FileBrowse()],
            [sg.Text('Arquivo de Códigos:', size=(18, 1), justification='right'), sg.InputText(
                self.config['ARQUIVO_CODIGOS'], key='ARQUIVO_CODIGOS', size=(40, 1)), sg.FileBrowse()],
            [sg.Text('Tempo entre envios (s):', size=(18, 1), justification='right'), sg.InputText(
                self.config['TEMPO_FILA'], key='TEMPO_FILA', size=(40, 1))],
            [sg.Text('Nome do Remetente:', size=(18, 1), justification='right'), sg.InputText(
                self.config['REMETENTE_NOME'], key='REMETENTE_NOME', size=(40, 1))],
            [sg.Text('Saudação do Email:', size=(18, 1), justification='right'), sg.InputText(
                self.config['EMAIL_SAUDACAO'], key='EMAIL_SAUDACAO', size=(40, 1))],
            [sg.Text('Mensagem Personalizada:', size=(18, 1), justification='right'), sg.InputText(
                self.config['MENSAGEM_PERSONALIZADA'], key='MENSAGEM_PERSONALIZADA', size=(40, 1))],
            [sg.Text('Instrução do Email:', size=(18, 1), justification='right'), sg.InputText(
                self.config['EMAIL_INSTRUCAO'], key='EMAIL_INSTRUCAO', size=(40, 1))],
            [sg.Text('Assinatura do Email:', size=(18, 1), justification='right'), sg.InputText(
                self.config['EMAIL_ASSINATURA'], key='EMAIL_ASSINATURA', size=(40, 1))],
            [sg.Text('Nome da Equipe:', size=(18, 1), justification='right'), sg.InputText(
                self.config['EMAIL_EQUIPE'], key='EMAIL_EQUIPE', size=(40, 1))],
            [sg.ProgressBar(max_value=100, orientation='h',
                            size=(46, 20), key='PROGRESSO')],
            [sg.Button(BOTAO_INICIAR, key='INICIAR',
                       size=(15, 1), pad=((190, 0), (10, 0)))]
        ]
        return sg.Window(TITULO_JANELA, layout, element_justification='center', finalize=True)

    def run(self) -> None:
        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED:
                break
            elif event == 'INICIAR':
                self.start_sending_thread(values)
            elif event == 'ENVIO_CONCLUIDO':
                sg.popup("Sucesso", POPUP_SUCESSO)
            elif event == 'ERRO':
                sg.popup_error("Erro", f"{POPUP_ERRO} {values['ERRO']}")

        self.window.close()

    def start_sending_thread(self, values: Dict) -> None:
        self.config.update(values)
        ConfigManager.save(self.config)

        emails = FileHandler.read_file(values['ARQUIVO_EMAILS'])
        codigos = FileHandler.read_file(values['ARQUIVO_CODIGOS'])

        email_sender = EmailSender(self.config)
        thread = threading.Thread(
            target=email_sender.start_sending,
            args=(emails, codigos, self.window)
        )
        thread.start()


if __name__ == "__main__":
    FileHandler.create_example_files()
    gui = GUI()
    gui.run()
