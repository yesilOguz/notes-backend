import os

import smtplib
import email

from ganesha.user.otp_types import OTP_TYPES

smtpPort = 587


class EmailService:
    @staticmethod
    def send_email(to_mail: str, content: str):
        email_address = os.getenv('EMAIL')
        email_password = os.getenv('EMAIL_PASS')

        msg = email.message_from_string(content)
        msg['From'] = email_address
        msg['To'] = to_mail
        msg['Subject'] = content

        smtp = smtplib.SMTP('smtp-mail.outlook.com', smtpPort)

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
        if otp_code_type == OTP_TYPES.PASSWORD_RESET:
            return f'Your password reset code is > {otp_code} < unless you did this, please ignore this email!'

        return f'Your code is > {otp_code} <'
