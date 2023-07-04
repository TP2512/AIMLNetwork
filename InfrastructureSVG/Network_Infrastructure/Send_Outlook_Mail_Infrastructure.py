import logging
import smtplib


""" 
In this py file have 1 class
    - SendOutlookMailClass
"""


class SendOutlookMailClass:
    """ This class ("SendOutlookMailClass") responsible for send emails from outlook account """

    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def send_outlook_mail(self, server_name, username, password, sender, receives, subject, text):
        """
        This function responsible to check for send emails from outlook account

        The function get 7 parameter:
            - "server_name" - the server name for connection (string type)
            - "username" - the username for connection (string type)
            - "password" - the password for connection (string type)
            - "sender" - the sender name for connection (string type)
            - "receives" - the receives name for connection (list type)
            - "subject" - the subject for connection (string type)
            - "text" - the text for connection (string type)

        The function return 0 parameters
        """

        try:
            # Prepare actual message
            message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

%s
            """ % (sender, ", ".join(receives), subject, text)

            # Send the mail
            server = smtplib.SMTP(server_name)
            if username and password:
                server.login(username, password)
            #
            server.sendmail(sender, receives, message)
            # server.sendmail(FROM, TO, message)
            server.quit()
        except Exception:
            self.logger.exception('')
            return
