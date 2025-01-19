from flask import Flask, request
import pandas as pd
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def get_erp_data():
    '''Function to get data from ERP System'''
    try:
        # File path for test data
        file_path = 'MockERPTestData.json'
        
        # Reading JSON content from the file
        with open(file_path, 'r') as file:
            all_content_json = file.read()
        
        # Converting JSON content to a DataFrame
        data = pd.read_json(all_content_json)
        return data

    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def check_due_dates(data):
    '''Function to check the payment due dates and categorize reminders'''
    try:
        today = datetime.date.today()
        
        # Convert 'Due Payment Date' to datetime and calculate days until due
        data['Due Payment Date'] = pd.to_datetime(data['Due Payment Date']).dt.date
        data['Days Until Due'] = (data['Due Payment Date'] - today).apply(lambda x: x.days)
        
        # Categorize based on days until due
        def categorize_due_days(days):
            if days == 1:
                return '1 day left'
            elif 2 <= days <= 5:
                return '5 days left'
            elif 6 <= days <= 7:
                return '7 days left'
            elif days < 0:
                return 'Overdue'
            else:
                return 'No reminder'
        
        data['Reminder Category'] = data['Days Until Due'].apply(categorize_due_days)
        return data
    except Exception as e:
        print(f"An error occurred while checking due dates: {e}")
        return data

def send_reminders(data):
    '''Function to send reminders as per categorized deadlines'''
    try:
        # SMTP server setup (update with real credentials)
        smtp_server = "smtp.example.com"
        smtp_port = 587
        sender_email = "sender@example.com"
        sender_password = "password"
        
        # Filter data to include only those requiring reminders
        reminder_data = data[data['Reminder Category'] != 'No reminder']
        
        if reminder_data.empty:
            print("No reminders to send.")
            return
        
        # Setting up the SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Email templates
        email_templates = {
            '1 day left': "Dear {first_name} {last_name},\n\nYour payment of ${amount} is due tomorrow ({due_date}). Please ensure payment is made promptly.\n\nThank you.",
            '5 days left': "Dear {first_name} {last_name},\n\nThis is a reminder that your payment of ${amount} is due in 5 days ({due_date}). Kindly make the payment soon.\n\nThank you.",
            '7 days left': "Dear {first_name} {last_name},\n\nYour payment of ${amount} is due in a week ({due_date}). Please make arrangements to pay before the due date.\n\nThank you.",
            'Overdue': "Dear {first_name} {last_name},\n\nYour payment of ${amount} was due on {due_date}. Kindly make the payment immediately to avoid penalties.\n\nThank you."
        }
        
        # Sending reminders
        for _, row in reminder_data.iterrows():
            recipient_email = row['Email']
            category = row['Reminder Category']
            
            # Populate email content dynamically from DataFrame
            body = email_templates[category].format(
                first_name=row['First Name'],
                last_name=row['Last Name'],
                amount=row['Payment Amount'],
                due_date=row['Due Payment Date']
            )
            
            # Create and send the email
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = f"Payment Reminder - {category}"
            message.attach(MIMEText(body, 'plain'))
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        server.quit()
        print("Reminders sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending reminders: {e}")

def main():
    # Step 1: Get data from the ERP system
    data = get_erp_data()
    
    if data.empty:
        print("No data to process. Exiting.")
        return
    
    # Step 2: Check due dates
    data = check_due_dates(data)
    
    # Step 3: Send reminders
    send_reminders(data)

if __name__ == '__main__':
    app.run('0.0.0.0', port=9000, debug=True)
