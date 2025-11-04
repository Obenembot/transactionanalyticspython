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
page = streamlit.sidebar.radio("Go to", ["Overview", "Transaction Analytics", "Customer Next Transaction", "Days Prediction"])


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

    # Convert TransactionDate to datetime, drop invalids
    customer_data['TransactionDate'] = pandas.to_datetime(customer_data['TransactionDate'], errors='coerce')
    customer_data = customer_data.dropna(subset=['TransactionDate'])

    streamlit.title("📈 Customer Next 3 Transaction Predictions (Prophet ML)")
    streamlit.write("Forecasting next expected transaction dates using transaction gaps")

    predictions = []
    skipped_customers = []

    for cust in customer_data['HpId'].unique():
        cust_df = customer_data[customer_data['HpId'] == cust].sort_values('TransactionDate').copy()
        cust_df = cust_df.dropna(subset=['TransactionDate'])

        if len(cust_df) < 2:
            skipped_customers.append(cust)
            continue

        # Calculate gaps between transactions
        cust_df['delta_days'] = cust_df['TransactionDate'].diff().dt.days
        cust_df = cust_df.dropna(subset=['delta_days'])

        if len(cust_df) < 2:
            skipped_customers.append(cust)
            continue

        # Prepare data for Prophet
        prophet_df = cust_df[['TransactionDate', 'delta_days']].rename(columns={'TransactionDate':'ds', 'delta_days':'y'})

        model = Prophet()
        model.fit(prophet_df)

        # Forecast next 3 transaction gaps
        future = model.make_future_dataframe(periods=3)
        forecast = model.predict(future)

        # Take the last 3 predicted gaps and add to last transaction date
        last_date = cust_df['TransactionDate'].max()
        next_gaps = forecast['yhat'][-3:].values
        next_dates = [last_date + pandas.Timedelta(days=int(gap)) for gap in next_gaps]

        predictions.append({
            "HpId": cust,
            "Last Transaction Date": last_date.date(),
            "Prediction 1": next_dates[0].date() if len(next_dates) > 0 else None,
            "Prediction 2": next_dates[1].date() if len(next_dates) > 1 else None,
            "Prediction 3": next_dates[2].date() if len(next_dates) > 2 else None
        })

    if skipped_customers:
        streamlit.warning(f"⚠️ Skipped {len(skipped_customers)} customers with insufficient data: {skipped_customers}")

    pred_df = pandas.DataFrame(predictions).sort_values("Last Transaction Date", ascending=False)

    output_path = "customer_prophet_top3_predictions.xlsx"
    pred_df.to_excel(output_path, index=False)

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
elif page == "Days Prediction":
    streamlit.title("Days Prediction Dashboard")
    streamlit.write("This section will predict the number of days until the customer's next transaction.")
    streamlit.write("Feature under development.")
    display_next_transaction_prediction()

streamlit.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)
