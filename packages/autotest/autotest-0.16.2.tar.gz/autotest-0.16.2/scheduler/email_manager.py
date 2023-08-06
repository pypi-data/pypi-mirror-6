import traceback
import socket
import os
import time
import smtplib
import re
import getpass
import logging
try:
    import autotest.common as common
except ImportError:
    import common
from autotest.client.shared.settings import settings

CONFIG_SECTION = 'SCHEDULER'

CONFIG_SECTION_SMTP = 'SERVER'


class EmailNotificationManager(object):

    def __init__(self):
        self._emails = []

        self._from_address = settings.get_value(CONFIG_SECTION,
                                                "notify_email_from",
                                                default=getpass.getuser())

        self._notify_address = settings.get_value(CONFIG_SECTION,
                                                  "notify_email", default='')

        self._smtp_server = settings.get_value(CONFIG_SECTION_SMTP,
                                               "smtp_server",
                                               default='localhost')

        self._smtp_port = settings.get_value(CONFIG_SECTION_SMTP,
                                             "smtp_port",
                                             default=None)

        self._smtp_user = settings.get_value(CONFIG_SECTION_SMTP,
                                             "smtp_user", default='')

        self._smtp_password = settings.get_value(CONFIG_SECTION_SMTP,
                                                 "smtp_password", default='')

    def send_email(self, to_string, subject, body):
        """Mails out emails to the addresses listed in to_string.

        to_string is split into a list which can be delimited by any of:
            ';', ',', ':' or any whitespace
        """
        # Create list from string removing empty strings from the list.
        to_list = [x for x in re.split('\s|,|;|:', to_string) if x]
        if not to_list:
            return

        msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (
            self._from_address, ', '.join(to_list), subject, body)
        try:
            mailer = smtplib.SMTP(self._smtp_server, self._smtp_port)
            try:
                if self._smtp_user:
                    mailer.login(self._smtp_user, self._smtp_password)
                mailer.sendmail(self._from_address, to_list, msg)
            finally:
                try:
                    mailer.quit()
                except:
                    logging.exception('mailer.quit() failed:')
        except Exception:
            logging.exception('Sending email failed:')

    def enqueue_notify_email(self, subject, message):
        logging.error(subject + '\n' + message)
        if not self._notify_address:
            return

        body = 'Subject: ' + subject + '\n'
        body += "%s / %s / %s\n%s" % (socket.gethostname(),
                                      os.getpid(),
                                      time.strftime("%X %x"), message)
        self._emails.append(body)

    def send_queued_emails(self):
        if not self._emails:
            return
        subject = 'Scheduler notifications from ' + socket.gethostname()
        separator = '\n' + '-' * 40 + '\n'
        body = separator.join(self._emails)

        self.send_email(self._notify_address, subject, body)
        self._emails = []

    def log_stacktrace(self, reason):
        logging.exception(reason)
        message = "EXCEPTION: %s\n%s" % (reason, traceback.format_exc())
        self.enqueue_notify_email("monitor_db exception", message)


manager = EmailNotificationManager()
