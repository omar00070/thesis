
import smtplib
import mimetypes
from email.message import EmailMessage

class Email:
    def __init__(self, sender, receiver, password):
        self.sender = sender
        self.receiver = receiver
        self.password = password

    def send_mail(self, mail_content, subject, attachments=None):
        message = EmailMessage()
        message['From'] = self.sender
        message['To'] = self.receiver
        message['Subject'] = subject  
        message.set_content(mail_content)

        if attachments:
            attachment_file = attachments
            mime_type, _ = mimetypes.guess_type(attachment_file)
            mime_type, mime_subtype = mime_type.split('/')
            with open(attachment_file, 'rb') as file:
                message.add_attachment(file.read(),
                maintype=mime_type,
                subtype=mime_subtype,
                filename=attachment_file)

        # send the email
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(self.sender, self.password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(self.sender, self.receiver, text)
        session.quit()
        print('Mail Sent')


#The mail addresses and password

# email = Email(sender_address, receiver_address, sender_pass)
# email.send_mail('something', 'some subject')