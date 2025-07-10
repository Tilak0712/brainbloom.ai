import hashlib, secrets, smtplib, ssl
from datetime import datetime
from email.message import EmailMessage
from firebase_config import db

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_otp_email(receiver_email, otp):
    EMAIL_ADDRESS = "91a793001@smtp-brevo.com"
    EMAIL_PASSWORD = "xsmtpsib-79bd8c8a4255988c2c24f85697077298e0aac5761bd3962adc25c4f014d0cd25-swX1EJhYrbndQMOt"
    DISPLAY_EMAIL = "tilaklakhani7@gmail.com"

    msg = EmailMessage()
    msg["Subject"] = "Your BrainBloom.AI OTP Code"
    msg["From"] = f"BrainBloom.AI <{DISPLAY_EMAIL}>"
    msg["To"] = receiver_email
    msg.set_content(f"Your OTP is: {otp}\n\nThis code is valid for a few minutes.\n\nThanks,\nBrainBloom.AI")

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp-relay.brevo.com", 587) as smtp:
        smtp.starttls(context=context)
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def signup_user(username, password, recovery_word, email, role="user"):
    ref = db.reference(f"users/{username}")
    if ref.get() is not None:
        return False
    ref.set({
        "password": hash_password(password),
        "role": role,
        "recovery": recovery_word,
        "email": email,
        "created_at": datetime.now().isoformat()
    })
    return True

def login_user(username, password):
    ref = db.reference(f"users/{username}").get()
    if ref and ref["password"] == hash_password(password):
        return True, ref["role"], ref["email"]
    return False, None, None

def reset_password(username, recovery_word, new_password):
    ref = db.reference(f"users/{username}").get()
    if ref and ref["recovery"] == recovery_word:
        db.reference(f"users/{username}/password").set(hash_password(new_password))
        return True
    return False

def generate_otp():
    return str(secrets.randbelow(10000)).zfill(4)
