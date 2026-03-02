from flask_mail import Message
from flask import url_for, current_app
from main import mail


def send_activation_mail(account):
    try:
        activation_link = url_for(
            "auth.activate_account",
            token=account.activation_token,
            _external=True
        )

        msg = Message(
            subject="Account aktivieren – Lerngruppen Tool",
            recipients=[account.email],
            body=f"""
Hallo {account.first_name},

bitte aktiviere deinen Account über folgenden Link:

{activation_link}

Falls du dich nicht registriert hast, ignoriere diese Nachricht.
"""
        )

        mail.send(msg)

    except Exception as e:
        # Optional: Logging statt print
        print("Mailversand fehlgeschlagen:", e)
