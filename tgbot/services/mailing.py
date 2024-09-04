import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class AsyncMail:
    def __init__(self, host: str, user: str, password: str, use_tls: bool = True, port: int | str = 465):
        self.host = host
        self.user = user
        self.password = password
        self.use_TLS = use_tls
        self.port = port

    async def send_mail(self, to: list[str] | str, subject: str, text: str, sender: str = 'swapmarketbot@softcraft.ltd', text_type='plain', *, cc=None, bcc=None):
        """
        Send async an outgoing email with the given parameters.

        :param sender: From whom the email is being sent
        :param to: A list of recipient email addresses
        :param subject: The subject of the email
        :param text: The text of the email
        :param text_type: Mime subtype of text, defaults to 'plain' (can be 'html')
        :param cc: A list of Cc email addresses
        :param bcc: A list of Bcc email addresses
        :return:
        """
        if bcc is None:
            bcc = []
        if cc is None:
            cc = []
        if sender is None:
            sender = self.user

        msg = MIMEMultipart()
        msg.preamble = subject
        msg.add_header('charset', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to if isinstance(to, str) else ', '.join(to)
        if cc:
            msg['Cc'] = cc if isinstance(cc, str) else ', '.join(cc)
        if bcc:
            msg['Bcc'] = bcc if isinstance(bcc, str) else ', '.join(bcc)

        msg.attach(MIMEText(text, text_type, 'utf-8'))

        async with aiosmtplib.SMTP(hostname=self.host, port=self.port, use_tls=self.use_TLS) as client:
            await client.login(self.user, self.password)
            await client.send_message(msg, sender=sender)
