import openpyxl as openpyxl  # Required for Excel file handling
import pandas as pandas  # Required for data manipulation
import streamlit as streamlit  # Streamlit for web app

# Load data from file
file_path = "predictCustomer.xlsx"
df = pandas.read_excel(file_path)

# Convert Transaction Date to datetime
df["TransactionDate"] = pandas.to_datetime(df["TransactionDate"])

print(openpyxl)
#  Set the sidebar for navigation
streamlit.sidebar.title("Navigation")
page = streamlit.sidebar.radio("Go to", ["Overview", "Transaction Analytics"])


def display_beneficiary_transactions():
    streamlit.write("Transaction distribution by Beneficiary Id")
    transaction_counts = df["BeneficiaryId"].value_counts().sort_values(ascending=False)
    streamlit.bar_chart(transaction_counts)

def display_hp_id_transactions():
    streamlit.write("Transaction distribution by HpId Id")
    transaction_counts = df["HpId"].value_counts().sort_values(ascending=False)
    streamlit.bar_chart(transaction_counts)

def display_hp_id_transactions_by_Date():
    streamlit.write("Transaction distribution by Transaction Date")
    transaction_counts = df["TransactionDate"].value_counts().sort_values(ascending=False)
    streamlit.bar_chart(transaction_counts)

if page == "Overview":
    streamlit.title("Overview Dashboard")
    streamlit.dataframe(df, height=600)
elif page == "Transaction Analytics":
    streamlit.title("Transaction Analytics Dashboard")
    # show a summary of user with the most transactions
    least_user = df["HpId"].value_counts().idxmin()
    least_user_count = df["HpId"].value_counts().min()

    top_user = df["HpId"].value_counts().idxmax()
    top_user_count = df["HpId"].value_counts().max()

    streamlit.write(f"User with most transactions: {top_user} ({top_user_count} transactions)")
    streamlit.write(f"User with least transactions: {least_user} ({least_user_count} transactions)")

    least_user = df["BeneficiaryId"].value_counts().idxmin()
    least_user_count = df["BeneficiaryId"].value_counts().min()
    streamlit.write(f"BeneficiaryId with least transactions: {least_user} ({least_user_count} transactions)")

    least_user = df["BeneficiaryId"].value_counts().idxmax()
    least_user_count = df["BeneficiaryId"].value_counts().max()
    streamlit.write(f"BeneficiaryId with most transactions: {least_user} ({least_user_count} transactions)")

# Transaction distribution by Beneficiary Id
    display_beneficiary_transactions()
    # Transaction distribution by HpID
    display_hp_id_transactions()
    # Transaction distribution by Transaction Date
    display_hp_id_transactions_by_Date()





streamlit.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)
