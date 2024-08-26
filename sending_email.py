import csv
import os
import smtplib
import sqlite3
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendEmail:
    def __init__(self):
        connection = sqlite3.connect('instance/todo.db')
        cursor = connection.cursor()

        cursor.execute("SELECT todolist FROM Todolist")
        rows = cursor.fetchall()

        with open('output.csv', 'w', newline='') as file:
            writer = csv.writer(file)

            column_names = [description[0] for description in cursor.description]
            writer.writerow(column_names)

            writer.writerows(rows)

        connection.close()

        MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
        MAIL_APP_PW = os.environ.get("PASSWORD_KEY")

        sender_email = MAIL_ADDRESS
        receiver_email = MAIL_ADDRESS
        password = MAIL_APP_PW

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = 'output.csv'

        body = 'Please download your To do list the attached CSV file.'
        msg.attach(MIMEText(body, 'plain'))

        filename = 'output.csv'
        attachment = open(filename, 'rb')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')

        msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", port=587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
