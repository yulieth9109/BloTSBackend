from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from website import app, mail
import mimetypes


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_email(to, subject, template, attachment = None):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )

    if attachment !=  None :
        file = open(attachment,'rb')
        print(mimetypes.guess_type(attachment)[0])
        msg.attach(filename = file.name, 
                        content_type = mimetypes.guess_type(attachment)[0],
                        data = file.read())
    mail.send(msg)

