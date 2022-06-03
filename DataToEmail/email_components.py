import os
import json
import smtplib
import ssl
from pathlib import Path
from typing import Union
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_config(config_opt, file_name='config.json'):
    curr_dir = os.getcwd()
    with open(os.path.join(curr_dir, '../config', file_name), 'r') as file:
        details = json.loads(file.read())
    return details[config_opt]


class EmailManager:
    _ssl_port = 465
    _starttls_port = 587

    def __init__(self, provider, smtp_server, sender, recipients, password, name):
        self._sender_email = sender
        self._recipient_email = recipients
        self._password = password
        self._smtp_server = smtp_server
        self._name = name
        if provider == 'outlook':
            self.ssl_port = self._starttls_port
        else:
            self.ssl_port = self._ssl_port

    @classmethod
    def setup(cls, provider='gmail', smtp_server='smtp.gmail.com', name='test', **kwargs):
        _details = get_config('profile')
        if name in _details.keys():
            creds = _details[name]
            _sender = creds['sender']
            _password = creds['password']
            _recipients = creds['recipients']
            assert all([_sender, _password, _recipients])
        else:
            raise Exception('Profile name does not exist')

        _smtp_server = kwargs.get('smtp_server', 'smtp.gmail.com')
        if provider == 'outlook':
            _smtp_server = 'smtp.office365.com'

        return cls(provider, _smtp_server, _sender, _recipients, _password, name)

    def send_email(self, message):
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self._smtp_server, self.ssl_port, context=context) as server:
                server.login(self._sender_email, self._password)
                server.sendmail(self._sender_email, self._recipient_email, message)
        except Exception as e:
            with smtplib.SMTP(self._smtp_server, self.ssl_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self._sender_email, self._password)
                server.sendmail(self._sender_email, self._recipient_email, message)


class Email:
    def __init__(self):
        self._parts = []
        self.message = MIMEMultipart()
        self._template_flag = False

    @staticmethod
    def _header(emailmgr: EmailManager, **kwargs):
        assert isinstance(emailmgr, EmailManager)
        sender = emailmgr._sender_email
        profile = get_config('profile')[emailmgr._name]
        recipients = profile.get('recipients', '')
        cc = profile.get('cc', '')
        bcc = profile.get('bcc', '')
        subject = kwargs.get('subject', '')
        return sender, recipients, cc, bcc, subject

    def add_body(self, body_content, body_type):
        if not self._template_flag:
            _body = MIMEText(body_content, body_type)
            self._parts.append(_body)
            self._template_flag = True
        else:
            raise Exception('Template already added.')

    def add_attachments(self, filename):
        with open(filename, 'rb') as attachment:
            _part = MIMEBase("application", "octet-stream")
            _part.set_payload(attachment.read())

        encoders.encode_base64(_part)

        _part.add_header(
            "Content-Disposition",
            f'attachment; filename="{filename}"',
        )
        self._parts.append(_part)

    def compose(self, emailmgr, **kwargs):
        sender, recipients, cc, bcc, subject = self._header(emailmgr, **kwargs)
        self.message['From'] = sender
        self.message['To'] = recipients
        self.message['Subject'] = subject
        self.message['Cc'] = cc
        self.message['Bcc'] = bcc
        for part in self._parts:
            self.message.attach(part)
        return self.message.as_string()

    def body_from_template(self, file_path: Union[str, Path], **templ_params):
        assert os.path.exists(file_path) is True, 'Not a valid template file path'

        _, ext = os.path.splitext(file_path)
        with open(os.path.join(file_path), 'r') as file:
            body = file.read()
            body_type = 'plain' if 'txt' in ext else 'html'

        if bool(templ_params):
            body = body.format(**templ_params)

        self.add_body(body, body_type)
        self._template_flag = True

