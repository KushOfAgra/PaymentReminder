import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load data from the JSON file
def load_data():
    file_path = 'MockERPTestData.json'  # Path to the uploaded JSON file
    data = pd.read_json(file_path)
    data['due_date'] = pd.to_datetime(data['due_date'], format='%m/%d/%Y')
    data['due_amount'] = data['due_amount'].astype(str).str.replace('$', '').astype(float)
    data['days_until_due'] = (data['due_date'] - datetime.now()).dt.days
    return data

def filter_data(data, days_filter):
    return data[data['days_until_due'] <= days_filter]

def filter_exact_days(data, days_filter):
    return data[data['days_until_due'] == days_filter]

def search_by_id(data, search_id):
    return data[data['id'] == search_id]

def search_by_name(data, search_name):
    return data[data['first_name'].str.contains(search_name, case=False, na=False) | data['last_name'].str.contains(search_name, case=False, na=False)]

# Streamlit app
st.title("Payment Reminder Dashboard")

# Load the data
data = load_data()

# Sidebar filters
st.sidebar.header("Filter Options")
selected_days = st.sidebar.number_input(
    "Enter the number of days left",
    min_value=0,
    value=7,
    step=1
)

# Checkbox for showing exact reminders
show_exact_reminders = st.sidebar.checkbox("Show specific Reminder for these days")

# Search options
st.sidebar.header("Search Options")
search_id = st.sidebar.text_input("Search by ID")
search_name = st.sidebar.text_input("Search by Name")

# Apply filters
if show_exact_reminders:
    filtered_data = filter_exact_days(data, selected_days)
else:
    filtered_data = filter_data(data, selected_days)

if search_id:
    filtered_data = search_by_id(filtered_data, int(search_id))

if search_name:
    filtered_data = search_by_name(filtered_data, search_name)

# Display filtered data
st.header("Upcoming Payment Reminders")

if not filtered_data.empty:
    st.dataframe(
        filtered_data[['id', 'first_name', 'last_name', 'email', 'due_date', 'due_amount', 'days_until_due']]
        .rename(columns={
            'id': 'ID',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'due_date': 'Due Date',
            'due_amount': 'Due Amount',
            'days_until_due': 'Days Until Due'
        })
    )
else:
    st.write("No reminders match the selected filters.")

# Summary statistics
st.sidebar.header("Summary Statistics")
if not data.empty:
    total_due = filtered_data['due_amount'].sum()
    st.sidebar.metric("Total Amount Due", f"${round(total_due, 2)}")
    reminders_count = len(filtered_data)
    st.sidebar.metric("Reminders Count", reminders_count)

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Developed by Kushagra Gupta")
