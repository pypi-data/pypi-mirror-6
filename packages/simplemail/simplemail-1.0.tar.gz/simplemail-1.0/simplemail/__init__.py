#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os import popen
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class NoSender(Exception):
    def __str__(self):
        return "No sender specified"


class NoRecipient(Exception):
    def __str__(self):
        return "No recipient specified"


class NoSendmail(Exception):
    def __str__(self):
        return "No sendmail path specified"


class NoSubject(Exception):
    def __str__(self):
        return "No subject specified"


class NoBody(Exception):
    def __str__(self):
        return "No body specified"


class SendmailError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "error %s" % self.value


class Simplemail(object):
    """ This object sets up the email sending procedure. Subject and the message body are both
    encoded in utf-8 for non-ascii charsets.

    The following arguments are required to set the default procedure:

    sender -- contains the string with the sender information in the
    "Sender Name <email@domain.tld> format.
    recipient -- contains a list with the recipients addresses like
    ["user1@domain.tld", "user2@domain.tld"].
    subject -- contains a string with the email subject like "Subject".
    body -- countains an actual plain-text body.

    The following arguments are optional:

    sendmail -- contains a string with the sendmail path. The default value is "/usr/sbin/sendmail"
    cc -- contains a list with the cc-recipients addresses. Format is the same as recipient.
    bcc -- contains a list with the bcc-recipients addresses. Format is the same as recipient.
    html -- contains an optional html body.
    """

    def __init__(self, sendmail="/usr/sbin/sendmail", **kwargs):
        self.defaults = {}
        if sendmail:
            self.defaults["sendmail"] = sendmail
        self.defaults.update(kwargs)

    def send(self, **kwargs):
        """ This method actually sends the email. But it allows you to override all the default
        values from the object constructor.

        For example:
                   Simplemail.send(sender="John Doe <jdoe@domain.tld>")
        It will use all the values from the initial object definition, but it will override the
        sender value.
        """
        settings = self.defaults.copy()
        settings.update(kwargs)
        if not "sendmail" in settings.keys():
            raise NoSendmail
        if not "sender" in settings.keys():
            raise NoSender
        if not "recipient" in settings.keys():
            raise NoRecipient
        if not "subject" in settings.keys():
            raise NoSubject
        if not "body" in settings.keys():
            raise NoBody
        sm = popen("%s -t" % settings["sendmail"], "w")
        msg = MIMEMultipart("alternative")
        msg["From"] = settings["sender"]
        msg["To"] = ", ".join(settings["recipient"])
        msg["Subject"] = settings["subject"]
        msg["Content-Type"] = "text/plain; charset=UTF-8; format=flowed"
        msg["Content-Transfer-Encoding"] = "8bit"
        if "cc" in settings.keys():
            msg["Cc"] = ", ".join(settings["cc"])
        if "bcc" in settings.keys():
            msg["Bcc"] = ", ".join(settings["bcc"])
        msg.attach(MIMEText(settings["body"], "plain"))
        if "html" in settings.keys():
            msg.attach(MIMEText(settings["html"], "html"))
        sm.write("%s\n" % msg.as_string())
        status = sm.close()
        if status:
            raise SendmailError(status)
