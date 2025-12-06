from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os


def generate_test_eml():
    filename = "test_report.xlsx"
    with open(filename, "wb") as f:
        f.write(b"Fake Excel Content")

    msg = MIMEMultipart()
    msg['From'] = "sender@example.com"
    msg['To'] = "recipient@example.com"
    msg['Subject'] = "Test Email with Attachment"

    msg.attach(MIMEText("This is the body.", 'plain'))

    with open(filename, "rb") as f:
        part = MIMEApplication(f.read(), Name=filename)

    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)

    output_filename = "debug_test.eml"
    with open(output_filename, "w") as f:
        f.write(msg.as_string())

    print(f"Generated {output_filename}")
    os.remove(filename)


if __name__ == "__main__":
    generate_test_eml()
