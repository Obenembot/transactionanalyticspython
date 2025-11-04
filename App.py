import pandas as pandas  # Required for data manipulation
import streamlit as streamlit  # Streamlit for web app
import matplotlib.pyplot as plt
import seaborn as sns

# Load data from file
file_path = "predictCustomer.xlsx"
df = pandas.read_excel(file_path)

# Convert Transaction Date to datetime
df["TransactionDate"] = pandas.to_datetime(df["TransactionDate"])

#  Set the sidebar for navigation
streamlit.sidebar.title("Navigation")
page = streamlit.sidebar.radio("Go to", ["Overview", "Transaction Analytics", "Customer Next Transaction"])


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


def display_next_transaction_prediction():

    # Load data
    file_path = "predictCustomer.xlsx"
    df = pandas.read_excel(file_path)

    # Ensure datetime is correct
    df['TransactionDate'] = pandas.to_datetime(df['TransactionDate'])

    # Sort data properly by customer and transaction date
    df = df.sort_values(by=['HpId', 'TransactionDate'])

    # Calculate time differences between transactions per customer
    df['NextPurchaseGap'] = df.groupby('HpId')['TransactionDate'].diff().shift(-1)

    # Compute average gap per customer
    avg_gaps = df.groupby('HpId')['NextPurchaseGap'].mean()

    # Get latest transaction date per customer
    latest_dates = df.groupby('HpId')['TransactionDate'].max()

    # Predict next transaction date
    pred_df = pandas.DataFrame({
        'HpId': avg_gaps.index,
        'Last Transaction Date': latest_dates.values,
        'Average Purchase Gap (Days)': avg_gaps.dt.days,
    })

    # Compute prediction
    pred_df['Predicted Next Purchase Date'] = pred_df['Last Transaction Date'] + pandas.to_timedelta(pred_df['Average Purchase Gap (Days)'], unit='D')

    # Save predictions to Excel
    output_path = "customer_next_transaction_prediction.xlsx"
    pred_df.to_excel(output_path, index=False)

    # Streamlit UI
    streamlit.title("Customer Next Transaction Predictions")

    streamlit.success("✅ Predictions generated successfully!")

    streamlit.write("📁 Download prediction file:")
    streamlit.download_button(
        label="📥 Download Excel",
        data=open(output_path, "rb"),
        file_name="customer_next_transaction_prediction.xlsx"
    )

    streamlit.dataframe(pred_df)


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

elif page == "Customer Next Transaction":
    streamlit.title("Customer Next Transaction Dashboard")
    #     Predict when next the customer will make a transaction
    streamlit.write("This section will predict when the customer will make their next transaction.")
    streamlit.write("Feature under development.")
    display_next_transaction_prediction()

streamlit.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)
