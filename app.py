import streamlit as st
import pandas as pd
from scipy.stats import zscore

def calculate_anomalies(data):
    # Identify the consumption columns
    consumption_columns = [col for col in data.columns if "CONSUMPTION" in col]
    customer_data_long = data.melt(id_vars=['CIS ACCOUNT', 'NAME'], value_vars=consumption_columns, var_name='Month', value_name='Consumption')

    # Convert 'Month' to datetime format and then to the desired string format
    customer_data_long['Month'] = pd.to_datetime(customer_data_long['Month'].str.replace('CONSUMPTION ', ''), format='%b %y')
    customer_data_long['Month'] = customer_data_long['Month'].dt.strftime('%B %Y')  # Format month and year only

    # Calculate Z-scores within each customer group
    customer_data_long['Z-Score'] = customer_data_long.groupby('CIS ACCOUNT')['Consumption'].transform(lambda x: zscore(x, nan_policy='omit'))

    # Define an anomaly based on Z-score threshold
    customer_data_long['Anomaly'] = customer_data_long['Z-Score'].abs() > 3

    # Filter to obtain rows where anomalies are found
    anomalies = customer_data_long[customer_data_long['Anomaly']]
    return anomalies
logo_url = 'https://vokallond.com/wp-content/uploads/2024/04/logo.png'
st.image(logo_url, width=550)

# Streamlit interface
st.title('Customer Electricity Consumption Anomaly Detection Platform')

# Add a link to download sample data
st.markdown("""
You can download a [sample CSV file](https://vokallond.com/wp-content/uploads/2024/08/consumption-data.csv) to test the app.
""")

uploaded_file = st.file_uploader("Choose a CSV file with consumption data", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    if st.button('Detect Anomalies'):
        anomalies = calculate_anomalies(data)
        st.write('Detected Anomalies:')
        st.dataframe(anomalies)
        # Optional: Provide an option to download the results
        st.download_button(label="Download Anomalies as CSV", data=anomalies.to_csv(index=False), file_name='anomalies.csv', mime='text/csv')
