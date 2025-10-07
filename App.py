import pandas as pandas # Required for data manipulation
import openpyxl as openpyxl # Required for Excel file handling
import streamlit as streamlit # Streamlit for web app

# Load data from file
file_path = "predictCustomer.xlsx"
df = pandas.read_excel(file_path)

# Convert Transaction Date to datetime
df["TransactionDate"] = pandas.to_datetime(df["TransactionDate"])

print(openpyxl)
#  Set the sidebar for navigation
streamlit.sidebar.title("Navigation")
page = streamlit.sidebar.radio("Go to", ["Overview", "Transaction Analytics"])


if page == "Overview":
    streamlit.title("Overview Dashboard")
    streamlit.dataframe(df, height=600)
streamlit.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)
