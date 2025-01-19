from flask import Flask, request
import pandas as pd
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def get_erp_data():
    """Function to get data from ERP System"""
    try:
        file_path = 'MockERPTestData.json'
        with open(file_path, 'r') as file:
            data = pd.read_json(file)
        return data
    except Exception as e:
        print(f"Error reading ERP data: {e}")
        return None

def check_due_dates(data):
    """Function to check payment due dates and filter reminders"""
    try:
        data['due_date'] = pd.to_datetime(data['due_date'], format='%m/%d/%Y')
        today = pd.Timestamp(datetime.date.today())
        data['days_until_payment'] = (data['due_date'] - today).dt.days
        reminders = data[data['days_until_payment'].isin([1, 3, 7])]
        return reminders
    except Exception as e:
        print(f"Error processing due dates: {e}")
        return None

def send_reminders(data):
    """Function to send reminders via email"""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        sender_email = "sample.erp123@gmail.com"
        sender_password = "hloj drqo soxs oile"

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)

        email_templates = {
            1: "Dear {first_name} {last_name},\n\nYour payment of ${amount} is due tomorrow ({due_date}). Please ensure payment is made promptly.\n\nThank you.",
            3: "Dear {first_name} {last_name},\n\nYour payment of ${amount} is due in 3 days ({due_date}). Please make arrangements to pay before the due date.\n\nThank you.",
            7: "Dear {first_name} {last_name},\n\nYour payment of ${amount} is due in a week ({due_date}). Kindly make the payment soon.\n\nThank you."
        }

        for _, row in data.iterrows():
            recipient_email = row['email']
            category = row['days_until_payment']
            body = email_templates.get(category, "").format(
                first_name=row['first_name'],
                last_name=row['last_name'],
                amount=row['due_amount'],
                due_date=row['due_date'].strftime('%m/%d/%Y')
            )

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = f"Payment Reminder - {category} day(s) left"
            message.attach(MIMEText(body, 'plain'))
            

            server.sendmail(sender_email, recipient_email, message.as_string())

        server.quit()
        print("Reminders sent successfully!")
    except Exception as e:
        print(f"Error sending reminders: {e}")

def main():
    print("Fetching ERP data...")
    data = get_erp_data()
    if data is None or data.empty:
        print("No data available to process.")
        return

    print("Processing due dates...")
    reminders = check_due_dates(data)
    if reminders is None or reminders.empty:
        print("No reminders to send.")
        return

    print("Sending reminders...")
    send_reminders(reminders)

if __name__ == '__main__':
    main()
