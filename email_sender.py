import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

def send_email(recipient, subject, body, smtp_server, smtp_port, smtp_username, smtp_password):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = recipient
    msg['Subject'] = subject

    # Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the graphs
    graph_directory = 'graphs'
    for graph_file in os.listdir(graph_directory):
        if graph_file.endswith('.png'):
            with open(os.path.join(graph_directory, graph_file), 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename=graph_file)
                msg.attach(img)

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient, msg.as_string())
