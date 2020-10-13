import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger('csss_site')


class Gmail:

    def __int__(self, from_email, password, smtp='smtp.gmail.com', port=587, max_number_of_retries=5):
        """
        initialized the gmail object for a gmail account

        Keyword Argument
        from_email -- the email address to log into
        password -- the password for the email to log into
        smtp -- the server that hosts the smptlib server for gmail
        port -- the port for the smptlib server for gmail
        max_number_of_retries -- the maximum number of times to try opening and closing the connection to the smptlib
         server as well as sending the email
        """
        self.connection_successful = False
        number_of_retries = 0
        self.from_email = from_email
        self.max_number_of_retries = max_number_of_retries
        while not self.connection_successful and number_of_retries < max_number_of_retries:
            try:
                self.server = smtplib.SMTP(f'{smtp}:{port}')
                logger.info(f"[Gmail __init__()] setup smptlib server connection to {smtp}:{port}")
                self.server.connect(f'{smtp}:{port}')
                logger.info("[Gmail __init__()] smptlib server connected")
                self.server.ehlo()
                logger.info("[Gmail __init__()] smptlib server ehlo() successful")
                self.server.starttls()
                logger.info("[Gmail __init__()] smptlib server ttls started")
                logger.info(f"[Gmail __init__()] Logging into account {from_email}")
                self.server.login(from_email, password)
                logger.info(f"[Gmail __init__()] login to email {from_email} successful")
                self.connection_successful = True
            except Exception as e:
                number_of_retries += 1
                logger.error(f"[Gmail __init__()] experienced following error when initializing.\n{e}")
                self.error_message = f"{e}"

    def send_email(self, subject, body, to_email, to_name, from_name="SFU CSSS"):
        """
        send email to the specified email address

        Keyword Argument
        subject -- the subject for the email to send
        body - -the body of the email to send
        to_email -- the email address to send the email to
        to_name -- the name of the person to send the email to
        from_name -- the name to assign to the from name field

        Return
        Bool -- true or false to indicate if email was sent successfully
        error_message -- None if success, otherwise, returns the error experienced
        """
        if self.connection_successful:
            number_of_retries = 0
            while number_of_retries < self.max_number_of_retries:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = from_name + " <" + self.from_email + ">"
                    msg['To'] = to_name + " <" + to_email + ">"
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body))
                    logger.info(f"[Gmail send_email()] sending email to {to_email}")
                    self.server.send_message(from_addr=self.from_email, to_addrs=to_email, msg=msg)
                    return True, None
                except Exception as e:
                    logger.info(f"[Gmail send_email()] unable to send email to {to_email} due to error.\n{e}")
                    number_of_retries += 1
                    self.error_message = f"{e}"
        return False, self.error_message

    def close_connection(self):
        """
        Closes connection to smptlib server

        Return
        Bool -- true or false to indicate if email was sent successfully
        error_message -- None if success, otherwise, returns the error experienced
        """
        if self.connection_successful:
            number_of_retries = 0
            while number_of_retries < self.max_number_of_retries:
                try:
                    logger.info("[Gmail close_connection()] closing connection to smtplib server")
                    self.server.close()
                    logger.info("[Gmail close_connection()] connection to smtplib server closed")
                    return True, None
                except Exception as e:
                    logger.error(
                        "[Gmail close_connection()] experienced following error when attempting "
                        f"to close connection to smtplib server.\n{e}"
                    )
                    number_of_retries += 1
                    self.error_message = f"{e}"
        return False, self.error_message
