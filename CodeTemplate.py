#This is the basic template followed for this project, the code is the other file on the repo, named FinalCode
from flask import Flask, request
import pandas as pd


app = Flask(_name_)


def get_erp_data():
    '''Function to get data from ERP System'''
    
    # we will get all the erp data from an api call 
    # using sample data for display purposes
    with 'filePath' as file:
        all_content_json = file.read()
    
    
    
    pass


def check_due_dates():
    '''Function to check the payment due dates'''
    pass


def send_reminders():
    '''Function to remind users as per the deadline via mail'''


def main():
    pass


if _name=='main_':
    app.run('0.0.0.0', port=9000, debug=True)
