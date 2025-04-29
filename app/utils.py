import os
from flask import current_app
from werkzeug.utils import secure_filename
from weasyprint import HTML
from flask_mail import Message
from . import mail

def save_uploaded_file(file_storage, folder):
    filename = secure_filename(file_storage.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_storage.save(path)
    return os.path.relpath(path, current_app.root_path)

def generate_pdf_from_html(html_content, pdf_path):
    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path

def send_email(subject, recipients, body, attachments=None, cc=None):
    msg = Message(subject, recipients=recipients, cc=cc, body=body)
    attachments = attachments or []
    for att in attachments:
        with open(att, 'rb') as f:
            msg.attach(os.path.basename(att), 'application/pdf', f.read())
    mail.send(msg)
