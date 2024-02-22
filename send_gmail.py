import smtplib
from email.message import EmailMessage
from config import smtp_sender, smtp_sender_password

def send_email_to_user(title:str, message:str, to_email:str) -> str:
    sender = smtp_sender
    password = smtp_sender_password

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = title 
    msg['From'] = sender 
    msg['To'] = to_email

    try:
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return "200 OK"
    except Exception as error:
        return f"Error: {error}"
print(send_email_to_user('Geeks', 'SMTP TEST', 'ktoktorov144@gmail.com'))