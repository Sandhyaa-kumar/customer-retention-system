import pandas as pd
from sqlalchemy import create_engine
import os
from config.database import _build_sqlalchemy_url, SSL_CA_PATH

# 1. Load your Excel file
# Put your excel file in the backend folder and change the name here
file_path = "customer_churn_dataset.csv" 
df = pd.read_csv(file_path)

# 2. Connect to TiDB
engine = create_engine(
    _build_sqlalchemy_url(),
    connect_args={"ssl_ca": SSL_CA_PATH}
)

# 3. Upload to the 'customers' table
try:
    df.to_sql('customers', con=engine, if_exists='append', index=False)
    print("✅ Data uploaded successfully to TiDB Cloud!")
except Exception as e:
    print(f"❌ Error: {e}")