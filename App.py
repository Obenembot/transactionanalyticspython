import warnings

import pandas as pandas  # Required for data manipulation
import streamlit as streamlit  # Streamlit for web app
from prophet import Prophet  # For time series forecasting first by facebook to determine patters

warnings.filterwarnings("ignore")

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
    predictCustomerData = pandas.read_excel(file_path)

    # Ensure datetime is correct
    predictCustomerData['TransactionDate'] = pandas.to_datetime(predictCustomerData['TransactionDate'])

    # Sort data properly by customer and transaction date
    predictCustomerData = predictCustomerData.sort_values(by=['HpId', 'TransactionDate'])

    # Calculate time differences between transactions per customer
    predictCustomerData['NextPurchaseGap'] = predictCustomerData.groupby('HpId')['TransactionDate'].diff().shift(-1)

    # Compute average gap per customer
    avg_gaps = predictCustomerData.groupby('HpId')['NextPurchaseGap'].mean()

    # Get latest transaction date per customer
    latest_dates = predictCustomerData.groupby('HpId')['TransactionDate'].max()

    # Predict next transaction date
    pred_df = pandas.DataFrame({
        # 'HpId': avg_gaps.index,
        'Last Transaction Date': latest_dates.values,
        'Average Purchase Gap (Days)': avg_gaps.dt.days,
    })

    # Compute prediction
    pred_df['Predicted Next Purchase Date'] = pred_df['Last Transaction Date'] + pandas.to_timedelta(
        pred_df['Average Purchase Gap (Days)'], unit='D')

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


def customer_next_transaction():
    # Load Data
    file_path = "predictCustomer.xlsx"
    customer_data = pandas.read_excel(file_path)

    # ✅ Convert to datetime, drop invalids
    customer_data['TransactionDate'] = pandas.to_datetime(customer_data['TransactionDate'], errors='coerce')
    customer_data = customer_data.dropna(subset=['TransactionDate'])

    # ✅ Standardize columns for Prophet
    customer_data = customer_data.rename(columns={'TransactionDate': 'ds'})
    customer_data['y'] = 1  # Prophet requires a numeric target

    streamlit.title("📈 Customer Next 3 Transaction Predictions (Prophet ML)")
    streamlit.write("Forecasting next expected transaction dates using historical transactions")

    predictions = []
    skipped_customers = []

    # ✅ Loop through each unique customer
    for cust in customer_data['HpId'].unique():

        cust_df = customer_data[customer_data['HpId'] == cust].copy()
        cust_df = cust_df.dropna(subset=['ds'])

        # ✅ Prophet needs at least 2 unique historical dates
        if cust_df['ds'].nunique() < 2:
            skipped_customers.append(cust)
            continue

        # ✅ Fit Prophet model
        model = Prophet()
        model.fit(cust_df[['ds', 'y']])

        # ✅ Predict the next 120 days
        future = model.make_future_dataframe(periods=120)
        forecast = model.predict(future)

        # ✅ Consider only future dates (after last transaction)
        last_date = cust_df['ds'].max()
        future_forecast = forecast[forecast['ds'] > last_date]

        # ✅ Pick the top 3 highest forecast values
        top3 = future_forecast.nlargest(4, 'yhat')

        predictions.append({
            "HpId": cust,
            "Last Transaction Date": last_date.date(),
            "Prediction 1": top3.iloc[0]['ds'].date() if len(top3) > 0 else None,
            "Prediction 2": top3.iloc[1]['ds'].date() if len(top3) > 1 else None,
            "Prediction 3": top3.iloc[2]['ds'].date() if len(top3) > 2 else None,
            "Prediction 4": top3.iloc[3]['ds'].date() if len(top3) > 2 else None
        })

    # ✅ Display skipped customers
    if skipped_customers:
        streamlit.warning(f"⚠️ Skipped {len(skipped_customers)} customers with insufficient data: {skipped_customers}")

    # ✅ Create result DataFrame
    pred_df = pandas.DataFrame(predictions).sort_values("HpId")

    # ✅ Save output file
    output_path = "customer_prophet_top3_predictions.xlsx"
    pred_df.to_excel(output_path, index=False)

    # ✅ UI output
    streamlit.subheader("🔮 Top 3 Predicted Next Transactions per Customer")
    streamlit.dataframe(pred_df)

    streamlit.download_button(
        label="📥 Download Predictions Excel",
        data=open(output_path, "rb"),
        file_name="customer_prophet_top3_predictions.xlsx"
    )


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
    # display_next_transaction_prediction()
    customer_next_transaction()

streamlit.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)
