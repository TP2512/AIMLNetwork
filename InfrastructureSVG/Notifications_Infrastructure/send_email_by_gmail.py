import logging
import smtplib


class Notifications:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')
    
    def send_email_by_gmail(self, to, subject, message_body):
        gmail_sender = 'airspanautomation1@gmail.com'
        gmail_passwd = 'cupldxzzgcsxbjox'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)

        email_body = '\r\n'.join(
            [
                f'To: {to}',
                f'From: {gmail_sender}',
                f'Subject: {subject}',
                '',
                message_body,
            ]
        )

        try:
            server.sendmail(gmail_sender, to, email_body)
        except Exception:
            self.logger.exception('error sending mail')

        server.quit()


if __name__ == '__main__':
    notifications = Notifications()
    _to = 'RBlumberg@airspan.com'
    _subject = 'Test Subject'
    _message_body = 'Test Body'
    notifications.send_email_by_gmail(_to, _subject, _message_body)
