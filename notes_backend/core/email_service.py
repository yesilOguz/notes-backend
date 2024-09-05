import os

import smtplib
import email
from email.utils import make_msgid

from notes_backend.core import DELETE_ACCOUNT_OTP_URL
from notes_backend.user.otp_types import OTP_TYPES

smtpPort = 587


class EmailService:
    @staticmethod
    def send_email(to_mail: str, content: str, subject: str):
        email_address = os.getenv('EMAIL')
        email_password = os.getenv('EMAIL_PASS')

        msg = email.message_from_string(content)
        msg['From'] = email_address
        msg['To'] = to_mail
        msg['Subject'] = subject

        msg['Message-ID'] = make_msgid()

        smtp = smtplib.SMTP('mt-cressi.guzelhosting.com', smtpPort)

        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email_address, email_password)
            smtp.sendmail(email_address, to_mail, msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def generate_otp_content(otp_code: str, otp_code_type: OTP_TYPES):
        if otp_code_type == OTP_TYPES.PASSWORD_RESET.value:
            return f'Your password reset code is > {otp_code} < unless you did this, please ignore this email!'
        if otp_code_type == OTP_TYPES.REMOVE_ACC.value:
            link = f'{DELETE_ACCOUNT_OTP_URL}/{otp_code}'
            return f'If you are sure you want to delete your account, you can complete the process by clicking the link. > {link} <'

        return f'Your code is > {otp_code} <'
